import json
import re
from pathlib import Path
from typing import Optional

import numpy as np
import faiss
from google.genai import types
from retriever.models import ConversationState

JOB_LEVEL_MAPPING = {
    "graduate": ["graduate", "entry-level", "general population"],
    "entry": ["entry-level", "graduate", "general population"],
    "junior": ["entry-level", "graduate", "general population"],
    "mid": ["mid-professional", "professional individual contributor", "general population"],
    "professional": ["mid-professional", "professional individual contributor", "general population"],
    "senior": ["mid-professional", "professional individual contributor", "manager", "front line manager", "general population"],
    "manager": ["manager", "front line manager", "supervisor", "general population"],
    "director": ["director", "executive", "general population"],
    "executive": ["executive", "director", "general population"]
}

class SHLRetriever:
    def __init__(self, project_root: Path, client):
        self.project_root = project_root
        self.client = client
        
        # Load processed documents
        processed_catalog_path = project_root / "data" / "processed" / "processed_catalog.json"
        if not processed_catalog_path.exists():
            raise FileNotFoundError(f"Processed catalog file not found at {processed_catalog_path}")
        with open(processed_catalog_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
            
        # Load FAISS index
        index_path = project_root / "data" / "processed" / "index.faiss"
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index file not found at {index_path}")
        self.index = faiss.read_index(str(index_path))
        
        if len(self.documents) != self.index.ntotal:
            raise ValueError(
                f"Mismatch between documents length ({len(self.documents)}) and FAISS index size ({self.index.ntotal})"
            )

    def _get_query_embedding(self, query_text: str) -> np.ndarray:
        """Call Gemini to generate a 768-dimensional normalized embedding vector."""
        response = self.client.models.embed_content(
            model="gemini-embedding-2",
            contents=query_text,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        vector = np.array(response.embeddings[0].values, dtype=np.float32)
        # L2-normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

    def semantic_search(self, state: ConversationState, k: int = 50) -> list[tuple[dict, float]]:
        """Perform semantic search against FAISS index using query constructed from ConversationState."""
        # Construct search query from role, skills and job description
        query_parts = []
        if state.role:
            query_parts.append(f"Role: {state.role}")
        if state.skills:
            query_parts.append(f"Skills: {', '.join(state.skills)}")
        if state.job_description:
            query_parts.append(f"Job Description: {state.job_description}")
            
        if not query_parts:
            # Fallback in case of empty states
            query_parts.append(state.user_message)
            
        query_text = " ".join(query_parts)
        
        # Get vector embedding
        query_vector = self._get_query_embedding(query_text)
        query_vector_2d = np.array([query_vector], dtype=np.float32)
        
        # Search index
        scores, indices = self.index.search(query_vector_2d, k=min(k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                results.append((self.documents[idx], float(score)))
        return results

    def _parse_duration_minutes(self, duration_str: str) -> Optional[int]:
        """Parse numerical minutes from a duration string (e.g. '30 minutes' -> 30)."""
        if not duration_str or duration_str == "-":
            return None
        match = re.search(r'(\d+)\s*(?:min|minute)', duration_str.lower())
        if match:
            return int(match.group(1))
        return None

    def filter_candidates(self, candidates: list[tuple[dict, float]], state: ConversationState) -> list[tuple[dict, float]]:
        """Apply strict metadata constraint filtering on top of semantic retrieval candidates."""
        filtered = []
        
        # Constraints from state
        constraints = state.constraints or {}
        req_remote = constraints.get("remote")
        req_adaptive = constraints.get("adaptive")
        req_languages = constraints.get("languages", [])
        req_duration_str = constraints.get("duration")
        req_job_level = state.job_level
        
        # Parse max duration limit if present in user request
        max_duration_limit = None
        if req_duration_str:
            max_duration_limit = self._parse_duration_minutes(req_duration_str)
            # Fallback: if no text match, look for any standalone digits
            if max_duration_limit is None:
                digit_match = re.search(r'(\d+)', req_duration_str)
                if digit_match:
                    max_duration_limit = int(digit_match.group(1))

        for doc, score in candidates:
            meta = doc.get("metadata", {})
            
            # 1. Job Level Filter (job levels should be in both semantic and metadata filtering)
            if req_job_level:
                doc_job_levels = [jl.lower() for jl in meta.get("job_levels", [])]
                req_jl_lower = req_job_level.lower()
                
                # Expand search target using mapping
                mapped_targets = [req_jl_lower]
                for key, vals in JOB_LEVEL_MAPPING.items():
                    if key in req_jl_lower:
                        mapped_targets.extend(vals)
                
                matched_job_level = False
                for target in mapped_targets:
                    for djl in doc_job_levels:
                        if target in djl or djl in target:
                            matched_job_level = True
                            break
                    if matched_job_level:
                        break
                        
                if not matched_job_level:
                    continue

            
            # 2. Remote Filter
            if req_remote is True:
                if not meta.get("remote"):
                    continue
                    
            # 3. Adaptive Filter
            if req_adaptive is True:
                if not meta.get("adaptive"):
                    continue
                    
            # 4. Languages Filter
            if req_languages:
                doc_languages = [l.lower() for l in meta.get("languages", [])]
                language_match = True
                for lang in req_languages:
                    if lang.lower() not in doc_languages:
                        language_match = False
                        break
                if not language_match:
                    continue
                    
            # 5. Duration Filter
            if max_duration_limit is not None:
                doc_duration_mins = self._parse_duration_minutes(meta.get("duration", ""))
                if doc_duration_mins is None or doc_duration_mins > max_duration_limit:
                    # Filter out if it has no duration or exceeds limit
                    continue

            filtered.append((doc, score))
            
        return filtered

    def retrieve(self, state: ConversationState, top_n: int = 5) -> list[dict]:
        """End-to-end pipeline: search FAISS index and filter down to top_n results."""
        # 1. Retrieve candidates
        candidates = self.semantic_search(state, k=100)
        
        # 2. Apply metadata filters
        filtered_candidates = self.filter_candidates(candidates, state)
        
        # 3. Format and return top_n matching products
        results = []
        for doc, score in filtered_candidates[:top_n]:
            page_content = doc.get("page_content", "")
            name = "Unknown Product"
            if page_content.startswith("Name:"):
                name = page_content.split("\n")[0].replace("Name:", "").strip()
                
            results.append({
                "entity_id": doc["metadata"].get("entity_id"),
                "name": name,
                "description": doc.get("page_content", ""),
                "score": score,
                "metadata": doc.get("metadata", {})
            })
            
        return results

import json
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
import numpy as np
from google.genai import types


# Ensure we can import modules from project root
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

def load_processed_documents(path: Path) -> list[dict]:
    """Load the processed documents from the JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"Processed catalog file not found at {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def get_single_embedding(text: str, client) -> list[float]:
    """Generate embedding for a single text using gemini-embedding-2 with backoff retry."""
    max_retries = 5
    backoff_factor = 2
    initial_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            response = client.models.embed_content(
                model="gemini-embedding-2",
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
            if not response.embeddings:
                raise ValueError("Embedding list is empty in API response")
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise e
            delay = initial_delay * (backoff_factor ** attempt)
            time.sleep(delay)

def get_embeddings_batch(texts: list[str], client) -> list[list[float]]:
    """Generate embeddings for a list of texts sequentially with a small delay to avoid rate limit spikes."""
    if not texts:
        return []
        
    results = []
    for text in texts:
        results.append(get_single_embedding(text, client))
        time.sleep(0.5)
        
    return results




def save_embeddings(embeddings: np.ndarray, path: Path):
    """Save processed embeddings to a numpy binary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, embeddings)

def build_embeddings(documents: list[dict], client, batch_size: int = 20) -> np.ndarray:
    """Batch retrieve embeddings for all documents and construct/save the NumPy matrix incrementally."""
    project_root = Path(__file__).parent.parent
    embeddings_path = project_root / "data" / "processed" / "embeddings.npy"
    
    # Load existing embeddings if they exist
    if embeddings_path.exists():
        try:
            embeddings = np.load(embeddings_path)
            print(f"Loaded existing embeddings matrix of shape {embeddings.shape} from {embeddings_path}")
        except Exception as e:
            print(f"Error loading existing embeddings, starting fresh: {e}")
            embeddings = np.empty((0, 768), dtype=np.float32)
    else:
        embeddings = np.empty((0, 768), dtype=np.float32)
        
    num_embedded = len(embeddings)
    if num_embedded >= len(documents):
        print(f"All {len(documents)} documents are already embedded. Skipping generation.")
        return embeddings
        
    print(f"Resuming embedding from index {num_embedded}...")
    
    # Process remaining documents in batches
    for i in range(num_embedded, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        texts = [doc["page_content"] for doc in batch_docs]
        
        print(f"Embedding batch [{i} to {min(i + batch_size, len(documents))} of {len(documents)}]...")
        batch_vectors = get_embeddings_batch(texts, client)
        
        # Convert to numpy array
        batch_array = np.array(batch_vectors, dtype=np.float32)
        
        # Append to matrix
        if len(embeddings) == 0:
            embeddings = batch_array
        else:
            embeddings = np.vstack([embeddings, batch_array])
            
        # Save progress immediately
        save_embeddings(embeddings, embeddings_path)
        print(f"Progress saved. Current matrix shape: {embeddings.shape}")
        
        # Rate limit throttling delay
        if i + batch_size < len(documents):
            time.sleep(3.0)
            
    return embeddings

if __name__ == "__main__":
    from google import genai
    
    project_root = Path(__file__).parent.parent
    catalog_path = project_root / "data" / "processed" / "processed_catalog.json"
    embeddings_path = project_root / "data" / "processed" / "embeddings.npy"
    
    # Initialize SDK client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment. Initializing default client.")
        client = genai.Client()
    else:
        client = genai.Client(api_key=api_key)
        
    print("Loading processed documents...")
    docs = load_processed_documents(catalog_path)
    print(f"Loaded {len(docs)} documents.")
    
    print("Building embeddings...")
    embeddings = build_embeddings(docs, client)
    print(f"Finished building embeddings. Matrix shape: {embeddings.shape}")

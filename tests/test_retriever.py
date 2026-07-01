import unittest
import os
import sys
from pathlib import Path
from retriever.models import ConversationState
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from retriever.retriever import SHLRetriever

class MockEmbeddingResponse:
    def __init__(self):
        class MockEmbedding:
            def __init__(self):
                self.values = [0.1] * 768
        self.embeddings = [MockEmbedding()]

class MockClient:
    def __init__(self):
        class Models:
            def embed_content(self, *args, **kwargs):
                return MockEmbeddingResponse()
        self.models = Models()

class TestRetriever(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.mock_client = MockClient()
        # Initialize retriever (this will load real catalog and real index)
        self.retriever = SHLRetriever(self.project_root, self.mock_client)

    def test_parse_duration_minutes(self):
        self.assertEqual(self.retriever._parse_duration_minutes("30 minutes"), 30)
        self.assertEqual(self.retriever._parse_duration_minutes("45 min"), 45)
        self.assertEqual(self.retriever._parse_duration_minutes("120 Minutes"), 120)
        self.assertIsNone(self.retriever._parse_duration_minutes("-"))
        self.assertIsNone(self.retriever._parse_duration_minutes(""))

    def test_metadata_filtering_remote_and_adaptive(self):
        # Create full list of candidates (the whole catalog)
        candidates = [(doc, 0.8) for doc in self.retriever.documents]
        
        # Test Remote filter
        state_remote = ConversationState(
            user_message="remote only",
            conversation_history=[],
            intent="recommend",
            confidence=0.9,
            role="Software Engineer",
            job_level="Graduate",
            skills=[],
            constraints={"remote": True},
            job_description=None,
            previous_recommendations=[]
        )
        filtered = self.retriever.filter_candidates(candidates, state_remote)
        # All filtered elements should have remote=True in metadata
        for doc, _ in filtered:
            self.assertTrue(doc["metadata"].get("remote"))

        # Test Adaptive filter
        state_adaptive = ConversationState(
            user_message="adaptive only",
            conversation_history=[],
            intent="recommend",
            confidence=0.9,
            role="Software Engineer",
            job_level="Graduate",
            skills=[],
            constraints={"adaptive": True},
            job_description=None,
            previous_recommendations=[]
        )
        filtered = self.retriever.filter_candidates(candidates, state_adaptive)
        # All filtered elements should have adaptive=True
        for doc, _ in filtered:
            self.assertTrue(doc["metadata"].get("adaptive"))

    def test_metadata_filtering_languages(self):
        candidates = [(doc, 0.8) for doc in self.retriever.documents]
        state_lang = ConversationState(
            user_message="in French",
            conversation_history=[],
            intent="recommend",
            confidence=0.9,
            role="Software Engineer",
            job_level="Graduate",
            skills=[],
            constraints={"languages": ["French"]},
            job_description=None,
            previous_recommendations=[]
        )
        filtered = self.retriever.filter_candidates(candidates, state_lang)
        for doc, _ in filtered:
            langs = [l.lower() for l in doc["metadata"].get("languages", [])]
            self.assertIn("french", langs)

    def test_metadata_filtering_job_levels(self):
        candidates = [(doc, 0.8) for doc in self.retriever.documents]
        state_level = ConversationState(
            user_message="senior level",
            conversation_history=[],
            intent="recommend",
            confidence=0.9,
            role="Software Engineer",
            job_level="Senior",
            skills=[],
            constraints={},
            job_description=None,
            previous_recommendations=[]
        )
        filtered = self.retriever.filter_candidates(candidates, state_level)
        mapped_targets = ["senior", "mid-professional", "professional individual contributor", "manager", "front line manager", "general population"]
        for doc, _ in filtered:
            doc_levels = [l.lower() for l in doc["metadata"].get("job_levels", [])]
            matched = False
            for dl in doc_levels:
                for target in mapped_targets:
                    if target in dl or dl in target:
                        matched = True
                        break
                if matched:
                    break
            self.assertTrue(matched)


    def test_metadata_filtering_duration(self):
        candidates = [(doc, 0.8) for doc in self.retriever.documents]
        
        # Limit to 30 mins
        state_duration = ConversationState(
            user_message="max 30 mins",
            conversation_history=[],
            intent="recommend",
            confidence=0.9,
            role="Software Engineer",
            job_level="Graduate",
            skills=[],
            constraints={"duration": "30 minutes"},
            job_description=None,
            previous_recommendations=[]
        )
        filtered = self.retriever.filter_candidates(candidates, state_duration)
        for doc, _ in filtered:
            doc_dur = doc["metadata"].get("duration")
            doc_mins = self.retriever._parse_duration_minutes(doc_dur)
            self.assertIsNotNone(doc_mins)
            self.assertLessEqual(doc_mins, 30)

    def test_live_semantic_search_and_retrieval(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.skipTest("GEMINI_API_KEY not found in environment. Skipping live retriever test.")
            
        from google import genai
        client = genai.Client(api_key=api_key)
        
        real_retriever = SHLRetriever(self.project_root, client)
        
        # Test retrieving coding tests for a Python developer
        state = ConversationState(
            user_message="Looking for coding tests for senior python dev",
            conversation_history=[],
            intent="recommend",
            confidence=0.95,
            role="Python Developer",
            job_level="Senior",
            skills=["Python", "Algorithms"],
            constraints={},
            job_description=None,
            previous_recommendations=[]
        )
        
        results = real_retriever.retrieve(state, top_n=5)
        self.assertGreater(len(results), 0)
        
        # Check if Python, Coding, or developer-related terms appear in results
        first_product_name = results[0]["name"].lower()
        first_product_desc = results[0]["description"].lower()
        
        # Print for manual review
        print(f"Top live result for Python Developer: {results[0]['name']} (Score: {results[0]['score']})")
        print(f"Job Levels of result: {results[0]['metadata'].get('job_levels')}")

if __name__ == "__main__":
    unittest.main()

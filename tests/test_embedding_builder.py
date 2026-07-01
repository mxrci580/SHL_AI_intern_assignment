import unittest
import sys
import os
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.build_embeddings import (
    load_processed_documents,
    get_embeddings_batch,
    save_embeddings,
    build_embeddings
)

class MockEmbedResponse:
    def __init__(self, texts):
        class MockEmbedding:
            def __init__(self):
                self.values = [0.1] * 768
        self.embeddings = [MockEmbedding() for _ in texts]

class MockClient:
    def __init__(self):
        class Models:
            def embed_content(self, model, contents, config=None, **kwargs):
                texts = [contents] if isinstance(contents, str) else contents
                return MockEmbedResponse(texts)
        self.models = Models()


class TestEmbeddingBuilder(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.test_output_dir = self.project_root / "data" / "processed"
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_path = self.test_output_dir / "embeddings.npy"

    def test_load_documents(self):
        catalog_path = self.test_output_dir / "processed_catalog.json"
        if catalog_path.exists():
            docs = load_processed_documents(catalog_path)
            self.assertEqual(len(docs), 377)
            self.assertIn("page_content", docs[0])

    def test_save_embeddings(self):
        dummy_matrix = np.random.rand(5, 768).astype(np.float32)
        temp_path = self.test_output_dir / "temp_test_embeddings.npy"
        
        save_embeddings(dummy_matrix, temp_path)
        self.assertTrue(temp_path.exists())
        
        loaded = np.load(temp_path)
        np.testing.assert_array_almost_equal(loaded, dummy_matrix)
        
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()

    def test_build_embeddings_mock(self):
        # Create dummy documents
        dummy_docs = [
            {"page_content": "Doc 1", "metadata": {}},
            {"page_content": "Doc 2", "metadata": {}},
            {"page_content": "Doc 3", "metadata": {}}
        ]
        
        # Remove any existing embeddings.npy to start fresh
        temp_embeddings_path = self.test_output_dir / "embeddings.npy"
        backup_matrix = None
        if temp_embeddings_path.exists():
            backup_matrix = np.load(temp_embeddings_path)
            temp_embeddings_path.unlink()
            
        mock_client = MockClient()
        
        try:
            # Build embeddings with batch_size=2
            embeddings = build_embeddings(dummy_docs, mock_client, batch_size=2)
            self.assertEqual(embeddings.shape, (3, 768))
            self.assertTrue(temp_embeddings_path.exists())
            
            # Test resume capability: add a 4th document
            dummy_docs.append({"page_content": "Doc 4", "metadata": {}})
            embeddings_resume = build_embeddings(dummy_docs, mock_client, batch_size=2)
            self.assertEqual(embeddings_resume.shape, (4, 768))
            
        finally:
            # Cleanup temp files and restore original if backed up
            if temp_embeddings_path.exists():
                temp_embeddings_path.unlink()
            if backup_matrix is not None:
                np.save(temp_embeddings_path, backup_matrix)

    def test_live_get_embeddings_batch(self):
        # Only run if API key is present in environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.skipTest("GEMINI_API_KEY not found in environment. Skipping live API test.")
            
        from google import genai
        client = genai.Client(api_key=api_key)
        
        texts = ["Hello world", "SHL Recommender System"]
        vectors = get_embeddings_batch(texts, client)
        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), 768)
        self.assertEqual(len(vectors[1]), 768)

if __name__ == "__main__":
    unittest.main()

import unittest
import sys
from pathlib import Path
import numpy as np
import faiss

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.build_faiss import (
    load_embeddings,
    normalize_vectors,
    build_index,
    save_index
)

class TestFAISSBuilder(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.test_output_dir = self.project_root / "data" / "processed"
        self.embeddings_path = self.test_output_dir / "embeddings.npy"
        self.index_path = self.test_output_dir / "index.faiss"

    def test_load_embeddings(self):
        if self.embeddings_path.exists():
            embeddings = load_embeddings(self.embeddings_path)
            self.assertEqual(embeddings.shape, (377, 768))
            self.assertEqual(embeddings.dtype, np.float32)

    def test_normalize_vectors(self):
        vectors = np.random.rand(10, 768).astype(np.float32) * 10
        normalized = normalize_vectors(vectors)
        
        # Verify L2 norm of each row is 1.0
        norms = np.linalg.norm(normalized, axis=1)
        np.testing.assert_array_almost_equal(norms, np.ones(10, dtype=np.float32), decimal=5)

    def test_build_and_save_index(self):
        dummy_embeddings = np.random.rand(5, 768).astype(np.float32)
        index = build_index(dummy_embeddings)
        self.assertEqual(index.ntotal, 5)
        
        # Test save and load
        temp_index_path = self.test_output_dir / "temp_index.faiss"
        save_index(index, temp_index_path)
        self.assertTrue(temp_index_path.exists())
        
        loaded_index = faiss.read_index(str(temp_index_path))
        self.assertEqual(loaded_index.ntotal, 5)
        
        # Cleanup
        if temp_index_path.exists():
            temp_index_path.unlink()

    def test_search_similarity(self):
        # We index 3 orthogonal unit vectors
        embeddings = np.array([
            [1.0] + [0.0]*767,  # Vector 0: X-axis
            [0.0, 1.0] + [0.0]*766,  # Vector 1: Y-axis
            [0.0, 0.0, 1.0] + [0.0]*765   # Vector 2: Z-axis
        ], dtype=np.float32)
        
        index = build_index(embeddings)
        
        # Query close to Vector 1 (Y-axis)
        query = np.array([[0.1, 0.9, 0.0] + [0.0]*765], dtype=np.float32)
        query = normalize_vectors(query)
        
        # Search top 2 neighbors
        D, I = index.search(query, k=2)
        
        # Nearest neighbor should be Vector 1
        self.assertEqual(I[0][0], 1)
        # Cosine similarity score should be high (closer to 1.0)
        self.assertGreater(D[0][0], 0.9)
        # Second nearest should be Vector 0 or 2
        self.assertIn(I[0][1], [0, 2])

if __name__ == "__main__":
    unittest.main()

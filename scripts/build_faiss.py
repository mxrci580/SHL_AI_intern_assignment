import sys
from pathlib import Path
import numpy as np
import faiss

# Ensure we can import modules from project root
sys.path.append(str(Path(__file__).parent.parent))

def load_embeddings(path: Path) -> np.ndarray:
    """Load the embeddings array from a .npy file."""
    if not path.exists():
        raise FileNotFoundError(f"Embeddings file not found at {path}")
    return np.load(path).astype(np.float32)

def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize rows of a 2D numpy array to enable Cosine Similarity search with Inner Product."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    # Prevent division by zero
    norms = np.where(norms == 0, 1.0, norms)
    return vectors / norms

def build_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """Construct a flat inner product index and add the normalized embeddings to it."""
    if len(embeddings.shape) != 2:
        raise ValueError("Embeddings matrix must be 2D")
    dimension = embeddings.shape[1]
    
    # Flat Inner Product index
    index = faiss.IndexFlatIP(dimension)
    
    # Normalize vectors before adding for cosine similarity
    normalized_embeddings = normalize_vectors(embeddings)
    index.add(normalized_embeddings)
    
    return index

def save_index(index: faiss.IndexFlatIP, path: Path):
    """Save the constructed FAISS index to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(path))

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    embeddings_path = project_root / "data" / "processed" / "embeddings.npy"
    index_path = project_root / "data" / "processed" / "index.faiss"
    
    print("Loading embeddings...")
    embeddings = load_embeddings(embeddings_path)
    print(f"Loaded embedding matrix of shape {embeddings.shape}.")
    
    print("Building FAISS index...")
    index = build_index(embeddings)
    print(f"Index built. Total vectors in index: {index.ntotal}")
    
    print("Saving FAISS index...")
    save_index(index, index_path)
    print("FAISS index saved successfully.")

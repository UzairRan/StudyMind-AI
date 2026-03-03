"""
Lightweight Embeddings Module - Using fastembed (ONNX Runtime)
This uses 1/3 of the memory compared to sentence-transformers
Perfect for Streamlit Cloud deployment (512MB memory limit)
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from fastembed import TextEmbedding
import faiss

class EmbeddingManagerLight:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initialize with fastembed (much lighter than sentence-transformers)
        
        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name
        self.model = TextEmbedding(model_name=model_name)
        
        # Get dimension by encoding a test text
        test_embedding = list(self.model.embed(["test"]))[0]
        self.dimension = len(test_embedding)
        
        self.index = None
        self.texts = []
        self.metadatas = []
    
    def create_embeddings(self, texts: List[str], metadatas: List[Dict] = None):
        """
        Create embeddings and build FAISS index
        
        Args:
            texts: List of text chunks
            metadatas: List of metadata dictionaries
        """
        if not texts:
            raise ValueError("No texts to embed")
        
        self.texts = texts
        self.metadatas = metadatas or [{}] * len(texts)
        
        # Generate embeddings in batches (memory efficient)
        all_embeddings = []
        batch_size = 32
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = list(self.model.embed(batch_texts))
            all_embeddings.extend(batch_embeddings)
        
        # Convert to numpy array
        embeddings_array = np.array([emb.tolist() for emb in all_embeddings]).astype('float32')
        
        # Build FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings_array)
        
        return embeddings_array
    
    def search(self, query: str, k: int = 5):
        """
        Search for similar texts
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            Tuple of (texts, metadatas) for top k results
        """
        if self.index is None:
            return [], []
        
        # Generate query embedding
        query_embedding = list(self.model.embed([query]))[0]
        query_array = np.array([query_embedding.tolist()]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_array, min(k, len(self.texts)))
        
        results_texts = [self.texts[i] for i in indices[0]]
        results_metadatas = [self.metadatas[i] for i in indices[0]]
        
        return results_texts, results_metadatas
    
    def save_index(self, path: str):
        """
        Save FAISS index and metadata to disk
        
        Args:
            path: Base path for saving (without extension)
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        faiss.write_index(self.index, f"{path}.faiss")
        
        with open(f"{path}.pkl", 'wb') as f:
            pickle.dump({
                'texts': self.texts,
                'metadatas': self.metadatas,
                'dimension': self.dimension,
                'model_name': self.model_name
            }, f)
    
    def load_index(self, path: str):
        """
        Load FAISS index and metadata from disk
        
        Args:
            path: Base path of saved index
        """
        if not os.path.exists(f"{path}.faiss") or not os.path.exists(f"{path}.pkl"):
            raise FileNotFoundError(f"Index not found at {path}")
        
        # Load FAISS index
        self.index = faiss.read_index(f"{path}.faiss")
        
        # Load metadata
        with open(f"{path}.pkl", 'rb') as f:
            data = pickle.load(f)
            self.texts = data['texts']
            self.metadatas = data['metadatas']
            self.dimension = data['dimension']
            self.model_name = data['model_name']
            
            # Reinitialize model
            self.model = TextEmbedding(model_name=self.model_name)
    
    def get_all_chunks(self):
        """
        Get all chunks and metadata
        
        Returns:
            Dictionary with texts and metadatas
        """
        return {
            'texts': self.texts,
            'metadatas': self.metadatas
        } 
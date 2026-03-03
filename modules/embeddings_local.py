"""
Lightweight Embeddings Module - Using fastembed (ONNX Runtime)
This uses 1/3 of the memory compared to sentence-transformers
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any
from fastembed import TextEmbedding
import faiss

class EmbeddingManager:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initialize with fastembed (much lighter than sentence-transformers)
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
        """Create embeddings and build FAISS index"""
        self.texts = texts
        self.metadatas = metadatas or [{}] * len(texts)
        
        # Generate embeddings (fastembed is memory efficient)
        embeddings = list(self.model.embed(texts))
        embeddings_array = np.array([emb.tolist() for emb in embeddings]).astype('float32')
        
        # Build FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings_array)
        
        return embeddings_array
    
    def search(self, query: str, k: int = 5):
        """Search for similar texts"""
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
        """Save FAISS index and metadata"""
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
        """Load FAISS index and metadata"""
        self.index = faiss.read_index(f"{path}.faiss")
        with open(f"{path}.pkl", 'rb') as f:
            data = pickle.load(f)
            self.texts = data['texts']
            self.metadatas = data['metadatas']
            self.dimension = data['dimension']
            self.model_name = data['model_name']
            self.model = TextEmbedding(model_name=self.model_name)
    
    def get_all_chunks(self):
        """Get all chunks and metadata"""
        return {
            'texts': self.texts,
            'metadatas': self.metadatas
        } 
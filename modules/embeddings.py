"""
Embeddings Module - Using sentence-transformers instead of fastembed
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with sentence-transformers
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        self.index = None
        self.texts = []
        self.metadatas = []
    
    def create_embeddings(self, texts: List[str], metadatas: List[Dict] = None):
        self.texts = texts
        self.metadatas = metadatas or [{}] * len(texts)
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Build FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings_array)
        
        return embeddings_array
    
    def search(self, query: str, k: int = 5):
        if self.index is None:
            return [], []
        
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        query_array = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_array, min(k, len(self.texts)))
        
        results_texts = [self.texts[i] for i in indices[0]]
        results_metadatas = [self.metadatas[i] for i in indices[0]]
        
        return results_texts, results_metadatas
    
    def save_index(self, path: str):
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
        self.index = faiss.read_index(f"{path}.faiss")
        with open(f"{path}.pkl", 'rb') as f:
            data = pickle.load(f)
            self.texts = data['texts']
            self.metadatas = data['metadatas']
            self.dimension = data['dimension']
            self.model_name = data['model_name']
            self.model = SentenceTransformer(self.model_name)
    
    def get_all_chunks(self):
        return {
            'texts': self.texts,
            'metadatas': self.metadatas
        } 
"""
Embeddings Module
Handles FastEmbed embeddings and FAISS vector store
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from fastembed import TextEmbedding
import faiss
from pathlib import Path

class EmbeddingManager:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initialize embedding model and FAISS index
        """
        self.model_name = model_name
        self.embedding_model = TextEmbedding(model_name=model_name)
        self.index = None
        self.texts = []
        self.metadatas = []
        self.dimension = 384  # Default for bge-small-en
        
    def create_embeddings(self, texts: List[str], metadatas: List[Dict] = None):
        """
        Create embeddings for texts and build FAISS index
        """
        self.texts = texts
        self.metadatas = metadatas or [{}] * len(texts)
        
        # Generate embeddings
        embeddings = list(self.embedding_model.embed(texts))
        embeddings_array = np.array([emb.tolist() for emb in embeddings]).astype('float32')
        
        # Build FAISS index
        self.dimension = embeddings_array.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings_array)
        
        return embeddings_array
    
    def search(self, query: str, k: int = 5) -> tuple:
        """
        Search for similar texts
        """
        if self.index is None:
            raise ValueError("No index available. Please create embeddings first.")
        
        # Generate query embedding
        query_embedding = list(self.embedding_model.embed([query]))[0]
        query_array = np.array([query_embedding.tolist()]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_array, k)
        
        # Get results
        results_texts = [self.texts[i] for i in indices[0]]
        results_metadatas = [self.metadatas[i] for i in indices[0]]
        
        return results_texts, results_metadatas
    
    def save_index(self, path: str):
        """
        Save FAISS index and metadata
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}.faiss")
        
        # Save metadata
        metadata = {
            'texts': self.texts,
            'metadatas': self.metadatas,
            'dimension': self.dimension,
            'model_name': self.model_name
        }
        
        with open(f"{path}.pkl", 'wb') as f:
            pickle.dump(metadata, f)
    
    def load_index(self, path: str):
        """
        Load FAISS index and metadata
        """
        # Load FAISS index
        self.index = faiss.read_index(f"{path}.faiss")
        
        # Load metadata
        with open(f"{path}.pkl", 'rb') as f:
            metadata = pickle.load(f)
        
        self.texts = metadata['texts']
        self.metadatas = metadata['metadatas']
        self.dimension = metadata['dimension']
        self.model_name = metadata['model_name']
    
    def get_all_chunks(self) -> Dict:
        """
        Get all chunks and their metadata
        """
        return {
            'texts': self.texts,
            'metadatas': self.metadatas
        } 
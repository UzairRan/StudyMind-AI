"""
Embeddings Module - Using sentence-transformers with memory-efficient models
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import faiss

class EmbeddingManager:
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize with sentence-transformers
        Uses all-MiniLM-L6-v2 for local, but can be overridden
        """
        # Detect if running on Streamlit Cloud
        IN_CLOUD = os.path.exists("/.dockerenv") or "STREAMLIT_SHARING" in os.environ
        
        # Use smaller model on cloud, full model locally
        if model_name:
            self.model_name = model_name
        elif IN_CLOUD:
            # Even smaller model for cloud (22MB instead of 90MB)
            self.model_name = "all-MiniLM-L12-v2"  # 22MB model
            # Alternative even smaller: "paraphrase-albert-small-v2" (15MB)
        else:
            self.model_name = "all-MiniLM-L6-v2"  # 90MB model for local
        
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        self.index = None
        self.texts = []
        self.metadatas = []
    
    def create_embeddings(self, texts: List[str], metadatas: List[Dict] = None):
        """Create embeddings and build FAISS index"""
        self.texts = texts
        self.metadatas = metadatas or [{}] * len(texts)
        
        # Generate embeddings in batches to save memory
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = self.model.encode(batch_texts, show_progress_bar=False)
            all_embeddings.append(batch_embeddings)
        
        embeddings = np.vstack(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Build FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings_array)
        
        return embeddings_array
    
    def search(self, query: str, k: int = 5):
        """Search for similar texts"""
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
            self.model = SentenceTransformer(self.model_name)
    
    def get_all_chunks(self):
        """Get all chunks and metadata"""
        return {
            'texts': self.texts,
            'metadatas': self.metadatas
        } 
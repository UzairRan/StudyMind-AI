"""
Retriever Module
Handles search and filtering logic
"""

from typing import List, Dict, Any, Optional

class Retriever:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
    
    def search(self, embedding_manager, query: str, chapter_filter: Optional[str] = None) -> tuple:
        """
        Search for relevant chunks with optional chapter filtering
        """
        # Get initial results
        chunks, metadatas = embedding_manager.search(query, k=self.top_k * 2)
        
        # Apply chapter filter if specified
        if chapter_filter and chapter_filter != "All Chapters":
            filtered_chunks = []
            filtered_metadatas = []
            
            for chunk, meta in zip(chunks, metadatas):
                if meta.get('chapter', '').lower() == chapter_filter.lower():
                    filtered_chunks.append(chunk)
                    filtered_metadatas.append(meta)
                    
                    if len(filtered_chunks) >= self.top_k:
                        break
            
            # If no results with filter, return empty
            if filtered_chunks:
                return filtered_chunks, filtered_metadatas
            else:
                return [], []
        
        # Return top_k results without filter
        return chunks[:self.top_k], metadatas[:self.top_k]
    
    def rerank_by_relevance(self, query: str, chunks: List[str], metadatas: List[Dict]) -> tuple:
        """
        Optional reranking based on keyword matching
        """
        # Simple keyword-based reranking
        query_words = set(query.lower().split())
        
        scored_items = []
        for chunk, meta in zip(chunks, metadatas):
            # Calculate relevance score
            chunk_words = set(chunk.lower().split())
            overlap = len(query_words.intersection(chunk_words))
            score = overlap / max(len(query_words), 1)
            
            scored_items.append((score, chunk, meta))
        
        # Sort by score descending
        scored_items.sort(reverse=True, key=lambda x: x[0])
        
        # Return sorted chunks and metadatas
        sorted_chunks = [item[1] for item in scored_items]
        sorted_metadatas = [item[2] for item in scored_items]
        
        return sorted_chunks, sorted_metadatas 
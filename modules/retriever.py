"""
Retriever Module
Handles search logic with metadata filtering
"""

from typing import List, Dict, Optional, Tuple

class Retriever:
    def __init__(self, top_k: int = 5):
        """
        Initialize retriever
        
        Args:
            top_k: Default number of results to return
        """
        self.top_k = top_k
    
    def search(self, embedding_manager, query: str, 
               chapter_filter: Optional[str] = None, 
               k: Optional[int] = None) -> Tuple[List[str], List[Dict]]:
        """
        Search with optional chapter filtering
        
        Args:
            embedding_manager: EmbeddingManager instance
            query: Search query
            chapter_filter: Chapter name to filter by (None for all)
            k: Number of results (uses self.top_k if None)
            
        Returns:
            Tuple of (chunks, metadatas)
        """
        k = k or self.top_k
        
        # Get initial results (request more for filtering)
        chunks, metadatas = embedding_manager.search(query, k=k * 3)
        
        # Apply chapter filter if specified
        if chapter_filter and chapter_filter != "All Chapters":
            filtered_chunks = []
            filtered_metadatas = []
            
            for chunk, meta in zip(chunks, metadatas):
                meta_chapter = meta.get('chapter', 'General').lower()
                if meta_chapter == chapter_filter.lower():
                    filtered_chunks.append(chunk)
                    filtered_metadatas.append(meta)
                    
                    if len(filtered_chunks) >= k:
                        break
            
            # If no results with filter, return empty
            if filtered_chunks:
                return filtered_chunks, filtered_metadatas
            else:
                return [], []
        
        # Return top k results without filter
        return chunks[:k], metadatas[:k]
    
    def hybrid_search(self, embedding_manager, query: str, 
                      chapter_filter: Optional[str] = None,
                      keyword_weight: float = 0.3) -> Tuple[List[str], List[Dict]]:
        """
        Hybrid search combining semantic and keyword matching
        
        Args:
            embedding_manager: EmbeddingManager instance
            query: Search query
            chapter_filter: Chapter filter
            keyword_weight: Weight for keyword matching (0-1)
            
        Returns:
            Tuple of (chunks, metadatas)
        """
        # Get semantic search results
        semantic_chunks, semantic_metadatas = self.search(
            embedding_manager, query, chapter_filter, k=self.top_k * 2
        )
        
        if not semantic_chunks:
            return [], []
        
        # Simple keyword reranking
        query_words = set(query.lower().split())
        
        # Score each chunk
        scored_items = []
        for chunk, meta in zip(semantic_chunks, semantic_metadatas):
            # Keyword matching score
            chunk_words = set(chunk.lower().split())
            keyword_score = len(query_words.intersection(chunk_words)) / max(len(query_words), 1)
            
            # Combined score (semantic is implicit in retrieval, keyword adds weight)
            combined_score = keyword_score
            
            scored_items.append((combined_score, chunk, meta))
        
        # Sort by score
        scored_items.sort(reverse=True, key=lambda x: x[0])
        
        # Return top k
        top_items = scored_items[:self.top_k]
        chunks = [item[1] for item in top_items]
        metadatas = [item[2] for item in top_items]
        
        return chunks, metadatas 
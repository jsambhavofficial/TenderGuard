import faiss
import numpy as np
import re
from typing import List, Dict, Any, Tuple
from app.nlp.embeddings import generate_embeddings, get_embedding_model

class TenderVectorStore:
    def __init__(self):
        self.indices: Dict[str, faiss.IndexFlatIP] = {}
        self.chunk_metadata: Dict[str, List[Dict[str, Any]]] = {}

    def index_document_chunks(self, doc_id: str, chunks: List[Dict[str, Any]]) -> None:
        """
        Builds a FAISS index for the given document's chunks.
        """
        if not chunks:
            return
            
        texts = [c["text_content"] for c in chunks]
        embeddings = generate_embeddings(texts)
        
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        
        self.indices[doc_id] = index
        self.chunk_metadata[doc_id] = chunks

    def search(self, doc_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval combining dense vector similarity with lexical keyword matching.
        Returns chunks sorted by combined relevance score.
        """
        if doc_id not in self.indices:
            return []
            
        query_vec = generate_embeddings([query])
        index = self.indices[doc_id]
        metadata = self.chunk_metadata[doc_id]
        
        # Dense search across all chunks
        total_chunks = len(metadata)
        dense_scores, dense_indices = index.search(query_vec, total_chunks)
        
        query_keywords = [w.lower() for w in re.findall(r'\b\w{3,}\b', query)]
        
        scored_results = []
        for score, idx in zip(dense_scores[0], dense_indices[0]):
            if idx != -1 and idx < total_chunks:
                chunk = metadata[idx]
                text_lower = chunk["text_content"].lower()
                
                # Lexical keyword boost
                match_count = sum(1 for kw in query_keywords if kw in text_lower)
                lexical_boost = (match_count / max(len(query_keywords), 1)) * 0.45 if query_keywords else 0.0
                
                combined_score = float(score) + lexical_boost
                chunk_copy = dict(chunk)
                chunk_copy["relevance_score"] = combined_score
                chunk_copy["dense_score"] = float(score)
                scored_results.append(chunk_copy)
                
        # Sort by combined hybrid score descending
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_results[:top_k]

# Global singleton store for the runtime session
vector_store = TenderVectorStore()

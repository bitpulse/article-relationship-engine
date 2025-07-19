# faiss_index.py
import faiss
import numpy as np
import pickle
from typing import List, Tuple, Dict, Any
import os

class FAISSIndexManager:
    """Manages FAISS index for efficient similarity search"""
    
    def __init__(self, dimension: int = 384, use_gpu: bool = False):
        """
        Initialize FAISS index manager
        
        Args:
            dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
            use_gpu: Whether to use GPU acceleration if available
        """
        self.dimension = dimension
        self.use_gpu = use_gpu and faiss.get_num_gpus() > 0
        
        # Create index - using Inner Product for normalized vectors (equivalent to cosine similarity)
        self.index = faiss.IndexFlatIP(dimension)
        
        # If GPU is available and requested, move index to GPU
        if self.use_gpu:
            self.index = faiss.index_cpu_to_gpu(
                faiss.StandardGpuResources(), 
                0,  # GPU id
                self.index
            )
            print("FAISS index moved to GPU")
        
        # Map from FAISS index position to article ID
        self.id_map = []
        
        # Store original embeddings for potential reuse
        self.embeddings = None
        
    def add_embeddings(self, embeddings: np.ndarray, article_ids: List[str]):
        """
        Add embeddings to the index
        
        Args:
            embeddings: Normalized embeddings array (n_articles x dimension)
            article_ids: List of article IDs corresponding to embeddings
        """
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embeddings dimension {embeddings.shape[1]} != expected {self.dimension}")
        
        # Ensure embeddings are normalized for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized_embeddings = embeddings / (norms + 1e-10)  # Add epsilon to avoid division by zero
        
        # Add to index
        self.index.add(normalized_embeddings.astype('float32'))
        
        # Update ID mapping
        self.id_map.extend(article_ids)
        
        # Store embeddings
        self.embeddings = normalized_embeddings
        
        print(f"Added {len(article_ids)} embeddings to index. Total: {self.index.ntotal}")
        
    def search(self, query_embedding: np.ndarray, k: int = 10, 
              similarity_threshold: float = None) -> List[Tuple[str, float]]:
        """
        Search for similar articles
        
        Args:
            query_embedding: Query embedding (1 x dimension)
            k: Number of results to return
            similarity_threshold: Optional minimum similarity score
            
        Returns:
            List of (article_id, similarity_score) tuples
        """
        # Ensure query is normalized
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm
        
        # Reshape for FAISS
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search
        k_search = min(k, self.index.ntotal)  # Don't search for more than we have
        scores, indices = self.index.search(query_embedding, k_search)
        
        # Convert to results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:  # FAISS returns -1 for no match
                continue
                
            if similarity_threshold is None or score >= similarity_threshold:
                article_id = self.id_map[idx]
                results.append((article_id, float(score)))
        
        return results
    
    def batch_search(self, query_embeddings: np.ndarray, k: int = 10) -> List[List[Tuple[str, float]]]:
        """
        Search for multiple queries at once
        
        Args:
            query_embeddings: Multiple query embeddings (n_queries x dimension)
            k: Number of results per query
            
        Returns:
            List of result lists, one per query
        """
        # Normalize queries
        norms = np.linalg.norm(query_embeddings, axis=1, keepdims=True)
        normalized_queries = query_embeddings / (norms + 1e-10)
        
        # Search
        k_search = min(k, self.index.ntotal)
        scores, indices = self.index.search(normalized_queries.astype('float32'), k_search)
        
        # Convert to results
        all_results = []
        for query_scores, query_indices in zip(scores, indices):
            results = []
            for score, idx in zip(query_scores, query_indices):
                if idx >= 0:
                    article_id = self.id_map[idx]
                    results.append((article_id, float(score)))
            all_results.append(results)
        
        return all_results
    
    def range_search(self, query_embedding: np.ndarray, 
                    radius: float = 0.7) -> List[Tuple[str, float]]:
        """
        Find all articles within a similarity radius
        
        Args:
            query_embedding: Query embedding
            radius: Similarity radius (0-1)
            
        Returns:
            List of (article_id, similarity_score) tuples
        """
        # For now, use regular search with high k and filter
        # (Full range search requires different index type)
        results = self.search(query_embedding, k=self.index.ntotal)
        return [(aid, score) for aid, score in results if score >= radius]
    
    def get_embedding(self, article_id: str) -> np.ndarray:
        """Get embedding for a specific article"""
        try:
            idx = self.id_map.index(article_id)
            return self.embeddings[idx] if self.embeddings is not None else None
        except ValueError:
            return None
    
    def save_index(self, filepath: str):
        """Save index and metadata to disk"""
        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save FAISS index
        if self.use_gpu:
            # Transfer back to CPU for saving
            cpu_index = faiss.index_gpu_to_cpu(self.index)
            faiss.write_index(cpu_index, filepath + ".faiss")
        else:
            faiss.write_index(self.index, filepath + ".faiss")
        
        # Save metadata
        metadata = {
            'id_map': self.id_map,
            'dimension': self.dimension,
            'embeddings': self.embeddings
        }
        with open(filepath + ".meta", 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"Saved FAISS index with {len(self.id_map)} articles to {filepath}")
    
    def load_index(self, filepath: str):
        """Load index and metadata from disk"""
        # Load FAISS index
        self.index = faiss.read_index(filepath + ".faiss")
        
        # Move to GPU if requested
        if self.use_gpu and faiss.get_num_gpus() > 0:
            self.index = faiss.index_cpu_to_gpu(
                faiss.StandardGpuResources(), 
                0, 
                self.index
            )
        
        # Load metadata
        with open(filepath + ".meta", 'rb') as f:
            metadata = pickle.load(f)
        
        self.id_map = metadata['id_map']
        self.dimension = metadata['dimension']
        self.embeddings = metadata.get('embeddings')
        
        print(f"Loaded FAISS index with {len(self.id_map)} articles from {filepath}")
    
    def clear(self):
        """Clear the index"""
        self.index.reset()
        self.id_map = []
        self.embeddings = None
    
    def __len__(self):
        """Return number of articles in index"""
        return self.index.ntotal
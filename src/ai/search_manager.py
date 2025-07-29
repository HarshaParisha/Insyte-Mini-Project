"""
Insyte AI - Search Manager
Handles semantic search using FAISS for document and note retrieval.
"""

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
import logging
from typing import List, Dict, Any, Tuple, Optional

class SearchManager:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", index_path: str = None):
        """
        Initialize the Search Manager with FAISS index and sentence embeddings.
        
        Args:
            embedding_model: SentenceTransformer model for embeddings
            index_path: Path to save/load FAISS index
        """
        self.embedding_model_name = embedding_model
        self.embedding_model = None
        self.index = None
        self.index_path = index_path or "data/database/faiss_index.bin"
        self.metadata_path = self.index_path.replace(".bin", "_metadata.pkl")
        self.documents = []
        self.metadata = []
        self.logger = logging.getLogger(__name__)
        
    def load_embedding_model(self) -> bool:
        """
        Load the sentence transformer model for embeddings.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.logger.info("Embedding model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {str(e)}")
            return False
    
    def create_index(self, dimension: int = 384) -> bool:
        """
        Create a new FAISS index.
        
        Args:
            dimension: Dimension of embeddings (384 for all-MiniLM-L6-v2)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create FAISS index with cosine similarity
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            self.documents = []
            self.metadata = []
            self.logger.info(f"Created new FAISS index with dimension {dimension}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create FAISS index: {str(e)}")
            return False
    
    def add_documents(self, documents: List[str], metadata: List[Dict] = None) -> bool:
        """
        Add documents to the search index.
        
        Args:
            documents: List of text documents to index
            metadata: Optional metadata for each document
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.embedding_model or not self.index:
            raise RuntimeError("Model and index must be loaded first")
        
        if metadata is None:
            metadata = [{"id": i, "source": "unknown"} for i in range(len(documents))]
        
        try:
            self.logger.info(f"Adding {len(documents)} documents to index")
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(
                documents, 
                normalize_embeddings=True,  # For cosine similarity
                show_progress_bar=True
            )
            
            # Add to FAISS index
            self.index.add(embeddings.astype(np.float32))
            
            # Store documents and metadata
            self.documents.extend(documents)
            self.metadata.extend(metadata)
            
            self.logger.info(f"Added {len(documents)} documents successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add documents: {str(e)}")
            return False
    
    def search(self, query: str, k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            k: Number of results to return
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of search results with documents, scores, and metadata
        """
        if not self.embedding_model or not self.index:
            raise RuntimeError("Model and index must be loaded first")
        
        if self.index.ntotal == 0:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(
                [query], 
                normalize_embeddings=True
            )
            
            # Search in FAISS index
            scores, indices = self.index.search(
                query_embedding.astype(np.float32), 
                min(k, self.index.ntotal)
            )
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and score >= threshold:  # Valid result above threshold
                    results.append({
                        "document": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "score": float(score),
                        "index": int(idx)
                    })
            
            self.logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            return []
    
    def save_index(self) -> bool:
        """
        Save the FAISS index and metadata to disk.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.index:
            self.logger.warning("No index to save")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata and documents
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    "documents": self.documents,
                    "metadata": self.metadata,
                    "embedding_model": self.embedding_model_name
                }, f)
            
            self.logger.info(f"Index saved to {self.index_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save index: {str(e)}")
            return False
    
    def load_index(self) -> bool:
        """
        Load the FAISS index and metadata from disk.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            self.logger.warning("Index files not found")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_path)
            
            # Load metadata and documents
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.metadata = data["metadata"]
                
                # Verify embedding model compatibility
                if data.get("embedding_model") != self.embedding_model_name:
                    self.logger.warning(
                        f"Index was created with {data.get('embedding_model')}, "
                        f"but current model is {self.embedding_model_name}"
                    )
            
            self.logger.info(f"Index loaded from {self.index_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load index: {str(e)}")
            return False
    
    def get_index_info(self) -> Dict[str, Any]:
        """Return information about the search index."""
        if not self.index:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "total_documents": self.index.ntotal,
            "dimension": self.index.d,
            "embedding_model": self.embedding_model_name,
            "index_path": self.index_path
        }
    
    def clear_index(self) -> bool:
        """Clear all documents from the index."""
        try:
            if self.index:
                dimension = self.index.d
                self.index = faiss.IndexFlatIP(dimension)
                self.documents = []
                self.metadata = []
                self.logger.info("Index cleared successfully")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to clear index: {str(e)}")
            return False

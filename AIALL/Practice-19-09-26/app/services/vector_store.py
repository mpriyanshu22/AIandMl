"""
app/services/vector_store.py
Wrapper for ChromaDB embedded vector database.
Handles collection creation, inserting text chunks, and similarity search.
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings


class VectorStoreService:
    """Manages vector operations using ChromaDB."""

    def __init__(self, collection_name: str = "knowledge_base"):
        self.collection_name = collection_name
        
        # Initialize a PersistentClient that saves data to the local disk directory
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # get_or_create_collection creates the collection if it doesn't exist,
        # or loads it from disk if it already does.
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "FastAPI RAG Knowledge Base Chunks"}
        )

    def add_chunks(
        self,
        chunk_ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """
        Store text chunks into ChromaDB.
        Chroma automatically computes embeddings for each string in `documents`.
        """
        self.collection.add(
            ids=chunk_ids,
            documents=documents,
            metadatas=metadatas
        )

    def search(
        self,
        query_text: str,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Search for the top_k most semantically similar text chunks to the query.
        Returns a dictionary containing matching documents, metadata, distances, and ids.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        return results

    def count(self) -> int:
        """Returns the total number of text chunks stored."""
        return self.collection.count()


# Singleton instance ready to be used across the app
vector_store = VectorStoreService()
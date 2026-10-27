"""
app/services/rag_service.py
Orchestrates text chunking, document ingestion, and context retrieval.
"""

import uuid
from typing import List, Dict, Any, Tuple
from app.services.vector_store import vector_store
from app.models.schemas import SourceChunk, DocumentIngestResponse


def chunk_text(text: str, chunk_size: int = 300, chunk_overlap: int = 50) -> List[str]:
    """
    Splits raw text into overlapping chunks using a sliding window technique.
    
    :param text: The full document string.
    :param chunk_size: Approximate maximum character length of each chunk.
    :param chunk_overlap: Character overlap between consecutive chunks.
    :return: List of chunk text strings.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        
        # Advance the window by (chunk_size - chunk_overlap)
        start += (chunk_size - chunk_overlap)
        
        # Stop if the remaining text is smaller than overlap
        if start >= len(text):
            break
            
    return [c for c in chunks if c]  # filter out any accidental empty strings


class RAGService:
    """Service handling ingestion and retrieval operations."""

    def __init__(self):
        self.store = vector_store

    def ingest_document(
        self,
        title: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> DocumentIngestResponse:
        """
        Takes raw document content, splits it into chunks, and stores it in vector DB.
        """
        metadata = metadata or {}
        document_id = str(uuid.uuid4())
        
        # 1. Break text into chunks
        chunks = chunk_text(content, chunk_size=300, chunk_overlap=50)
        
        # 2. Prepare IDs and metadata for each chunk
        chunk_ids = []
        chunk_documents = []
        chunk_metadatas = []
        
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{idx}"
            chunk_ids.append(chunk_id)
            chunk_documents.append(chunk)
            
            # Combine custom metadata with document title and chunk index
            combined_meta = {
                **metadata,
                "document_id": document_id,
                "document_title": title,
                "chunk_index": idx
            }
            chunk_metadatas.append(combined_meta)

        # 3. Store into ChromaDB
        self.store.add_chunks(
            chunk_ids=chunk_ids,
            documents=chunk_documents,
            metadatas=chunk_metadatas
        )

        return DocumentIngestResponse(
            document_id=document_id,
            title=title,
            chunks_created=len(chunks),
            message=f"Successfully ingested and indexed '{title}' into {len(chunks)} chunks."
        )

    def retrieve_context(self, query: str, top_k: int = 3) -> List[SourceChunk]:
        """
        Queries ChromaDB for the top_k relevant chunks and formats them into SourceChunk models.
        """
        results = self.store.search(query_text=query, top_k=top_k)
        
        sources: List[SourceChunk] = []
        
        # Chroma returns lists of lists because it supports batch queries
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            ids = results["ids"][0] if results.get("ids") else ["unknown"] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
            
            for doc, meta, cid, dist in zip(docs, metas, ids, distances):
                sources.append(
                    SourceChunk(
                        chunk_id=cid,
                        document_title=meta.get("document_title", "Untitled"),
                        text=doc,
                        score=round(float(dist), 4)
                    )
                )
                
        return sources


rag_service = RAGService()
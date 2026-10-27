"""
app/routers/documents.py
Document ingestion endpoints for feeding knowledge into RAG.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import DocumentIngestRequest, DocumentIngestResponse
from app.services.rag_service import rag_service

router = APIRouter(
    prefix="/documents",
    tags=["Document Ingestion"]
)


@router.post(
    "/ingest",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a document",
    description="Splits the document into overlapping chunks, computes embeddings, and stores them in ChromaDB."
)
async def ingest_document(payload: DocumentIngestRequest):
    """
    Accepts document title, content, and optional metadata.
    Returns details on created chunks and document ID.
    """
    try:
        response = rag_service.ingest_document(
            title=payload.title,
            content=payload.content,
            metadata=payload.metadata
        )
        return response
    except Exception as e:
        # If anything unexpected happens during vector storage, return HTTP 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}"
        )
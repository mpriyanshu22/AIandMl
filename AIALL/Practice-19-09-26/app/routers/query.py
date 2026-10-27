"""
app/routers/query.py
RAG query endpoint to retrieve context and generate grounded answers.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service

router = APIRouter(
    prefix="/query",
    tags=["RAG Query & Search"]
)


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query Knowledge Base",
    description="Performs semantic search to find relevant context and generates a grounded response."
)
async def query_knowledge_base(payload: QueryRequest):
    """
    1. Retrieves top_k relevant chunks from ChromaDB.
    2. Builds augmented prompt.
    3. Calls LLM service (or offline generator) to synthesize an answer.
    """
    try:
        # Step A: Retrieve relevant source chunks from vector store
        sources = rag_service.retrieve_context(
            query=payload.query,
            top_k=payload.top_k
        )

        # Step B: Generate grounded answer using retrieved sources
        answer = llm_service.generate_answer(
            query=payload.query,
            sources=sources
        )

        # Step C: Return formatted QueryResponse
        return QueryResponse(
            query=payload.query,
            answer=answer,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )
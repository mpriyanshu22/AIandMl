# Vector document upload & semantic search
"""
FastAPI Vector RAG Router for Financial Filings
Demonstrates:
1. Querying the vector store with Query parameters
2. Dynamic document ingestion via POST endpoint
3. RAG pipeline: Query -> Document Retrieval -> Augmented Context -> LLM Analysis
"""
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.vector_service import vector_service
from app.services.llm_service import llm_service
router = APIRouter(
    prefix="/api/v1/rag",
    tags=["Vector RAG Engine"]
)

class DocumentIngestRequest(BaseModel):
    title: str = Field(..., example="BNP Paribas ESG Sustainable Bond Framework")
    section: str = Field(..., example="Eligibility Criteria - Clean Transportation")
    content: str = Field(..., min_length=20, example="Eligible projects must achieve zero direct greenhouse gas emissions.")
    tags: List[str] = Field(default_factory=list, example=["green_bond", "esg", "bnp"])
class RAGQueryRequest(BaseModel):
    company_name: str = Field(..., example="TotalEnergies SE")
    question: str = Field(..., example="What are the guarantee obligations and debt covenants?")
    top_k: int = Field(default=2, ge=1, le=5)


@router.get("/search", summary="Search regulatory & corporate filings via Vector Similarity")
async def search_documents(
    query: str = Query(..., examples=["What is the maximum allowed Net Debt to EBITDA leverage ratio?"]),
    top_k: int = Query(default=3, ge=1, le=10)
):
    results = vector_service.search(query=query, top_k=top_k)
    return {
        "query": query,
        "matches_count": len(results),
        "results": results
    }

@router.post("/documents", status_code=status.HTTP_201_CREATED, summary="Ingest new financial disclosure")
async def ingest_document(doc: DocumentIngestRequest):
    doc_id = vector_service.add_document(
        title=doc.title,
        section=doc.section,
        content=doc.content,
        tags=doc.tags
    )
    return {
        "status": "INGESTED",
        "document_id": doc_id,
        "message": f"Document '{doc.title}' successfully indexed into vector space."
    }

@router.post("/ask", summary="Full RAG Pipeline: Retrieve relevant clauses and synthesize answer")
async def rag_pipeline_ask(request: RAGQueryRequest):
    # Step 1: Retrieve relevant vector chunks
    matched_chunks = vector_service.search(query=request.question, top_k=request.top_k)
    text_contexts = [f"[{c['title']} - {c['section']}]: {c['content']}" for c in matched_chunks]
    # Step 2: Pass context to LLM for grounded answer
    report = await llm_service.generate_compliance_audit(
        company_name=request.company_name,
        query=request.question,
        rag_context=text_contexts
    )
    return {
        "question": request.question,
        "company_name": request.company_name,
        "retrieved_evidence": matched_chunks,
        "llm_synthesis": report
    }
"""
FastAPI GenAI Router with Server-Sent Events (SSE) Streaming
In Node.js:
  app.get('/api/stream', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    const interval = setInterval(() => {
      res.write(`data: ${chunk}\n\n`);
    }, 100);
  });
In FastAPI:
  Use `StreamingResponse(generator(), media_type="text/event-stream")`
  It is much cleaner, fully async, and handles connection teardown automatically!
"""


from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.llm_service import llm_service
router = APIRouter(
    prefix="/api/v1/genai",
    tags=["GenAI & LLM Services"]
)


class FinancialPromptRequest(BaseModel):
    company_name: str = Field(..., example="Airbus SE", description="Company or borrower name")
    query: str = Field(..., example="Assess credit risk and debt covenant compliance under ESG guidelines.", description="The risk officer prompt")
    include_rag: bool = Field(default=True, description="Enrich with vector document chunks")
    include_graph: bool = Field(default=True, description="Enrich with multi-hop knowledge graph")
@router.post("/audit-report", summary="Generate full structured credit audit report")
async def generate_audit_report(request: FinancialPromptRequest):
    """
    Standard Request-Response GenAI endpoint.
    Waits for LLM completion and returns a typed JSON payload.
    """
    report = await llm_service.generate_compliance_audit(
        company_name=request.company_name,
        query=request.query
    )
    return report


@router.get("/stream-analysis", summary="Stream LLM analysis token-by-token (SSE)")
async def stream_analysis(
    company_name: str = Query(default="TotalEnergies SE", description="Company to analyze"),
    query: str = Query(default="Evaluate debt covenants and subsidiary risk", description="Risk audit prompt")
):
    """
    Real-time Token Streaming Endpoint:
    Returns text/event-stream chunks.
    Connect directly to your frontend (React EventSource / fetch stream reader)!
    """
    stream_generator = llm_service.stream_financial_analysis(
        query=query,
        company_name=company_name
    )
    return StreamingResponse(
        stream_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Prevents Nginx/proxy buffering
        }
    )
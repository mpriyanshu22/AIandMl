 # Path & query parameter demonstration

 from fastapi import APIRouter, Query, Path
 from typing import Optional
 from datetime import datetime

 router = APIRouter(
    prefix="/api/v1/system",
    tags=["System & Health"]
 )

@router.get("/health")
async def health_check():
     """
    Basic health check endpoint.
    FastAPI automatically serializes Python dictionaries into JSON!
    """
    return {
        "status": "healthy",
        "service": "BNP Paribas FinGraph-RAG Engine",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/status/{subsystem}")
async def subsystem_status(
    # Path parameter (In Node: req.params.subsystem)
    subsystem: str = Path(...,description="Name of subsystem: e.g. vector_store, graph_db, llm_gateway"),
    # Query parameter (In Node: req.query.detailed)
    detailed: bool = Query(default=False,description="Include detailed memory  latency telemetry")
):
   """
    Demonstrates:
    1. Path Parameters: defined in the route pattern and argument list
    2. Query Parameters: function arguments NOT in route pattern
    FastAPI automatically validates and coerces the types (e.g. detailed string 'true' -> boolean True)
    """
    response = {
        "subsystem": subsystem,
        "is_active": True,
        "status": "OPERATIONAL"
    }
    if detailed:
        response["telemetry"] = {
            "latency_ms":14.2,
            "connected_nodes":128,
            "version":"1.0.0"
        }
    return response


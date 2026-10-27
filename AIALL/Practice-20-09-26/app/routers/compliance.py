# Loan assessment & Dependency Injection (`Depends`)
"""
BNP Paribas Corporate Compliance & Loan Evaluation Router
Concepts demonstrated:
1. POST request with Pydantic body validation (Node.js: req.body)
2. Response Model enforcement (FastAPI strips out any sensitive fields not in schema)
3. HTTPException for error handling (Node.js: return res.status(400).json({ error }))
4. Dependency Injection using `Depends` (Node.js: middleware / auth handler)
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException,Header,status
from app.models.schemas import (
    LoanApplicationCreate,
    LoanApplicationResponse,
    CurrencyEnum,
    RiskRating
)

router =APIRouter(
    prefix="/api/v1/compliance".
    tags=["Compliance & Loan Assessment"]
)

async def verify_bnp_analyst_token(x_bnp_api_key: str = Header(default="bnp-hackathon-2026")):
    """
    FastAPI extracts headers automatically from parameter names.
    If the condition fails, it raises an HTTPException.
    Whatever this function returns is injected into the endpoint!
    """
    if not x_bnp_api_key or not x_bnp_api_key.startswith("bnp-"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing BNP Paribas Analyst API credentials"
        )
    return {"analyst_id": "ANALYST_PARIS_01","role":"Senior Credit Auditor"}


# -----------------------------------------------------------------------------
# POST Endpoint: Submit Corporate Loan for Assessment
# -----------------------------------------------------------------------------

@router.post(
    "/evaluate-loan",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit and evaluate a corporate credit application"
)
async def evaluate_loan_application(
    application: LoanApplicationCreate,  # <-- In Node: req.body validated by Zod
    analyst: dict = Depends(verify_bnp_analyst_token)  # <-- In Node: req.analyst from middleware
):
    """
    Evaluates corporate credit based on BNP Paribas risk thresholds.
    Notice how clean this is:
    - 'application' is ALREADY parsed, validated, and typed.
    - If validation fails, FastAPI returns a 422 Unprocessable Entity with exact field errors!
    """
    # Business rule: loans above 50M in high-risk sectors require special clearance
    high_risk_sectors = ["Defense", "Cryptocurrency", "Speculative Real Estate"]
    is_high_risk = any(sector in high_risk_sectors for sector in application.sectors)
    if application.requested_amount_m > 100 and is_high_risk:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Exposure limit exceeded for speculative sector under BNP Basel III compliance rules."
        )
    # Calculate preliminary risk rating
    if application.requested_amount_m > 50 or is_high_risk:
        rating = RiskRating.HIGH
        passed = False
        notes = f"Escalated to Risk Committee by {analyst['analyst_id']}. Sector exposure requires manual audit."
    elif application.requested_amount_m > 20:
        rating = RiskRating.MEDIUM
        passed = True
        notes = f"Approved within standard credit limits by {analyst['analyst_id']}."
    else:
        rating = RiskRating.LOW
        passed = True
        notes = "Fast-track approved under automated BNP SME liquidity facility."
    # Return response matching LoanApplicationResponse schema
    return LoanApplicationResponse(
        application_id=f"BNP-{uuid.uuid4().hex[:8].upper()}",
        company_name=application.company_name,
        requested_amount_m=application.requested_amount_m,
        currency=application.currency,
        risk_rating=rating,
        compliance_passed=passed,
        review_notes=notes
    )



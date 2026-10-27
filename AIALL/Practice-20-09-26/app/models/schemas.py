"""
FastAPI Pydantic Models (The Python equivalent of TypeScript interfaces + Zod schemas)
In Node.js (TypeScript + Zod):
  const LoanApplicationSchema = z.object({
    company_name: z.string().min(2),
    requested_amount: z.number().positive(),
    currency: z.enum(['EUR', 'USD', 'GBP']).default('EUR'),
    risk_score: z.number().min(0).max(100).optional()
  });
In FastAPI (Pydantic):
  Defined below. Pydantic automatically validates incoming JSON request bodies,
  coerces types, generates Swagger documentation, and provides auto-completion!
"""


from pydantic import BaseModel, Field
from typing import  List, Optional
from enum import Enum

class CurrencyEnum(str, Enum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"

class RiskRating(str, Enum):
    LOW = "LOW"
    MEDUIM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# 1. Incoming Request Model (Node.js: req.body schema)
class LoanApplicationCreate(BaseModel):
    company_name: str = Field(...,min_length=2,description="legal entry name of the borrower")
    registration_number: str = Field(...,description="Commercial registry or lei code")
    requested_amount_m: float = Field(..., gt=0,description="Amount in millions")
    currency: CurrencyEnum = Field(default=CurrencyEnum.EUR, description="Transaction currency")
    jurisdiction: str =Field(default="FR",description="Country ISO code (e.g., FR, UK, US)")
    sectors: List[str] = Field(default_factory=list,description="Industry sectors, e.g. ['Energy','Renewables']")


# 2. Outgoing Response Model (Node.js: res.json structure)
class LoanApplicationResponse(BaseModel):
    application_id: str
    company_name: str
    requested_amount_m: float
    currency: CurrencyEnum
    risk_rating: RiskRating
    compliance_passed: bool
    review_notes: str


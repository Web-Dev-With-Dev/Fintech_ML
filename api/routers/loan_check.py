from fastapi import APIRouter, Depends
from api.schemas import LoanCheckRequest, LoanCheckResponse
from api.dependencies import get_model_registry

router = APIRouter()

@router.post("/analyze/loan", response_model=LoanCheckResponse)
async def analyze_loan(request: LoanCheckRequest, registry=Depends(get_model_registry)):
    detector = registry.get_loan_detector()
    result = detector.predict(request.offer_text, request.language or "en")
    return LoanCheckResponse(
        verdict=result.get("verdict", "SAFE"),
        confidence=result.get("confidence", 0.0),
        risk_score=result.get("risk_score", 0.0),
        warning_flags=result.get("warning_flags", []),
        regulatory_note=result.get("regulatory_note", ""),
    )

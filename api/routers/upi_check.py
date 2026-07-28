from fastapi import APIRouter, Depends
from ..schemas import UPICheckRequest, UPICheckResponse, ScamVerdict
from ..dependencies import ModelRegistry, get_model_registry

router = APIRouter(prefix="/analyze", tags=["UPI Analysis"])

@router.post("/upi", response_model=UPICheckResponse)
async def analyze_upi(
    payload: UPICheckRequest,
    registry: ModelRegistry = Depends(get_model_registry)
) -> UPICheckResponse:
    mule_detector = registry.get_mule_detector
    res = mule_detector.predict(
        payload.sender_id,
        payload.receiver_id,
        payload.amount
    )
    risk_score = res.get("risk_score", 0.1)
    verdict = ScamVerdict.SAFE
    if risk_score > 0.75:
        verdict = ScamVerdict.SCAM
    elif risk_score > 0.4:
        verdict = ScamVerdict.SUSPICIOUS

    return UPICheckResponse(
        verdict=verdict,
        confidence=res.get("confidence", 0.8),
        risk_score=risk_score,
        fraud_type="MULE_CHAIN" if risk_score > 0.75 else None,
        graph_risk_score=risk_score * 1.2,
        mule_chain_detected=risk_score > 0.75,
        ring_id="RING_123" if risk_score > 0.75 else None
    )

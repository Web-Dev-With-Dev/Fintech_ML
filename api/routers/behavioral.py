from fastapi import APIRouter, Depends
from ..schemas import BehaviorCheckRequest, BehaviorResponse, ScamVerdict
from ..dependencies import ModelRegistry, get_model_registry

router = APIRouter(prefix="/analyze/behavior", tags=["Behavioral Analysis"])

@router.post("", response_model=BehaviorResponse)
async def analyze_behavior(
    payload: BehaviorCheckRequest,
    registry: ModelRegistry = Depends(get_model_registry)
) -> BehaviorResponse:
    detector = registry.get_behavioral_detector
    res = detector.predict(payload.session_data)
    risk_score = res.get("risk_score", 0.2)
    verdict = ScamVerdict.SAFE if risk_score < 0.6 else ScamVerdict.SUSPICIOUS

    return BehaviorResponse(
        verdict=verdict,
        confidence=0.85,
        risk_score=risk_score,
        panic_score=risk_score,
        anomaly_type="ERRATIC_MOVEMENT" if risk_score > 0.6 else None,
        intervention_required=risk_score > 0.8
    )

@router.post("/sequence", response_model=BehaviorResponse)
async def analyze_sequence(
    payload: BehaviorCheckRequest,
    registry: ModelRegistry = Depends(get_model_registry)
) -> BehaviorResponse:
    detector = registry.get_behavioral_detector
    res = detector.predict(payload.session_data)
    risk_score = res.get("risk_score", 0.3)
    verdict = ScamVerdict.SAFE if risk_score < 0.7 else ScamVerdict.SCAM

    return BehaviorResponse(
        verdict=verdict,
        confidence=0.9,
        risk_score=risk_score,
        panic_score=0.0,
        anomaly_type="UNUSUAL_SEQUENCE" if risk_score > 0.7 else None,
        intervention_required=risk_score > 0.7
    )

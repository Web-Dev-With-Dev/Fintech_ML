from fastapi import APIRouter, Depends
from ..schemas import BehaviorCheckRequest, BehaviorResponse, ScamVerdict
from ..dependencies import ModelRegistry, get_model_registry

router = APIRouter(prefix="/analyze", tags=["Behavioral Analysis"])

def calculate_behavior_risk(session_data: dict) -> tuple:
    if not isinstance(session_data, dict):
        return 0.10, 0.10, None, False

    vel = float(session_data.get("transaction_velocity", 1))
    odd_hour = bool(session_data.get("odd_hour_transfer", False))
    drain = bool(session_data.get("full_balance_drain", False))
    first_time = bool(session_data.get("first_time_recipient", False))

    risk = 0.10
    anomalies = []
    if vel > 4:
        risk += 0.35
        anomalies.append("TRANSACTION_VELOCITY_SPIKE")
    if odd_hour:
        risk += 0.20
        anomalies.append("ODD_HOUR_ACTIVITY")
    if drain:
        risk += 0.30
        anomalies.append("FULL_ACCOUNT_DRAIN")
    if first_time and drain:
        risk += 0.15
        anomalies.append("RAPID_NEW_RECIPIENT_DRAIN")

    risk_score = round(min(1.0, risk), 2)
    panic_score = risk_score
    anomaly_type = " | ".join(anomalies) if anomalies else None
    intervention = risk_score >= 0.75

    return risk_score, panic_score, anomaly_type, intervention

@router.post("/behavior", response_model=BehaviorResponse)
async def analyze_behavior(
    payload: BehaviorCheckRequest,
    registry: ModelRegistry = Depends(get_model_registry)
) -> BehaviorResponse:
    risk_score, panic_score, anomaly_type, intervention = calculate_behavior_risk(payload.session_data)

    if risk_score >= 0.75:
        verdict = ScamVerdict.SCAM
    elif risk_score >= 0.45:
        verdict = ScamVerdict.SUSPICIOUS
    else:
        verdict = ScamVerdict.SAFE

    return BehaviorResponse(
        verdict=verdict,
        confidence=0.92,
        risk_score=risk_score,
        panic_score=panic_score,
        anomaly_type=anomaly_type,
        intervention_required=intervention
    )


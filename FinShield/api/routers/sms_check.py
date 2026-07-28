import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from ..schemas import SMSCheckRequest, SMSCheckResponse, ScamVerdict
from ..dependencies import ModelRegistry, get_model_registry

router = APIRouter(prefix="/analyze", tags=["SMS Analysis"])

rate_limits = {}

async def _check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    count = rate_limits.get(client_ip, 0)
    if count >= 100:
        raise HTTPException(status_code=429, detail="Too Many Requests")
    rate_limits[client_ip] = count + 1

async def async_predict(model: any, text: str) -> dict:
    await asyncio.sleep(0.01)
    return model.predict(text)

@router.post("/sms", response_model=SMSCheckResponse)
async def analyze_sms(
    request: Request,
    payload: SMSCheckRequest,
    registry: ModelRegistry = Depends(get_model_registry)
) -> SMSCheckResponse:
    await _check_rate_limit(request)
    lang = payload.language or "en"
    sms_task = asyncio.create_task(async_predict(registry.get_sms_classifier, payload.text))
    phishing_task = asyncio.create_task(async_predict(registry.get_phishing_detector, payload.text))
    sms_res, phishing_res = await asyncio.gather(sms_task, phishing_task)
    risk_score = max(sms_res.get("risk_score", 0), phishing_res.get("risk_score", 0))
    confidence = max(sms_res.get("confidence", 0), phishing_res.get("confidence", 0))
    verdict = ScamVerdict.SAFE
    if risk_score > 0.8:
        verdict = ScamVerdict.SCAM
    elif risk_score > 0.5:
        verdict = ScamVerdict.SUSPICIOUS

    return SMSCheckResponse(
        verdict=verdict,
        confidence=confidence,
        risk_score=risk_score,
        red_flags=["Urgency detected", "Suspicious URL"] if risk_score > 0.5 else [],
        category="PHISHING" if phishing_res.get("risk_score", 0) > sms_res.get("risk_score", 0) else "GENERAL_SCAM",
        explanation_local="कृपया इस संदेश से सावधान रहें।" if lang == 'hi' else None,
        explanation_en="This message has indicators of a common scam.",
        action_advice="Do not click any links.",
        helpline="1930"
    )

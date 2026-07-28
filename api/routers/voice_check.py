from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from ..schemas import AudioCheckResponse, ScamVerdict
from ..dependencies import ModelRegistry, get_model_registry

router = APIRouter(prefix="/analyze", tags=["Voice Analysis"])

@router.post("/audio", response_model=AudioCheckResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    registry: ModelRegistry = Depends(get_model_registry)
) -> AudioCheckResponse:
    detector = registry.get_voice_detector
    _content = await file.read()
    res = detector.predict(len(_content))
    risk_score = res.get("risk_score", 0.4)
    verdict = ScamVerdict.SAFE
    if risk_score > 0.8:
        verdict = ScamVerdict.SCAM
    elif risk_score > 0.5:
        verdict = ScamVerdict.SUSPICIOUS

    return AudioCheckResponse(
        verdict=verdict,
        confidence=0.88,
        risk_score=risk_score,
        transcript="Simulated transcript text indicating potential context.",
        acoustic_flags=["High stress detected"] if risk_score > 0.5 else [],
        language_detected=language or "hi"
    )

import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from ..schemas import SMSCheckRequest, SMSCheckResponse, ScamVerdict
from ..dependencies import ModelRegistry, get_model_registry
from nlp.xai_explainer import EXPLANATION_TEMPLATES, ACTION_ADVICE

router = APIRouter(prefix="/analyze", tags=["SMS Analysis"])

rate_limits = {}

async def _check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    count = rate_limits.get(client_ip, 0)
    if count >= 100:
        raise HTTPException(status_code=429, detail="Too Many Requests")
    rate_limits[client_ip] = count + 1

async def async_predict(model: any, text: str, lang: str = "en") -> dict:
    await asyncio.sleep(0.01)
    try:
        return model.predict(text, lang)
    except TypeError:
        try:
            return model.predict(text)
        except Exception:
            return {"risk_score": 0.1, "confidence": 0.5, "verdict": "SAFE"}

def build_dynamic_explanations(text: str, lang: str, red_flags: list, verdict: str) -> tuple[str, str, str]:
    t = text.lower()
    local_reasons = []
    en_reasons = []

                                            
    trigger_map = [
        ('otp', 'otp_keyword'),
        ('urgent', 'urgent_tone'),
        ('turant', 'urgent_tone'),
        ('jald', 'urgent_tone'),
        ('http', 'contains_url'),
        ('.com', 'contains_url'),
        ('bit.ly', 'contains_url'),
        ('kyc', 'kyc_expiry'),
        ('block', 'account_blocked'),
        ('suspend', 'account_blocked'),
        ('winner', 'lottery_won'),
        ('prize', 'lottery_won'),
        ('lottery', 'lottery_won'),
        ('inaam', 'lottery_won'),
        ('pan', 'pan_update'),
        ('aadhaar', 'aadhaar_link'),
        ('pin', 'asks_for_pin'),
        ('password', 'asks_for_pin')
    ]

    for keyword, tmpl_key in trigger_map:
        if keyword in t and tmpl_key in EXPLANATION_TEMPLATES:
            loc_text = EXPLANATION_TEMPLATES[tmpl_key].get(lang, EXPLANATION_TEMPLATES[tmpl_key]['en'])
            en_text = EXPLANATION_TEMPLATES[tmpl_key]['en']
            if loc_text not in local_reasons:
                local_reasons.append(loc_text)
            if en_text not in en_reasons:
                en_reasons.append(en_text)

    if not en_reasons:
        if verdict in ["SCAM", "SUSPICIOUS"]:
            explanation_en = "This message contains suspicious wording or patterns typical of financial fraud."
            explanation_local = EXPLANATION_TEMPLATES.get('urgent_tone', {}).get(lang, explanation_en)
        else:
            explanation_en = "This message appears legitimate and safe."
            explanation_local = "यह संदेश सुरक्षित प्रतीत होता है।" if lang == 'hi' else "This message appears safe."
    else:
        explanation_en = " | ".join(en_reasons[:3])
        explanation_local = " | ".join(local_reasons[:3])

    if verdict in ["SCAM", "SUSPICIOUS"]:
        action_advice = ACTION_ADVICE.get(lang, ACTION_ADVICE['en'])
    else:
        action_advice = "No action required. Always stay cautious sharing personal details."

    return explanation_local, explanation_en, action_advice

@router.post("/sms", response_model=SMSCheckResponse)
async def analyze_sms(
    request: Request,
    payload: SMSCheckRequest,
    registry: ModelRegistry = Depends(get_model_registry)
) -> SMSCheckResponse:
    await _check_rate_limit(request)
    lang = payload.get_language()
    text = payload.text or ""


    sms_task = asyncio.create_task(async_predict(registry.get_sms_classifier, text, lang))
    phishing_task = asyncio.create_task(async_predict(registry.get_phishing_detector, text, lang))
    sms_res, phishing_res = await asyncio.gather(sms_task, phishing_task)

                               
    red_flags = list(set(
        sms_res.get("red_flags", []) + 
        phishing_res.get("url_flags", []) + 
        phishing_res.get("text_flags", [])
    ))

                     
    if "risk_score" in sms_res:
        sms_risk = float(sms_res["risk_score"])
    elif sms_res.get("label") == "SCAM" or sms_res.get("rule_triggered"):
        sms_risk = float(sms_res.get("confidence", 0.95))
    else:
        sms_risk = 0.10

                       
    if "risk_score" in phishing_res:
        phish_risk = float(phishing_res["risk_score"])
    elif phishing_res.get("is_phishing"):
        phish_risk = float(phishing_res.get("confidence", 0.90))
    else:
        phish_risk = 0.10

                                                             
    if len(red_flags) >= 2:
        risk_score = max(sms_risk, phish_risk, 0.88)
    elif len(red_flags) == 1:
        risk_score = max(sms_risk, phish_risk, 0.65)
    else:
        risk_score = max(sms_risk, phish_risk)

    sms_conf = sms_res.get("confidence", 0.5)
    phish_conf = phishing_res.get("confidence", 0.5)
    confidence = max(sms_conf, phish_conf)

                       
    if risk_score >= 0.75:
        verdict = ScamVerdict.SCAM
    elif risk_score >= 0.45:
        verdict = ScamVerdict.SUSPICIOUS
    else:
        verdict = ScamVerdict.SAFE

                            
    if phish_risk > sms_risk and phish_risk > 0.4:
        category = str(phishing_res.get("category", "PHISHING")).upper()
    elif sms_risk > 0.4 or len(red_flags) > 0:
        category = "GENERAL_SCAM"
    else:
        category = "SAFE"

                                
    exp_local, exp_en, advice = build_dynamic_explanations(text, lang, red_flags, verdict.value)

    return SMSCheckResponse(
        verdict=verdict,
        confidence=round(float(confidence), 2),
        risk_score=round(float(risk_score), 2),
        red_flags=red_flags,
        category=category,
        explanation_local=exp_local,
        explanation_en=exp_en,
        action_advice=advice,
        helpline="1930"
    )



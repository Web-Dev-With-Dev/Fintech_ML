from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class ScamVerdict(str, Enum):
    SCAM = "SCAM"
    SUSPICIOUS = "SUSPICIOUS"
    SAFE = "SAFE"

class BaseAnalysisResponse(BaseModel):
    verdict: ScamVerdict
    confidence: float
    risk_score: float = Field(ge=0.0, le=1.0)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SMSCheckResponse(BaseAnalysisResponse):
    red_flags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    explanation_local: Optional[str] = None
    explanation_en: Optional[str] = None
    action_advice: Optional[str] = None
    helpline: Optional[str] = None

class UPICheckResponse(BaseAnalysisResponse):
    fraud_type: Optional[str] = None
    graph_risk_score: float = 0.0
    mule_chain_detected: bool = False
    ring_id: Optional[str] = None

class BehaviorResponse(BaseAnalysisResponse):
    panic_score: float = 0.0
    anomaly_type: Optional[str] = None
    intervention_required: bool = False

class AudioCheckResponse(BaseAnalysisResponse):
    transcript: Optional[str] = None
    acoustic_flags: List[str] = Field(default_factory=list)
    language_detected: Optional[str] = None

class LoanCheckResponse(BaseAnalysisResponse):
    warning_flags: List[str] = Field(default_factory=list)
    regulatory_note: Optional[str] = None

class HelplineInfo(BaseModel):
    number: str
    name: str
    description: str
    available_24x7: bool

class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    version: str
    uptime: str

class SMSCheckRequest(BaseModel):
    text: str
    language: Optional[str] = None
    lang: Optional[str] = None

    def get_language(self) -> str:
        return self.lang or self.language or "en"

class AudioCheckRequest(BaseModel):
    audio_url: Optional[str] = None
    base64_audio: Optional[str] = None
    language: Optional[str] = None
    lang: Optional[str] = None

    def get_language(self) -> str:
        return self.lang or self.language or "en"

class UPICheckRequest(BaseModel):
    sender_id: str
    receiver_id: str
    amount: float
    timestamp: datetime
    message_text: Optional[str] = None

class LoanCheckRequest(BaseModel):
    offer_text: str
    app_name: Optional[str] = None
    language: Optional[str] = None
    lang: Optional[str] = None

    def get_language(self) -> str:
        return self.lang or self.language or "en"

class BehaviorCheckRequest(BaseModel):
    user_id: str
    session_data: Dict[str, Any]
    language: Optional[str] = None
    lang: Optional[str] = None

    def get_language(self) -> str:
        return self.lang or self.language or "en"



class ReportRequest(BaseModel):
    text: str
    category: str
    language: str
    location: Optional[str] = None

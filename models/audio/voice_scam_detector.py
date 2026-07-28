import tempfile
import os
from typing import Dict, Any, Optional
from .voice_transcriber import VoiceTranscriber

class VoiceScamDetector:
    def __init__(self, transcriber: VoiceTranscriber, text_classifier: Any):
        self.transcriber = transcriber
        self.text_classifier = text_classifier
        
    def compute_acoustic_scam_score(self, audio_features: Dict[str, float]) -> float:
        score = 0.0
        
        speech_rate = audio_features.get('speech_rate', 0.0)
        if speech_rate > 150.0:
            score += 0.4
        elif speech_rate > 120.0:
            score += 0.2
            
        pitch_variance = audio_features.get('pitch_variance', 0.0)
        if pitch_variance > 5000.0:
            score += 0.3
            
        avg_pause = audio_features.get('avg_pause_duration', 1.0)
        if avg_pause < 0.2:
            score += 0.3
            
        return min(score, 1.0)

    def analyze_call(self, audio_path: str, lang: Optional[str] = None) -> Dict[str, Any]:
        detected_lang = lang
        if not detected_lang:
            try:
                detected_lang = self.transcriber.detect_audio_language(audio_path)
            except Exception as e:
                print(f"Language detection failed: {e}")
                detected_lang = "en"
                
        transcription_result = self.transcriber.transcribe(audio_path, language=detected_lang)
        transcript = transcription_result['text']
        
        try:
            audio_features = self.transcriber.extract_audio_features(audio_path)
            acoustic_scam_prob = self.compute_acoustic_scam_score(audio_features)
            acoustic_flags = audio_features
        except Exception as e:
            print(f"Acoustic feature extraction failed: {e}")
            acoustic_scam_prob = 0.0
            acoustic_flags = {}

        text_scam_prob = 0.0
        text_flags = {}
        
        try:
            if hasattr(self.text_classifier, 'predict_proba'):
                probs = self.text_classifier.predict_proba([transcript])[0]
                text_scam_prob = float(probs[1] if len(probs) > 1 else probs[0])
            elif hasattr(self.text_classifier, 'analyze'):
                res = self.text_classifier.analyze(transcript)
                text_scam_prob = float(res.get('scam_probability', 0.0))
                text_flags = res.get('flags', {})
            else:
                text_scam_prob = float(self.text_classifier(transcript))
        except Exception as e:
            print(f"Text classification failed: {e}")

        final_confidence = (text_scam_prob * 0.7) + (acoustic_scam_prob * 0.3)
        verdict = "SCAM" if final_confidence >= 0.5 else "SAFE"
        
        red_flags = []
        if text_scam_prob > 0.6:
            red_flags.append("Suspicious conversation content")
        if acoustic_scam_prob > 0.6:
            red_flags.append("High urgency or scripted acoustic tone detected")
            
        return {
            "verdict": verdict,
            "confidence": final_confidence,
            "transcript": transcript,
            "language": detected_lang,
            "acoustic_flags": acoustic_flags,
            "text_flags": text_flags,
            "red_flags": red_flags,
            "helpline": "Call 1930 for National Cyber Crime Reporting Portal (India) if you suspect a scam."
        }
        
    def analyze_from_bytes(self, audio_bytes: bytes, lang: Optional[str] = None, format: str = 'wav') -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name
            
        try:
            return self.analyze_call(temp_path, lang=lang)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

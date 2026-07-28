import os
import tempfile
import numpy as np
from typing import Dict, Any, Optional

try:
    import whisper
except ImportError:
    whisper = None
    print("Warning: 'whisper' library is not installed. Voice transcription will not work.")

try:
    import librosa
except ImportError:
    librosa = None
    print("Warning: 'librosa' library is not installed. Acoustic feature extraction will fail.")

class VoiceTranscriber:
    def __init__(self, model_size: str = 'small'):
        self.model_size = model_size
        self.model = None
        if whisper is not None:
            print(f"Loading Whisper model '{model_size}'...")
            self.model = whisper.load_model(model_size)
            print("Whisper model loaded.")
        else:
            print("Whisper is not available. Please pip install openai-whisper.")

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        if self.model is None:
            raise RuntimeError("Whisper model is not initialized.")
            
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        options = {}
        if language:
            options['language'] = language
            
        result = self.model.transcribe(audio_path, **options)
        
        duration = 0.0
        if result.get("segments") and len(result["segments"]) > 0:
            duration = result["segments"][-1]["end"]
            
        return {
            "text": result["text"].strip(),
            "language": result.get("language", language or "unknown"),
            "segments": result.get("segments", []),
            "duration": duration
        }

    def transcribe_from_bytes(self, audio_bytes: bytes, format: str = 'wav') -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name
            
        try:
            return self.transcribe(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def detect_audio_language(self, audio_path: str) -> str:
        if self.model is None:
            raise RuntimeError("Whisper model is not initialized.")
            
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        
        _, probs = self.model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        return detected_lang

    def extract_audio_features(self, audio_path: str) -> Dict[str, float]:
        if librosa is None:
            raise RuntimeError("Librosa is not installed.")
            
        y, sr = librosa.load(audio_path, sr=None)
        
        rms = librosa.feature.rms(y=y)[0]
        energy_level = float(np.mean(rms))
        
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        valid_pitches = pitches[pitches > 0]
        pitch_variance = float(np.var(valid_pitches)) if len(valid_pitches) > 0 else 0.0
        
        intervals = librosa.effects.split(y, top_db=20)
        total_duration = librosa.get_duration(y=y, sr=sr)
        
        pause_count = len(intervals) - 1 if len(intervals) > 0 else 0
        speech_duration = sum([(end - start) / sr for start, end in intervals])
        pause_duration = total_duration - speech_duration
        
        avg_pause_duration = pause_duration / pause_count if pause_count > 0 else 0.0
        
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        peaks = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
        syllable_count_proxy = len(peaks)
        speech_rate = (syllable_count_proxy / total_duration) * 60 if total_duration > 0 else 0.0
        
        return {
            "speech_rate": speech_rate,
            "pause_count": float(pause_count),
            "avg_pause_duration": float(avg_pause_duration),
            "pitch_variance": pitch_variance,
            "energy_level": energy_level
        }

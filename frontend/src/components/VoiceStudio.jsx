import React, { useState } from 'react';
import { Activity, Mic, ShieldAlert, Play } from 'lucide-react';
import axios from 'axios';

const VOICE_PRESETS = [
  {
    label: "🎙️ Hindi Bank Officer Scam Call",
    audio_url: "bank_scam_call.wav",
    lang: "hi"
  },
  {
    label: "🎙️ Tamil Police Threat Call",
    audio_url: "police_threat_scam_audio",
    lang: "ta"
  },
  {
    label: "🎙️ English Cyber Extortion",
    audio_url: "cyber_extortion_threat.wav",
    lang: "en"
  },
  {
    label: "🎙️ Normal Friendly Call",
    audio_url: "normal_family_call.mp3",
    lang: "en"
  }
];

export default function VoiceStudio({ selectedLang }) {
  const [audioUrl, setAudioUrl] = useState(VOICE_PRESETS[0].audio_url);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async (preset = null) => {
    const url = preset ? preset.audio_url : audioUrl;
    const l = preset ? preset.lang : selectedLang;

    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/v1/analyze/audio', {
        audio_url: url,
        lang: l
      });
      setResult(res.data);

      try {
        const { addScanHistoryItem } = await import('../utils/scanLogger');
        addScanHistoryItem({
          name: `Voice Call Analysis (${url})`,
          category: 'Voice Interceptor',
          risk: res.data.risk_score,
          verdict: res.data.verdict,
          text: url,
          xai: res.data.transcript,
          tab: 'voice'
        });
      } catch (e) {}
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '32px', display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '24px' }}>
      
      {/* Input Panel */}
      <div className="gov-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <Activity size={22} color="#000000" />
          <h2 style={{ fontSize: '24px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000' }}>
            Vernacular Voice Call Interceptor
          </h2>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          OpenAI Whisper Speech Neural Net + Librosa Acoustic Pitch/Pause DSP Extractor.
        </p>

        {/* Sample Call Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
          {VOICE_PRESETS.map((p, i) => (
            <button
              key={i}
              className="btn-light"
              style={{ textAlign: 'left', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              onClick={() => {
                setAudioUrl(p.audio_url);
                handleAnalyze(p);
              }}
            >
              <span>{p.label}</span>
              <Play size={14} color="#000000" />
            </button>
          ))}
        </div>

        {/* Input Field */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px', fontWeight: '700' }}>
            AUDIO FILE URL OR RECORDING NAME
          </label>
          <input className="gov-input" value={audioUrl} onChange={e => setAudioUrl(e.target.value)} />
        </div>

        <button className="btn-black" style={{ width: '100%', justifyContent: 'center' }} onClick={() => handleAnalyze()} disabled={loading}>
          <Mic size={18} />
          {loading ? 'Transcribing & Analyzing Acoustic Features...' : 'Analyze Call Audio Recording'}
        </button>
      </div>

      {/* Results Panel */}
      <div className="gov-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        {result ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--border-light)' }}>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700' }}>CALL SCAM VERDICT</span>
                <div style={{ marginTop: '4px' }}>
                  {result.verdict === 'SCAM' ? (
                    <span className="badge-scam">🚨 SCAM CALL DETECTED</span>
                  ) : (
                    <span className="badge-safe">✅ SAFE CALL</span>
                  )}
                </div>
              </div>

              <span style={{ fontSize: '11px', background: '#F1F5F9', color: '#0F172A', padding: '4px 10px', borderRadius: '12px', fontWeight: '700', border: '1px solid var(--border-light)' }}>
                LANG: {result.language_detected.toUpperCase()}
              </span>
            </div>

            {/* Audio Waveform Spectrum Animation */}
            <div style={{ background: '#F8FAFC', border: '1px solid var(--border-light)', borderRadius: '12px', padding: '16px', marginBottom: '16px' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
                ACOUSTIC SPECTRUM & VELOCITY SPECTROGRAM
              </span>
              <div style={{ display: 'flex', alignItems: 'flex-end', height: '40px', gap: '3px' }}>
                {[30, 55, 80, 45, 90, 100, 75, 40, 60, 85, 95, 70, 50, 80, 100, 60, 40, 70, 90, 55, 35].map((h, idx) => (
                  <div
                    key={idx}
                    style={{
                      flex: 1,
                      height: `${h}%`,
                      background: result.verdict === 'SCAM' ? '#DC2626' : '#16A34A',
                      borderRadius: '2px',
                      transition: 'height 0.3s ease'
                    }}
                  />
                ))}
              </div>
            </div>

            {/* Transcript Box */}
            <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', padding: '16px', borderRadius: '10px', marginBottom: '16px' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: '#1D4ED8', display: 'block', marginBottom: '6px' }}>
                REAL-TIME WHISPER TRANSCRIPTION
              </span>
              <p style={{ fontSize: '14px', lineHeight: '1.6', fontWeight: '600', color: '#0F172A' }}>
                "{result.transcript}"
              </p>
            </div>

            {/* Acoustic Anomaly Flags */}
            {result.acoustic_flags && result.acoustic_flags.length > 0 && (
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px', fontWeight: '700' }}>LIBROSA ACOUSTIC ANOMALIES</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {result.acoustic_flags.map((flag, idx) => (
                    <span key={idx} style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '12px', background: '#FEF2F2', color: '#DC2626', border: '1px solid #FCA5A5', fontWeight: '600' }}>
                      🔊 {flag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 0' }}>
            <Activity size={48} color="var(--text-subtle)" style={{ marginBottom: '16px' }} />
            <h3 style={{ fontSize: '18px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000', marginBottom: '8px' }}>
              Voice Interceptor Studio
            </h3>
            <p style={{ fontSize: '13px', maxWidth: '300px', margin: '0 auto' }}>
              Select a sample call recording to extract OpenAI Whisper speech transcripts & Librosa acoustic stress signatures.
            </p>
          </div>
        )}
      </div>

    </div>
  );
}

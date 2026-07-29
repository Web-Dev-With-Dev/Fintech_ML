import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, HelpCircle, Volume2, PhoneCall, ShieldAlert, Send, Globe } from 'lucide-react';
import axios from 'axios';

const LANGUAGES = [
  { code: 'hi', label: 'हिंदी (Hindi)' },
  { code: 'en', label: 'English' },
  { code: 'hinglish', label: 'Hinglish' },
  { code: 'ta', label: 'தமிழ் (Tamil)' },
  { code: 'te', label: 'తెలుగు (Telugu)' },
  { code: 'bn', label: 'বাংলা (Bengali)' },
  { code: 'mr', label: 'मराठी (Marathi)' },
  { code: 'gu', label: 'ગુજરાતી (Gujarati)' }
];

const PRESETS = [
  {
    label: "⚡ Electricity Bill Cutoff",
    text: "URGENT: Your electricity connection will be disconnected tonight at 9:30 PM due to unpaid bill. Immediately pay or call electricity officer at 9876543210.",
    lang: "hi"
  },
  {
    label: "🎁 KBC Lottery Prize",
    text: "Congratulations! You won 25,00,000 in KBC Lucky Draw. Share your OTP and Aadhaar details to claim prize money.",
    lang: "hinglish"
  },
  {
    label: "🏦 SBI KYC Account Block",
    text: "Dear SBI customer, your account is blocked due to pending KYC update. Click http://update-sbi-kyc.xyz immediately.",
    lang: "hi"
  },
  {
    label: "☕ Safe Friendly Text",
    text: "Hello, when are we meeting for coffee today near the market?",
    lang: "en"
  }
];

export default function SMSScanner({ selectedLang }) {
  const [currentLang, setCurrentLang] = useState(selectedLang || 'hi');
  const [text, setText] = useState(PRESETS[0].text);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async (overrideText = null, overrideLang = null) => {
    const msgText = overrideText || text;
    const targetLang = overrideLang || currentLang;
    if (!msgText.trim()) return;

    setLoading(true);
    setError('');
    try {
      const res = await axios.post('http://localhost:8000/api/v1/analyze/sms', {
        text: msgText,
        lang: targetLang
      });
      setResult(res.data);

      // Log to live history
      try {
        const { addScanHistoryItem } = await import('../utils/scanLogger');
        addScanHistoryItem({
          name: msgText.length > 30 ? msgText.substring(0, 30) + '...' : msgText,
          category: 'SMS Phishing',
          risk: res.data.risk_score,
          verdict: res.data.verdict,
          text: msgText,
          xai: res.data.explanation_local || res.data.explanation_en,
          tab: 'sms'
        });
      } catch (e) {}
    } catch (err) {
      console.error(err);
      setError('Could not connect to FinShield AI backend. Make sure uvicorn is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const speakText = (content) => {
    if ('speechSynthesis' in window && content) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(content);
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div style={{ padding: '32px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
      
      {/* Input Panel */}
      <div className="gov-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldAlert size={22} color="#000000" />
            <h2 style={{ fontSize: '24px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000' }}>
              Vernacular SMS & Phishing Scanner
            </h2>
          </div>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Paste any SMS, WhatsApp message, or tap a sample scam scenario below to scan with XGBoost & Explainable AI models.
        </p>

        {/* Response Language Selection Bar */}
        <div style={{ background: '#F8FAFC', border: '1px solid var(--border-light)', padding: '12px 16px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Globe size={18} color="#000000" />
            <span style={{ fontSize: '13px', fontWeight: '700', color: '#000000' }}>Target Response Language:</span>
          </div>
          <select
            className="gov-input"
            style={{ width: 'auto', padding: '6px 12px', fontSize: '13px', fontWeight: '700', background: '#FFFFFF' }}
            value={currentLang}
            onChange={(e) => {
              setCurrentLang(e.target.value);
              if (result) {
                handleAnalyze(null, e.target.value);
              }
            }}
          >
            {LANGUAGES.map(l => (
              <option key={l.code} value={l.code}>{l.label}</option>
            ))}
          </select>
        </div>

        {/* Preset Chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              className="btn-light"
              style={{ fontSize: '12px', padding: '6px 12px' }}
              onClick={() => {
                setText(p.text);
                setCurrentLang(p.lang || currentLang);
                handleAnalyze(p.text, p.lang || currentLang);
              }}
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* Text Input */}
        <textarea
          className="gov-input"
          rows={6}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste SMS or message content here..."
          style={{ resize: 'vertical', marginBottom: '16px', lineHeight: '1.6' }}
        />

        <button
          className="btn-black"
          onClick={() => handleAnalyze()}
          disabled={loading}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          <Send size={18} />
          {loading ? 'Analyzing Message with ML Models...' : `Scan Message (${LANGUAGES.find(l => l.code === currentLang)?.label})`}
        </button>

        {error && (
          <div style={{ marginTop: '16px', padding: '12px', borderRadius: '8px', background: '#FEF2F2', color: '#DC2626', fontSize: '13px', border: '1px solid #FCA5A5' }}>
            {error}
          </div>
        )}
      </div>

      {/* Output Panel */}
      <div className="gov-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        
        {result ? (
          <div>
            {/* Header Result Badge */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid var(--border-light)' }}>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700', letterSpacing: '0.05em' }}>SCAM VERDICT</span>
                <div style={{ marginTop: '4px' }}>
                  {result.verdict === 'SCAM' && (
                    <span className="badge-scam"><AlertTriangle size={16} /> SCAM DETECTED</span>
                  )}
                  {result.verdict === 'SUSPICIOUS' && (
                    <span className="badge-suspicious"><HelpCircle size={16} /> SUSPICIOUS PATTERN</span>
                  )}
                  {result.verdict === 'SAFE' && (
                    <span className="badge-safe"><CheckCircle size={16} /> SAFE MESSAGE</span>
                  )}
                </div>
              </div>

              {/* Category Badge */}
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700', letterSpacing: '0.05em' }}>CATEGORY</span>
                <div style={{ fontSize: '14px', fontWeight: '800', color: '#000000', marginTop: '4px' }}>
                  {result.category}
                </div>
              </div>
            </div>

            {/* Risk Meter Progress Bar */}
            <div style={{ marginBottom: '20px', background: '#F8FAFC', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-light)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: '600', marginBottom: '8px' }}>
                <span>Risk Probability Score</span>
                <span style={{ color: result.risk_score > 0.7 ? 'var(--status-scam)' : result.risk_score > 0.4 ? 'var(--status-suspicious)' : 'var(--status-safe)' }}>
                  {(result.risk_score * 100).toFixed(0)}%
                </span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#E2E8F0', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{
                  width: `${result.risk_score * 100}%`,
                  height: '100%',
                  background: result.risk_score > 0.7 ? '#DC2626' : result.risk_score > 0.4 ? '#D97706' : '#16A34A',
                  transition: 'width 0.6s ease'
                }} />
              </div>
            </div>

            {/* Localized XAI Explanation Box */}
            <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', padding: '16px', borderRadius: '10px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', fontWeight: '700', color: '#1D4ED8', letterSpacing: '0.05em' }}>
                  EXPLAINABLE AI (XAI) REASONING [{currentLang.toUpperCase()}]
                </span>
                <button
                  onClick={() => speakText(result.explanation_local || result.explanation_en)}
                  style={{ background: 'none', border: 'none', color: '#1D4ED8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: '700' }}
                >
                  <Volume2 size={16} /> Voice Read-Aloud
                </button>
              </div>

              <p style={{ fontSize: '14px', lineHeight: '1.6', fontWeight: '600', color: '#0F172A', marginBottom: '8px' }}>
                {result.explanation_local || result.explanation_en}
              </p>
              {result.explanation_local && result.explanation_en !== result.explanation_local && (
                <p style={{ fontSize: '12px', color: '#475569', fontStyle: 'italic' }}>
                  English: {result.explanation_en}
                </p>
              )}
            </div>

            {/* Red Flags Trigger Chips */}
            {result.red_flags && result.red_flags.length > 0 && (
              <div style={{ marginBottom: '16px' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px', fontWeight: '700' }}>DETECTED RISK TRIGGERS</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {result.red_flags.map((flag, i) => (
                    <span key={i} style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '12px', background: '#FEF2F2', color: '#DC2626', border: '1px solid #FCA5A5', fontWeight: '600' }}>
                      🚩 {flag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Action Advice Box */}
            <div style={{ background: '#F8FAFC', border: '1px solid var(--border-light)', padding: '12px 16px', borderRadius: '10px' }}>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>RECOMMENDED USER ACTION</span>
              <p style={{ fontSize: '13px', color: 'var(--text-main)', fontWeight: '500' }}>
                {result.action_advice}
              </p>
            </div>

          </div>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 0' }}>
            <ShieldAlert size={48} color="var(--text-subtle)" style={{ marginBottom: '16px' }} />
            <h3 style={{ fontSize: '18px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000', marginBottom: '8px' }}>
              Ready to Scan Messages
            </h3>
            <p style={{ fontSize: '13px', maxWidth: '300px', margin: '0 auto' }}>
              Type or select a message preset on the left to receive instant machine learning scam verdicts & XAI explanations in your chosen language.
            </p>
          </div>
        )}

        {/* Quick Emergency Call Button */}
        <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-light)', paddingTop: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', fontWeight: '600' }}>VICTIM OF FINANCIAL FRAUD?</span>
            <span style={{ fontSize: '13px', fontWeight: '700', color: '#000000' }}>Call National Cybercrime Portal</span>
          </div>
          <a
            href="tel:1930"
            className="btn-black"
            style={{ padding: '8px 16px', background: '#DC2626', textDecoration: 'none', fontSize: '13px' }}
          >
            <PhoneCall size={16} /> Dial 1930
          </a>
        </div>

      </div>

    </div>
  );
}

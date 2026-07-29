import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, FileText, ArrowRight, Globe } from 'lucide-react';
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

const LOAN_PRESETS = [
  {
    label: "🚨 Advance Processing Fee Trap",
    offer: "Instant Loan approved ₹50,000 without CIBIL. Pay ₹1,999 advance processing fee immediately to receive funds.",
    app_name: "QuickCash Loan",
    lang: "hi"
  },
  {
    label: "📱 Contact Scraper Loan App",
    offer: "Get ₹10,000 in 5 mins. Allow full access to phone contact list and photo gallery for instant approval.",
    app_name: "RupeePocket App",
    lang: "hinglish"
  },
  {
    label: "✅ Registered Bank Loan",
    offer: "Personal loan of ₹1,00,000 available at 11.5% APR. Apply via official SBI YONO app with Aadhaar e-KYC.",
    app_name: "SBI YONO Official",
    lang: "en"
  }
];

export default function LoanAuditor({ selectedLang }) {
  const [currentLang, setCurrentLang] = useState(selectedLang || 'hi');
  const [offerText, setOfferText] = useState(LOAN_PRESETS[0].offer);
  const [appName, setAppName] = useState(LOAN_PRESETS[0].app_name);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAudit = async (preset = null, overrideLang = null) => {
    const txt = preset ? preset.offer : offerText;
    const name = preset ? preset.app_name : appName;
    const l = overrideLang || (preset ? preset.lang : currentLang);

    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/v1/analyze/loan', {
        offer_text: txt,
        app_name: name,
        lang: l
      });
      setResult(res.data);

      try {
        const { addScanHistoryItem } = await import('../utils/scanLogger');
        addScanHistoryItem({
          name: `Loan App: ${name || 'Digital Lender'}`,
          category: 'Loan Audit',
          risk: res.data.risk_score,
          verdict: res.data.verdict,
          text: txt,
          xai: res.data.regulatory_note,
          tab: 'loan'
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
          <Shield size={22} color="#000000" />
          <h2 style={{ fontSize: '24px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000' }}>
            Predatory Loan App Auditor
          </h2>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Audits instant digital loan offers for advance fee scams, unregistered NBFCs, and illegal contact list scraping.
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
                handleAudit(null, e.target.value);
              }
            }}
          >
            {LANGUAGES.map(l => (
              <option key={l.code} value={l.code}>{l.label}</option>
            ))}
          </select>
        </div>

        {/* Presets */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
          {LOAN_PRESETS.map((p, i) => (
            <button
              key={i}
              className="btn-light"
              style={{ textAlign: 'left', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              onClick={() => {
                setOfferText(p.offer);
                setAppName(p.app_name);
                setCurrentLang(p.lang || currentLang);
                handleAudit(p, p.lang || currentLang);
              }}
            >
              <span>{p.label}</span>
              <ArrowRight size={14} color="#000000" />
            </button>
          ))}
        </div>

        {/* Inputs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
          <div>
            <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>LOAN OFFER SMS / PROMO TEXT</label>
            <textarea className="gov-input" rows={4} value={offerText} onChange={e => setOfferText(e.target.value)} />
          </div>

          <div>
            <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>DIGITAL LENDING APP NAME</label>
            <input className="gov-input" value={appName} onChange={e => setAppName(e.target.value)} />
          </div>
        </div>

        <button className="btn-black" style={{ width: '100%', justifyContent: 'center' }} onClick={() => handleAudit()} disabled={loading}>
          <FileText size={18} />
          {loading ? 'Auditing RBI Compliance...' : `Audit Loan Offer (${LANGUAGES.find(l => l.code === currentLang)?.label})`}
        </button>
      </div>

      {/* Results Panel */}
      <div className="gov-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        {result ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--border-light)' }}>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700' }}>PREDATORY RISK VERDICT</span>
                <div style={{ marginTop: '4px' }}>
                  {result.verdict === 'SCAM' && <span className="badge-scam">🚨 PREDATORY LOAN APP</span>}
                  {result.verdict === 'SUSPICIOUS' && <span className="badge-suspicious">⚠️ SUSPICIOUS OFFER</span>}
                  {result.verdict === 'SAFE' && <span className="badge-safe">✅ REGISTERED LENDER</span>}
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700' }}>RISK RATING</span>
                <div style={{ fontSize: '18px', fontWeight: '800', color: result.risk_score > 0.7 ? '#DC2626' : '#16A34A' }}>
                  {(result.risk_score * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Warning Flags */}
            <div style={{ marginBottom: '16px' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
                AUDIT WARNING FLAGS [{currentLang.toUpperCase()}]
              </span>
              {result.warning_flags && result.warning_flags.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {result.warning_flags.map((flag, idx) => (
                    <div key={idx} style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', padding: '10px 14px', borderRadius: '8px', color: '#DC2626', fontSize: '13px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <AlertTriangle size={16} />
                      {flag}
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ background: '#F0FDF4', border: '1px solid #86EFAC', padding: '10px 14px', borderRadius: '8px', color: '#16A34A', fontSize: '13px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle size={16} /> No predatory loan patterns detected.
                </div>
              )}
            </div>

            {/* RBI Regulatory Note Card */}
            <div style={{ background: '#F8FAFC', border: '1px solid var(--border-light)', padding: '16px', borderRadius: '12px' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: '#000000', display: 'block', marginBottom: '6px', letterSpacing: '0.05em' }}>
                RBI DIGITAL LENDING REGULATORY ADVISORY
              </span>
              <p style={{ fontSize: '13px', lineHeight: '1.6', color: '#0F172A', fontWeight: '500' }}>
                {result.regulatory_note}
              </p>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 0' }}>
            <Shield size={48} color="var(--text-subtle)" style={{ marginBottom: '16px' }} />
            <h3 style={{ fontSize: '18px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000', marginBottom: '8px' }}>
              Digital Loan App Auditor
            </h3>
            <p style={{ fontSize: '13px', maxWidth: '300px', margin: '0 auto' }}>
              Test loan offer SMS or app names to audit against RBI digital lending compliance guidelines.
            </p>
          </div>
        )}
      </div>

    </div>
  );
}

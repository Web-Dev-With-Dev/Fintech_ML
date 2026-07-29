import React, { useState, useEffect } from 'react';
import { PhoneCall, ShieldCheck, Send, MapPin, CheckCircle, Globe } from 'lucide-react';
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

export default function HelplineKiosk({ selectedLang }) {
  const [currentLang, setCurrentLang] = useState(selectedLang || 'hi');
  const [helplines, setHelplines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [reportText, setReportText] = useState('');
  const [reportCategory, setReportCategory] = useState('SMS_PHISHING');
  const [reportLocation, setReportLocation] = useState('Patna, Bihar');
  const [reportSubmitted, setReportSubmitted] = useState(false);

  useEffect(() => {
    const fetchHelplines = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`http://localhost:8000/api/v1/helplines?language=${currentLang}`);
        setHelplines(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchHelplines();
  }, [currentLang]);

  const handleReportSubmit = (e) => {
    e.preventDefault();
    if (!reportText.trim()) return;
    setReportSubmitted(true);
    setTimeout(() => {
      setReportSubmitted(false);
      setReportText('');
    }, 4000);
  };

  return (
    <div style={{ padding: '32px', display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
      
      {/* Helpline Directory */}
      <div className="gov-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--border-light)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <PhoneCall size={22} color="#000000" />
            <h2 style={{ fontSize: '24px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000' }}>
              Emergency Cybercrime Helpline Directory
            </h2>
          </div>

          {/* Dedicated Language Selector inside Helpline Card */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Globe size={18} color="#000000" />
            <select
              className="gov-input"
              style={{ width: 'auto', padding: '6px 12px', fontSize: '13px', fontWeight: '700', background: '#FFFFFF' }}
              value={currentLang}
              onChange={(e) => setCurrentLang(e.target.value)}
            >
              {LANGUAGES.map(l => (
                <option key={l.code} value={l.code}>{l.label}</option>
              ))}
            </select>
          </div>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
          Official government emergency helpline numbers for financial cyber fraud, bank ombudsman, and digital payments.
        </p>

        {/* Directory Grid */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {helplines.map((h, i) => (
            <div key={i} style={{ background: '#F8FAFC', border: '1px solid var(--border-light)', padding: '16px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#000000' }}>{h.name}</h3>
                  {h.available_24x7 && (
                    <span style={{ fontSize: '10px', background: '#DCFCE7', color: '#16A34A', padding: '2px 8px', borderRadius: '8px', fontWeight: '700' }}>24x7</span>
                  )}
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{h.description}</p>
              </div>

              <a
                href={`tel:${h.number}`}
                className="btn-black"
                style={{ padding: '8px 16px', background: '#DC2626', textDecoration: 'none', fontSize: '13px' }}
              >
                <PhoneCall size={14} /> Call {h.number}
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* Community Scam Reporting Kiosk */}
      <div className="gov-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <ShieldCheck size={22} color="#000000" />
          <h2 style={{ fontSize: '24px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000' }}>
            Community Scam Reporting Kiosk
          </h2>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Report newly emerging rural scam calls or fake UPI collect requests to update regional threat databases.
        </p>

        {reportSubmitted ? (
          <div style={{ background: '#F0FDF4', border: '1px solid #86EFAC', padding: '24px', borderRadius: '12px', textAlign: 'center', color: '#16A34A' }}>
            <CheckCircle size={40} style={{ marginBottom: '12px' }} />
            <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>Scam Report Submitted!</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Thank you for protecting your local community. Threat parameters logged to regional node.
            </p>
          </div>
        ) : (
          <form onSubmit={handleReportSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>SCAM CATEGORY</label>
              <select className="gov-input" value={reportCategory} onChange={e => setReportCategory(e.target.value)}>
                <option value="SMS_PHISHING">SMS & Phishing Link</option>
                <option value="UPI_COLLECT">UPI Fake Collect Request</option>
                <option value="VOICE_IMPERSONATION">Bank Officer Voice Call</option>
                <option value="PREDATORY_LOAN">Instant Loan App Fee</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>LOCATION (CITY / STATE)</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MapPin size={16} color="var(--text-muted)" />
                <input className="gov-input" value={reportLocation} onChange={e => setReportLocation(e.target.value)} />
              </div>
            </div>

            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>SCAM MESSAGE OR CALL DETAILS</label>
              <textarea className="gov-input" rows={4} value={reportText} onChange={e => setReportText(e.target.value)} placeholder="Enter phone number, scam text, or payment note..." />
            </div>

            <button type="submit" className="btn-black" style={{ width: '100%', justifyContent: 'center' }}>
              <Send size={18} /> Submit Threat Report to Regional Node
            </button>
          </form>
        )}
      </div>

    </div>
  );
}

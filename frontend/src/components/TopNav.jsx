import React from 'react';
import { Search, Bell, Globe } from 'lucide-react';

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

export default function TopNav({ selectedLang, setSelectedLang }) {
  return (
    <header className="top-nav">
      {/* Search Input Bar */}
      <div style={{ position: 'relative', width: '320px' }}>
        <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
        <input
          type="text"
          className="gov-input"
          placeholder="Search scam text, VPA, phone..."
          style={{ paddingLeft: '36px', height: '38px', borderRadius: '8px', fontSize: '13px', background: '#F8FAFC' }}
        />
        <span style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', fontSize: '10px', fontWeight: '700', color: 'var(--text-subtle)', background: '#FFFFFF', padding: '2px 6px', borderRadius: '4px', border: '1px solid var(--border-light)' }}>
          ⌘K
        </span>
      </div>

      {/* Right User Bar & Language Pill */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        
        {/* Vernacular Language Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#F8FAFC', padding: '6px 12px', borderRadius: '20px', border: '1px solid var(--border-light)' }}>
          <Globe size={15} color="var(--text-muted)" />
          <select
            value={selectedLang}
            onChange={(e) => setSelectedLang(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-main)',
              fontSize: '12px',
              fontWeight: '600',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {LANGUAGES.map(l => (
              <option key={l.code} value={l.code}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        {/* Bell Icon */}
        <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}>
          <Bell size={18} />
        </button>

        {/* User Profile Avatar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', borderLeft: '1px solid var(--border-light)', paddingLeft: '16px' }}>
          <div style={{ width: '34px', height: '34px', borderRadius: '50%', background: '#F1F5F9', border: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '12px', color: '#0F172A' }}>
            JD
          </div>
          <div style={{ fontSize: '13px', lineHeight: '1.2' }}>
            <div style={{ fontWeight: '700', color: '#000000' }}>John Doe</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Cyber Safety Officer</div>
          </div>
        </div>

      </div>
    </header>
  );
}

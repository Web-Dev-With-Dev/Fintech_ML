import React, { useState, useEffect } from 'react';
import { Shield, Activity, Globe, Zap } from 'lucide-react';
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

export default function Header({ activeTab, setActiveTab, selectedLang, setSelectedLang }) {
  const [health, setHealth] = useState({ status: 'checking', modelsLoaded: false });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/v1/health');
        setHealth({ status: 'healthy', modelsLoaded: res.data.models_loaded });
      } catch (err) {
        setHealth({ status: 'offline', modelsLoaded: false });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'sms', label: 'SMS & Phishing', icon: Shield },
    { id: 'upi', label: 'UPI Mule Network', icon: Zap },
    { id: 'voice', label: 'Voice Interceptor', icon: Activity },
    { id: 'loan', label: 'Loan Auditor', icon: Shield },
    { id: 'panic', label: 'Panic Shield', icon: Activity },
    { id: 'fl', label: 'Federated AI Map', icon: Globe },
    { id: 'helpline', label: 'Helpline Kiosk', icon: Shield }
  ];

  return (
    <header className="glass-card" style={{ margin: '16px 24px 0 24px', padding: '16px 24px', borderBottom: '1px solid var(--border-glass)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-cyan))',
            padding: '10px',
            borderRadius: '12px',
            boxShadow: '0 0 15px rgba(99, 102, 241, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Shield size={26} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '22px', fontWeight: '800', background: 'linear-gradient(90deg, #FFFFFF, #94A3B8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                FinShield AI
              </h1>
              <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.2)', color: 'var(--accent-primary)', fontWeight: '700', border: '1px solid rgba(99, 102, 241, 0.4)' }}>
                RURAL EDITION
              </span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Multi-Modal Privacy-Preserving Financial Scam Shield
            </p>
          </div>
        </div>

        {/* System Health & Language Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          
          {/* API Health Pill */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 14px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: '600',
            background: health.status === 'healthy' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
            border: `1px solid ${health.status === 'healthy' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            color: health.status === 'healthy' ? 'var(--status-safe)' : 'var(--status-scam)'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: health.status === 'healthy' ? 'var(--status-safe)' : 'var(--status-scam)',
              boxShadow: health.status === 'healthy' ? '0 0 8px var(--status-safe)' : '0 0 8px var(--status-scam)'
            }} />
            {health.status === 'healthy' ? 'ML Engine Online' : 'Backend Offline'}
          </div>

          {/* Language Selector Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(15, 23, 42, 0.6)', padding: '6px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
            <Globe size={16} color="var(--accent-cyan)" />
            <select
              value={selectedLang}
              onChange={(e) => setSelectedLang(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-main)',
                fontSize: '13px',
                fontWeight: '600',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {LANGUAGES.map(l => (
                <option key={l.code} value={l.code} style={{ background: '#0F172A', color: '#F8FAFC' }}>
                  {l.label}
                </option>
              ))}
            </select>
          </div>

        </div>

      </div>

      {/* Navigation Tabs */}
      <nav style={{ display: 'flex', gap: '8px', marginTop: '18px', overflowX: 'auto', paddingBottom: '4px' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '600',
                whiteSpace: 'nowrap',
                transition: 'all 0.2s ease',
                background: isActive ? 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))' : 'rgba(255, 255, 255, 0.04)',
                color: isActive ? '#FFFFFF' : 'var(--text-muted)',
                boxShadow: isActive ? '0 4px 15px rgba(99, 102, 241, 0.35)' : 'none'
              }}
            >
              <Icon size={16} />
              {item.label}
            </button>
          );
        })}
      </nav>

    </header>
  );
}

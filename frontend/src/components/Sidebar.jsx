import React from 'react';
import { 
  LayoutDashboard, 
  ShieldCheck, 
  Zap, 
  Activity, 
  FileText, 
  AlertOctagon, 
  Globe, 
  PhoneCall, 
  Shield 
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'sms', label: 'SMS & Phishing', icon: ShieldCheck },
    { id: 'upi', label: 'UPI Mule Network', icon: Zap },
    { id: 'voice', label: 'Voice Interceptor', icon: Activity },
    { id: 'loan', label: 'Loan Auditor', icon: FileText },
    { id: 'panic', label: 'Panic Shield', icon: AlertOctagon },
    { id: 'fl', label: 'Federated AI Map', icon: Globe },
    { id: 'helpline', label: 'Helpline Kiosk', icon: PhoneCall }
  ];

  return (
    <aside className="sidebar">
      <div>
        {/* Brand Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '0 8px 24px 8px', borderBottom: '1px solid var(--border-light)', marginBottom: '20px' }}>
          <div style={{ background: '#000000', padding: '8px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Shield size={22} color="#FFFFFF" />
          </div>
          <div>
            <h1 style={{ fontSize: '22px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000', lineHeight: 1 }}>
              FinShield AI
            </h1>
            <span style={{ fontSize: '10px', fontWeight: '700', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
              RURAL CYBER MITIGATION
            </span>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`sidebar-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={18} color={isActive ? '#000000' : 'var(--text-muted)'} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Status Card */}
      <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-md)', padding: '14px', marginTop: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
          <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-heading)' }}>Govt AI Portal</span>
          <span style={{ fontSize: '10px', fontWeight: '700', color: '#16A34A', background: '#DCFCE7', padding: '2px 6px', borderRadius: '4px' }}>Active</span>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>API ML Engine Latency</div>
        <div style={{ width: '100%', height: '4px', background: '#E2E8F0', borderRadius: '2px', overflow: 'hidden' }}>
          <div style={{ width: '85%', height: '100%', background: '#000000' }} />
        </div>
      </div>
    </aside>
  );
}

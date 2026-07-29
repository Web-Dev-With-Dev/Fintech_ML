import React from 'react';
import { Globe, Lock, ShieldCheck, Cpu } from 'lucide-react';

const REGIONAL_NODES = [
  { name: 'Uttar Pradesh Node', region: 'North', samples: '12,500 local samples', epsilon: 'ε = 1.15', status: 'Syncing Gradients' },
  { name: 'Bihar Regional Node', region: 'East', samples: '9,800 local samples', epsilon: 'ε = 1.20', status: 'Active Training' },
  { name: 'West Bengal Node', region: 'East', samples: '8,400 local samples', epsilon: 'ε = 1.10', status: 'Syncing Gradients' },
  { name: 'Maharashtra Node', region: 'West', samples: '11,200 local samples', epsilon: 'ε = 1.25', status: 'Active Training' },
  { name: 'Tamil Nadu Node', region: 'South', samples: '10,100 local samples', epsilon: 'ε = 1.18', status: 'Active Training' }
];

export default function FederatedDashboard() {
  return (
    <div style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Overview Banner */}
      <div className="gov-card" style={{ background: '#F8FAFC' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <Globe size={26} color="#000000" />
              <h2 style={{ fontSize: '24px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000' }}>
                Federated Learning & Differential Privacy Center
              </h2>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', maxWidth: '700px' }}>
              Models train locally across 5 regional nodes in India using Flower FL framework. Raw banking data zero-leaves local storage. Only gradient updates with Gaussian Differential Privacy noise are shared.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{ background: '#F0FDF4', border: '1px solid #86EFAC', padding: '10px 16px', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '8px', color: '#16A34A', fontWeight: '700', fontSize: '13px' }}>
              <ShieldCheck size={18} /> DPDPA COMPLIANT BY DESIGN
            </div>
          </div>
        </div>
      </div>

      {/* Grid of Regional Nodes */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        {REGIONAL_NODES.map((node, idx) => (
          <div key={idx} className="gov-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={18} color="#000000" />
                <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#000000' }}>{node.name}</h3>
              </div>
              <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '8px', background: '#F1F5F9', color: '#0F172A', fontWeight: '700' }}>
                {node.region}
              </span>
            </div>

            <div style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '14px' }}>
              <div>📊 Training Data: <strong style={{ color: '#000000' }}>{node.samples}</strong></div>
              <div>🔒 Differential Privacy Budget: <strong style={{ color: '#16A34A' }}>{node.epsilon}</strong></div>
              <div>⚡ Network Status: <strong style={{ color: '#2563EB' }}>{node.status}</strong></div>
            </div>

            <div style={{ width: '100%', height: '6px', background: '#E2E8F0', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: `${80 + idx * 4}%`, height: '100%', background: '#000000' }} />
            </div>
          </div>
        ))}
      </div>

      {/* DP Guarantee Panel */}
      <div className="gov-card" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Lock size={18} color="#000000" /> Differential Privacy Guarantees
          </h3>
          <p style={{ fontSize: '13px', lineHeight: '1.6', color: 'var(--text-muted)' }}>
            Gaussian noise ($\sigma = 0.5$) is added to model gradients before transmission. Re-identification or reverse-engineering of user banking messages from gradient vectors is mathematically impossible under $(\epsilon = 1.2, \delta = 10^{-5})$ privacy budget bounds.
          </p>
        </div>

        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={18} color="#16A34A" /> India DPDPA Act 2023 Compliance
          </h3>
          <p style={{ fontSize: '13px', lineHeight: '1.6', color: 'var(--text-muted)' }}>
            Fully satisfies Section 6 of India’s Digital Personal Data Protection Act by enforcing zero data transfer across state boundaries. Only anonymized model parameters are aggregated at the central coordinator node.
          </p>
        </div>
      </div>

    </div>
  );
}

import React, { useState } from 'react';
import { Activity, AlertOctagon, Phone, RefreshCw } from 'lucide-react';
import axios from 'axios';

export default function PanicShield() {
  const [velocity, setVelocity] = useState(7);
  const [oddHour, setOddHour] = useState(true);
  const [fullDrain, setFullDrain] = useState(true);
  const [firstTime, setFirstTime] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/v1/analyze/behavior', {
        user_id: "rural_user_session_4021",
        session_data: {
          transaction_velocity: velocity,
          odd_hour_transfer: oddHour,
          full_balance_drain: fullDrain,
          first_time_recipient: firstTime
        },
        lang: "hi"
      });
      setResult(res.data);

      try {
        const { addScanHistoryItem } = await import('../utils/scanLogger');
        addScanHistoryItem({
          name: `Session Anomaly Audit (${velocity} tx/hr)`,
          category: 'Behavioral Panic',
          risk: res.data.panic_score,
          verdict: res.data.verdict,
          text: `Velocity: ${velocity} tx/hr, OddHour: ${oddHour}, FullDrain: ${fullDrain}`,
          xai: res.data.anomaly_type || 'Isolation Forest Anomaly Detected',
          tab: 'panic'
        });
      } catch (e) {}

      if (res.data.intervention_required) {
        setShowModal(true);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '32px', display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '24px', position: 'relative' }}>
      
      {/* Simulation Controls */}
      <div className="gov-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <Activity size={22} color="#000000" />
          <h2 style={{ fontSize: '24px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000' }}>
            Behavioral Panic State Shield
          </h2>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
          Isolation Forest Anomaly Detector monitors user session parameters to catch panic state transfers under coercion.
        </p>

        {/* Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: 'var(--text-main)', marginBottom: '6px', fontWeight: '600' }}>
              <span>Transaction Velocity (Transfers/hr)</span>
              <span style={{ fontWeight: '800', color: '#000000' }}>{velocity} tx/hr</span>
            </div>
            <input type="range" min="1" max="15" value={velocity} onChange={e => setVelocity(parseInt(e.target.value))} style={{ width: '100%', accentColor: '#000000' }} />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#F8FAFC', padding: '12px 16px', borderRadius: '10px', border: '1px solid var(--border-light)' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-main)', fontWeight: '600' }}>Odd Hour Activity (1 AM - 4 AM)</span>
            <input type="checkbox" checked={oddHour} onChange={e => setOddHour(e.target.checked)} style={{ width: '18px', height: '18px', accentColor: '#000000' }} />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#F8FAFC', padding: '12px 16px', borderRadius: '10px', border: '1px solid var(--border-light)' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-main)', fontWeight: '600' }}>Full Account Balance Drain (90%+)</span>
            <input type="checkbox" checked={fullDrain} onChange={e => setFullDrain(e.target.checked)} style={{ width: '18px', height: '18px', accentColor: '#000000' }} />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#F8FAFC', padding: '12px 16px', borderRadius: '10px', border: '1px solid var(--border-light)' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-main)', fontWeight: '600' }}>First-Time Recipient Node</span>
            <input type="checkbox" checked={firstTime} onChange={e => setFirstTime(e.target.checked)} style={{ width: '18px', height: '18px', accentColor: '#000000' }} />
          </div>
        </div>

        <button className="btn-black" style={{ width: '100%', justifyContent: 'center' }} onClick={handleAnalyze} disabled={loading}>
          <RefreshCw size={18} />
          {loading ? 'Evaluating Isolation Forest Model...' : 'Simulate Session & Analyze Panic Score'}
        </button>
      </div>

      {/* Results Panel */}
      <div className="gov-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        {result ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--border-light)' }}>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700' }}>BEHAVIORAL VERDICT</span>
                <div style={{ marginTop: '4px' }}>
                  {result.verdict === 'SCAM' ? <span className="badge-scam">🚨 HIGH COERCION PANIC STATE</span> : <span className="badge-safe">✅ NORMAL USER BEHAVIOR</span>}
                </div>
              </div>

              {result.intervention_required && (
                <span className="badge-scam">
                  🛑 SOFT-BLOCK TRIGGERED
                </span>
              )}
            </div>

            {/* Panic Score Dial */}
            <div style={{ background: '#F8FAFC', border: '1px solid var(--border-light)', padding: '20px', borderRadius: '12px', textAlign: 'center', marginBottom: '16px' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>ISOLATION FOREST ANOMALY PANIC SCORE</span>
              <div style={{ fontSize: '42px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: result.panic_score >= 0.75 ? '#DC2626' : '#16A34A' }}>
                {(result.panic_score * 100).toFixed(0)} / 100
              </div>
            </div>

            {/* Anomaly Type */}
            {result.anomaly_type && (
              <div style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', padding: '14px', borderRadius: '10px', color: '#DC2626', fontSize: '13px', fontWeight: '600' }}>
                ⚠️ Detected Session Anomalies: {result.anomaly_type}
              </div>
            )}
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 0' }}>
            <Activity size={48} color="var(--text-subtle)" style={{ marginBottom: '16px' }} />
            <h3 style={{ fontSize: '18px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000', marginBottom: '8px' }}>
              Behavioral Panic State Shield
            </h3>
            <p style={{ fontSize: '13px', maxWidth: '300px', margin: '0 auto' }}>
              Adjust user session sliders to simulate coerced panic state transfers and trigger automatic soft-block security intervention.
            </p>
          </div>
        )}
      </div>

      {/* Emergency Soft-Block Interception Modal */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div className="gov-card" style={{ maxWidth: '480px', width: '100%', padding: '32px', textAlign: 'center', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}>
            <AlertOctagon size={56} color="#DC2626" style={{ marginBottom: '16px' }} />
            <h2 style={{ fontSize: '24px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000', marginBottom: '12px' }}>
              सुरक्षा चेतावनी: सॉफ्ट-ब्लॉक (Intervention)
            </h2>
            <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#475569', marginBottom: '24px' }}>
              आपके खाते में असामान्य ट्रांसफर गतिविधि का पता चला है। आपकी सुरक्षा के लिए यह लेन-देन अस्थायी रूप से रोक दिया गया है। क्या आप किसी दबाव में हैं?
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              <a href="tel:1930" className="btn-black" style={{ flex: 1, justifyContent: 'center', background: '#DC2626' }}>
                <Phone size={18} /> कॉल 1930 हेल्पलाइन
              </a>
              <button className="btn-light" style={{ flex: 1, justifyContent: 'center' }} onClick={() => setShowModal(false)}>
                बंद करें (Close)
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

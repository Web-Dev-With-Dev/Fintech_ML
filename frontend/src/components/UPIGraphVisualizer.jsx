import React, { useState } from 'react';
import axios from 'axios';

const PRESET_TXS = [
  {
    label: "🚨 Money Mule Chain Ring",
    sender: "victim_user@upi",
    receiver: "mule_temp_chain@upi",
    amount: 45000.0,
    note: "Pay immediately for lottery processing fee"
  },
  {
    label: "💸 Cashback PIN Collect Trap",
    sender: "rural_farmer@okaxis",
    receiver: "claim_reward_bonus@upi",
    amount: 4999.0,
    note: "Enter UPI PIN to receive 4999 cashback reward"
  },
  {
    label: "💀 Cyber Extortion Threat",
    sender: "priya_sharma@icici",
    receiver: "rahul_verma@okaxis",
    amount: 25000.0,
    note: "II am hackaer , your money will goene YEss........."
  },
  {
    label: "🛒 Safe Merchant Payment",
    sender: "ramesh@paytm",
    receiver: "kiranastore@ybl",
    amount: 350.0,
    note: "Grocery items payment"
  }
];

export default function UPIGraphVisualizer() {
  const [sender, setSender] = useState(PRESET_TXS[0].sender);
  const [receiver, setReceiver] = useState(PRESET_TXS[0].receiver);
  const [amount, setAmount] = useState(PRESET_TXS[0].amount);
  const [note, setNote] = useState(PRESET_TXS[0].note);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async (preset = null) => {
    const s = preset ? preset.sender : sender;
    const r = preset ? preset.receiver : receiver;
    const a = preset ? preset.amount : amount;
    const n = preset ? preset.note : note;

    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/v1/analyze/upi', {
        sender_id: s,
        receiver_id: r,
        amount: parseFloat(a),
        timestamp: new Date().toISOString(),
        message_text: n
      });
      setResult(res.data);

      try {
        const { addScanHistoryItem } = await import('../utils/scanLogger');
        addScanHistoryItem({
          name: `UPI Transfer to ${r}`,
          category: 'UPI Mule GAT',
          risk: res.data.risk_score,
          verdict: res.data.verdict,
          text: `Sender: ${s}, Receiver: ${r}, Amount: ₹${a}, Note: ${n}`,
          xai: `GAT Graph Risk: ${(res.data.graph_risk_score * 100).toFixed(0)}% • Fraud: ${res.data.fraud_type || 'MULE'}`,
          tab: 'upi'
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
      
            <div className="gov-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          
          <h2 style={{ fontSize: '24px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000' }}>
            UPI Money Mule & Network Inspector
          </h2>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Graph Attention Neural Network (GAT) evaluates money mule chain routing, star topologies, and fake collect traps.
        </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
          {PRESET_TXS.map((p, i) => (
            <button
              key={i}
              className="btn-light"
              style={{ textAlign: 'left', justifyContent: 'space-between', display: 'flex', alignItems: 'center' }}
              onClick={() => {
                setSender(p.sender);
                setReceiver(p.receiver);
                setAmount(p.amount);
                setNote(p.note);
                handleAnalyze(p);
              }}
            >
              <span>{p.label}</span>
              
            </button>
          ))}
        </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
          <div>
            <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>SENDER VPA</label>
            <input className="gov-input" value={sender} onChange={e => setSender(e.target.value)} />
          </div>

          <div>
            <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>RECEIVER VPA (TARGET NODE)</label>
            <input className="gov-input" value={receiver} onChange={e => setReceiver(e.target.value)} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>AMOUNT (₹)</label>
              <input type="number" className="gov-input" value={amount} onChange={e => setAmount(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: '700' }}>TRANSACTION NOTE</label>
              <input className="gov-input" value={note} onChange={e => setNote(e.target.value)} />
            </div>
          </div>
        </div>

        <button className="btn-black" style={{ width: '100%', justifyContent: 'center' }} onClick={() => handleAnalyze()} disabled={loading}>
          
          {loading ? 'Evaluating Network Topology...' : 'Run GAT Graph Network Inspection'}
        </button>

      </div>

            <div className="gov-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        
        {result ? (
          <div>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--border-light)' }}>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700' }}>GAT VERDICT</span>
                <div style={{ marginTop: '4px' }}>
                  {result.verdict === 'SCAM' && <span className="badge-scam">🚨 HIGH GRAPH RISK</span>}
                  {result.verdict === 'SUSPICIOUS' && <span className="badge-suspicious">⚠️ SUSPICIOUS NETWORK</span>}
                  {result.verdict === 'SAFE' && <span className="badge-safe">✅ LEGITIMATE TRANSFER</span>}
                </div>
              </div>

              {result.ring_id && (
                <div style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', padding: '6px 12px', borderRadius: '8px', textAlign: 'right' }}>
                  <span style={{ fontSize: '10px', color: '#DC2626', display: 'block', fontWeight: '700' }}>MONEY MULE RING ID</span>
                  <span style={{ fontSize: '13px', fontWeight: '800', color: '#000000' }}>{result.ring_id}</span>
                </div>
              )}
            </div>

                        <div style={{ background: '#F8FAFC', border: '1px solid var(--border-light)', borderRadius: '12px', padding: '20px', marginBottom: '16px', position: 'relative' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: '#000000', display: 'block', marginBottom: '12px', letterSpacing: '0.05em' }}>
                GRAPH ATTENTION NETWORK TOPOLOGY VISUALIZER
              </span>

              <svg width="100%" height="160" viewBox="0 0 400 160" style={{ overflow: 'visible' }}>
                                <line x1="60" y1="80" x2="200" y2="80" stroke={result.mule_chain_detected ? '#DC2626' : '#2563EB'} strokeWidth="3" strokeDasharray={result.mule_chain_detected ? "4 4" : "none"} />
                <line x1="200" y1="80" x2="340" y2="80" stroke={result.mule_chain_detected ? '#DC2626' : '#16A34A'} strokeWidth="3" />
                <line x1="200" y1="80" x2="200" y2="20" stroke={result.mule_chain_detected ? '#D97706' : 'transparent'} strokeWidth="2" />
                <line x1="200" y1="80" x2="200" y2="140" stroke={result.mule_chain_detected ? '#D97706' : 'transparent'} strokeWidth="2" />

                                <circle cx="60" cy="80" r="22" fill="#FFFFFF" stroke="#2563EB" strokeWidth="3" />
                <text x="60" y="85" textAnchor="middle" fill="#000000" fontSize="10" fontWeight="bold">SENDER</text>

                                <circle cx="200" cy="80" r="26" fill={result.mule_chain_detected ? "#DC2626" : "#16A34A"} stroke="#FFFFFF" strokeWidth="3" />
                <text x="200" y="84" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="bold">{result.mule_chain_detected ? "MULE" : "TARGET"}</text>

                                <circle cx="340" cy="80" r="22" fill="#FFFFFF" stroke={result.mule_chain_detected ? "#DC2626" : "#16A34A"} strokeWidth="3" />
                <text x="340" y="85" textAnchor="middle" fill="#000000" fontSize="10" fontWeight="bold">RECV</text>

                                {result.mule_chain_detected && (
                  <>
                    <circle cx="200" cy="20" r="12" fill="#D97706" />
                    <circle cx="200" cy="140" r="12" fill="#D97706" />
                  </>
                )}
              </svg>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px', fontWeight: '600' }}>
                <span>Origin: {sender.substring(0, 14)}</span>
                <span>Target: {receiver.substring(0, 14)}</span>
              </div>
            </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
              <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', display: 'block', fontWeight: '700' }}>RISK SCORE</span>
                <span style={{ fontSize: '18px', fontWeight: '800', color: result.risk_score > 0.7 ? '#DC2626' : '#16A34A' }}>{(result.risk_score * 100).toFixed(0)}%</span>
              </div>
              <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', display: 'block', fontWeight: '700' }}>GAT GRAPH RISK</span>
                <span style={{ fontSize: '18px', fontWeight: '800', color: '#2563EB' }}>{(result.graph_risk_score * 100).toFixed(0)}%</span>
              </div>
              <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', display: 'block', fontWeight: '700' }}>FRAUD TYPE</span>
                <span style={{ fontSize: '11px', fontWeight: '700', color: '#000000' }}>{result.fraud_type || 'NONE'}</span>
              </div>
            </div>

          </div>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 0' }}>
            
            <h3 style={{ fontSize: '18px', fontWeight: '400', fontFamily: 'var(--font-serif)', color: '#000000', marginBottom: '8px' }}>
              Awaiting UPI Transaction
            </h3>
            <p style={{ fontSize: '13px', maxWidth: '300px', margin: '0 auto' }}>
              Submit a transaction on the left or tap a money mule preset to view Graph Neural Network node analysis.
            </p>
          </div>
        )}

      </div>

    </div>
  );
}
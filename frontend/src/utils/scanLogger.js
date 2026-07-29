const STORAGE_KEY = 'finshield_scan_history';

export const getScanHistory = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    return [];
  }
};

export const addScanHistoryItem = (item) => {
  const history = getScanHistory();
  const newItem = {
    id: Date.now(),
    name: item.name || `${item.category} Session #${history.length + 1}`,
    category: item.category,
    risk: typeof item.risk === 'number' ? item.risk : 0.85,
    verdict: item.verdict || 'SCAM',
    date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }),
    text: item.text || 'Payload Data',
    xai: item.xai || 'ML Scan Completed',
    tab: item.tab || 'sms'
  };
  const updated = [newItem, ...history];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  return updated;
};

export const clearScanHistory = () => {
  localStorage.removeItem(STORAGE_KEY);
  return [];
};
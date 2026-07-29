import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Overview from './components/Overview';
import SMSScanner from './components/SMSScanner';
import UPIGraphVisualizer from './components/UPIGraphVisualizer';
import VoiceStudio from './components/VoiceStudio';
import LoanAuditor from './components/LoanAuditor';
import PanicShield from './components/PanicShield';
import FederatedDashboard from './components/FederatedDashboard';
import HelplineKiosk from './components/HelplineKiosk';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedLang, setSelectedLang] = useState('hi');

  return (
    <div className="app-container">
      
      {/* Fixed Left Vertical Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="main-content">
        
        {/* Dynamic Page Views */}
        <main style={{ flex: 1 }}>
          {activeTab === 'overview' && <Overview setActiveTab={setActiveTab} />}
          {activeTab === 'sms' && <SMSScanner selectedLang={selectedLang} />}
          {activeTab === 'upi' && <UPIGraphVisualizer selectedLang={selectedLang} />}
          {activeTab === 'voice' && <VoiceStudio selectedLang={selectedLang} />}
          {activeTab === 'loan' && <LoanAuditor selectedLang={selectedLang} />}
          {activeTab === 'panic' && <PanicShield selectedLang={selectedLang} />}
          {activeTab === 'fl' && <FederatedDashboard selectedLang={selectedLang} />}
          {activeTab === 'helpline' && <HelplineKiosk selectedLang={selectedLang} />}
        </main>

      </div>

    </div>
  );
}

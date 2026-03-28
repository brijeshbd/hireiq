import { useState } from 'react';
import Chat from './components/Chat';
import ResumeAnalyzer from './components/ResumeAnalyzer';
import JDAnalyzer from './components/JDAnalyzer';
import CoverLetter from './components/CoverLetter';
import Interview from './components/Interview';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  const tabs = [
    { id: 'chat',     label: '💬 Chat',            component: <Chat /> },
    { id: 'resume',   label: '📄 Resume Analyzer',  component: <ResumeAnalyzer /> },
    { id: 'jd',       label: '🔍 JD Analyzer',      component: <JDAnalyzer /> },
    { id: 'cover',    label: '✍️ Cover Letter',      component: <CoverLetter /> },
    { id: 'interview',label: '🎤 Mock Interview',    component: <Interview /> },
  ];

  return (
    <div className="app">
      {/* SIDEBAR */}
      <div className="sidebar">
        <div className="logo">
          <h1>🤖 HireIQ</h1>
          <p>AI Job Assistant</p>
        </div>
        <nav>
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`nav-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <p>Built by Brijesh 🚀</p>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="main">
        {tabs.find(t => t.id === activeTab)?.component}
      </div>
    </div>
  );
}

export default App;
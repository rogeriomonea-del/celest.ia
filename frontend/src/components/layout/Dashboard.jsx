import React from 'react'
import '../../styles/Dashboard.css'

function Dashboard({ children, activeTab, onTabChange }) {
  const tabs = [
    { id: 'search', label: '✈️ Search Flights', icon: '🔍' },
    { id: 'analysis', label: '📊 Analysis', icon: '📈' },
    { id: 'trends', label: '📈 Trends', icon: '📊' },
    { id: 'settings', label: '⚙️ Settings', icon: '🔧' }
  ]

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <h2>🌟 Celes.ia</h2>
        </div>
        <ul className="nav-tabs">
          {tabs.map(tab => (
            <li key={tab.id}>
              <button
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => onTabChange(tab.id)}
              >
                <span className="tab-icon">{tab.icon}</span>
                <span className="tab-label">{tab.label}</span>
              </button>
            </li>
          ))}
        </ul>
        <div className="nav-status">
          <span className="status-indicator online"></span>
          <span>AI System Online</span>
        </div>
      </nav>
      
      <div className="dashboard-content">
        {children}
      </div>
      
      <footer className="dashboard-footer">
        <p>© 2024 Celes.ia - AI-Powered Travel Intelligence</p>
        <div className="footer-links">
          <a href="/docs">API Docs</a>
          <a href="/telegram">Telegram Bot</a>
          <a href="/about">About</a>
        </div>
      </footer>
    </div>
  )
}

export default Dashboard

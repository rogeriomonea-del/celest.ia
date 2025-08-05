import React, { useState, useEffect } from 'react'
import FlightSearch from './components/search/FlightSearch'
import PriceChart from './components/charts/PriceChart'
import MilhasChart from './components/charts/MilhasChart'
import Dashboard from './components/layout/Dashboard'
import { searchFlights, getPriceTrends } from './services/api'
import './styles/globals.css'
import './styles/App.css'

function App() {
  const [flightResults, setFlightResults] = useState([])
  const [priceData, setPriceData] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('search')

  const handleFlightSearch = async (searchParams) => {
    setLoading(true)
    try {
      const results = await searchFlights(searchParams)
      setFlightResults(results.flights || [])
      
      // Also fetch price trends for the route
      const trends = await getPriceTrends(searchParams.origin, searchParams.destination)
      setPriceData(trends.historical_data || [])
    } catch (error) {
      console.error('Flight search failed:', error)
      setFlightResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dashboard activeTab={activeTab} onTabChange={setActiveTab}>
      <div className="celes-app">
        <header className="app-header">
          <h1>🛩️ Celes.ia Dashboard</h1>
          <p>AI-powered flight search and analysis platform</p>
        </header>

        <main className="app-main">
          {activeTab === 'search' && (
            <div className="search-section">
              <FlightSearch 
                onSearch={handleFlightSearch} 
                loading={loading}
                results={flightResults}
              />
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="analysis-section">
              <h2>Price Analysis</h2>
              <div className="charts-container">
                <div className="chart-item">
                  <PriceChart data={priceData} />
                </div>
                <div className="chart-item">
                  <MilhasChart />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'trends' && (
            <div className="trends-section">
              <h2>Market Trends</h2>
              <div className="trends-content">
                <div className="trend-card">
                  <h3>Popular Routes</h3>
                  <ul>
                    <li>GRU → PTY (São Paulo → Panama City)</li>
                    <li>GIG → JFK (Rio → New York)</li>
                    <li>BSB → LAX (Brasília → Los Angeles)</li>
                  </ul>
                </div>
                <div className="trend-card">
                  <h3>Best Booking Times</h3>
                  <p>✈️ Domestic flights: 2-3 weeks in advance</p>
                  <p>🌍 International flights: 6-8 weeks in advance</p>
                  <p>💡 Tuesday and Wednesday typically offer best prices</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="settings-section">
              <h2>Settings</h2>
              <div className="settings-content">
                <div className="setting-group">
                  <h3>Preferences</h3>
                  <label>
                    Currency:
                    <select defaultValue="USD">
                      <option value="USD">USD ($)</option>
                      <option value="BRL">BRL (R$)</option>
                      <option value="EUR">EUR (€)</option>
                    </select>
                  </label>
                  <label>
                    <input type="checkbox" defaultChecked />
                    Enable price alerts
                  </label>
                  <label>
                    <input type="checkbox" defaultChecked />
                    AI recommendations
                  </label>
                </div>
                <div className="setting-group">
                  <h3>Notifications</h3>
                  <label>
                    <input type="checkbox" defaultChecked />
                    Email notifications
                  </label>
                  <label>
                    <input type="checkbox" defaultChecked />
                    Telegram notifications
                  </label>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </Dashboard>
  )
}

export default App

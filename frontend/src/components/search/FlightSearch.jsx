import React, { useState } from 'react'
import '../../styles/FlightSearch.css'

function FlightSearch({ onSearch, loading, results }) {
  const [searchParams, setSearchParams] = useState({
    origin: '',
    destination: '',
    departureDate: '',
    returnDate: '',
    passengers: 1
  })

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (searchParams.origin && searchParams.destination && searchParams.departureDate) {
      onSearch({
        origin: searchParams.origin.toUpperCase(),
        destination: searchParams.destination.toUpperCase(),
        departure_date: searchParams.departureDate,
        return_date: searchParams.returnDate || null,
        passengers: parseInt(searchParams.passengers)
      })
    }
  }

  const formatPrice = (price, currency = 'USD') => {
    if (currency === 'BRL') return `R$ ${price.toFixed(2)}`
    if (currency === 'EUR') return `€ ${price.toFixed(2)}`
    return `$ ${price.toFixed(2)}`
  }

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A'
    try {
      const date = new Date(timeString)
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      })
    } catch {
      return timeString
    }
  }

  return (
    <div className="flight-search">
      <div className="search-form">
        <h2>🔍 Search Flights</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="origin">From</label>
              <input
                type="text"
                id="origin"
                name="origin"
                value={searchParams.origin}
                onChange={handleInputChange}
                placeholder="GRU"
                maxLength="3"
                required
              />
              <small>Airport code (e.g., GRU, JFK)</small>
            </div>
            
            <div className="form-group">
              <label htmlFor="destination">To</label>
              <input
                type="text"
                id="destination"
                name="destination"
                value={searchParams.destination}
                onChange={handleInputChange}
                placeholder="PTY"
                maxLength="3"
                required
              />
              <small>Airport code (e.g., PTY, LAX)</small>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="departureDate">Departure</label>
              <input
                type="date"
                id="departureDate"
                name="departureDate"
                value={searchParams.departureDate}
                onChange={handleInputChange}
                min={new Date().toISOString().split('T')[0]}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="returnDate">Return (optional)</label>
              <input
                type="date"
                id="returnDate"
                name="returnDate"
                value={searchParams.returnDate}
                onChange={handleInputChange}
                min={searchParams.departureDate}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="passengers">Passengers</label>
              <select
                id="passengers"
                name="passengers"
                value={searchParams.passengers}
                onChange={handleInputChange}
              >
                {[1,2,3,4,5,6,7,8,9].map(num => (
                  <option key={num} value={num}>{num}</option>
                ))}
              </select>
            </div>
          </div>

          <button 
            type="submit" 
            className="search-button"
            disabled={loading}
          >
            {loading ? '🔄 Searching...' : '🚀 Search Flights'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>🤖 AI is analyzing flights across multiple sources...</p>
        </div>
      )}

      {results && results.length > 0 && (
        <div className="search-results">
          <h3>✈️ Found {results.length} flights</h3>
          <div className="results-grid">
            {results.map((flight, index) => (
              <div key={index} className="flight-card">
                <div className="flight-header">
                  <span className="airline">{flight.airline}</span>
                  <span className="flight-number">{flight.flight_number}</span>
                  {flight.ai_score && (
                    <span className="ai-score">
                      🤖 Score: {(flight.ai_score).toFixed(1)}/100
                    </span>
                  )}
                </div>
                
                <div className="flight-route">
                  <div className="route-info">
                    <span className="time">{formatTime(flight.departure_time)}</span>
                    <span className="airport">{flight.origin}</span>
                  </div>
                  <div className="route-line">
                    {flight.stops > 0 ? (
                      <span className="stops">✈️ {flight.stops} stop{flight.stops > 1 ? 's' : ''}</span>
                    ) : (
                      <span className="direct">✈️ Direct</span>
                    )}
                  </div>
                  <div className="route-info">
                    <span className="time">{formatTime(flight.arrival_time)}</span>
                    <span className="airport">{flight.destination}</span>
                  </div>
                </div>
                
                <div className="flight-details">
                  <div className="price">
                    <span className="amount">{formatPrice(flight.price, flight.currency)}</span>
                    <span className="currency">{flight.currency}</span>
                  </div>
                  
                  {flight.duration_minutes && (
                    <div className="duration">
                      ⏱️ {Math.floor(flight.duration_minutes / 60)}h {flight.duration_minutes % 60}m
                    </div>
                  )}
                </div>
                
                {flight.recommendations && flight.recommendations.length > 0 && (
                  <div className="ai-recommendations">
                    <strong>💡 AI Insights:</strong>
                    <ul>
                      {flight.recommendations.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="flight-actions">
                  <button className="btn-primary">
                    📘 Book Now
                  </button>
                  <button className="btn-secondary">
                    📊 Price History
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {results && results.length === 0 && !loading && (
        <div className="no-results">
          <p>😔 No flights found for your search criteria.</p>
          <p>Try adjusting your dates or destinations.</p>
        </div>
      )}
    </div>
  )
}

export default FlightSearch

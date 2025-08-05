import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import '../../styles/PriceChart.css'

function PriceChart({ data = [] }) {
  // If no data provided, use sample data
  const chartData = data.length > 0 ? data : [
    { date: '2024-01-01', price: 450, airline: 'Copa' },
    { date: '2024-01-05', price: 420, airline: 'LATAM' },
    { date: '2024-01-10', price: 480, airline: 'Copa' },
    { date: '2024-01-15', price: 410, airline: 'Azul' },
    { date: '2024-01-20', price: 440, airline: 'Copa' },
    { date: '2024-01-25', price: 390, airline: 'LATAM' },
    { date: '2024-01-30', price: 465, airline: 'Copa' },
  ]

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    } catch {
      return dateStr
    }
  }

  const formatPrice = (price) => `$${price}`

  const averagePrice = chartData.reduce((sum, item) => sum + (item.price || 0), 0) / chartData.length
  const minPrice = Math.min(...chartData.map(item => item.price || 0))
  const maxPrice = Math.max(...chartData.map(item => item.price || 0))

  return (
    <div className="price-chart">
      <div className="chart-header">
        <h3>📊 Price Trends</h3>
        <div className="price-stats">
          <div className="stat">
            <span className="label">Average:</span>
            <span className="value">${averagePrice.toFixed(0)}</span>
          </div>
          <div className="stat">
            <span className="label">Min:</span>
            <span className="value text-green">${minPrice}</span>
          </div>
          <div className="stat">
            <span className="label">Max:</span>
            <span className="value text-red">${maxPrice}</span>
          </div>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            stroke="#6b7280"
          />
          <YAxis 
            tickFormatter={formatPrice}
            domain={['dataMin - 20', 'dataMax + 20']}
            stroke="#6b7280"
          />
          <Tooltip 
            formatter={(value, name) => [`$${value}`, 'Price']}
            labelFormatter={(date) => `Date: ${formatDate(date)}`}
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}
          />
          <Area 
            type="monotone" 
            dataKey="price" 
            stroke="#3b82f6" 
            strokeWidth={2}
            fill="url(#priceGradient)"
            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2, fill: '#ffffff' }}
          />
        </AreaChart>
      </ResponsiveContainer>
      
      <div className="chart-insights">
        <div className="insight">
          <span className="insight-icon">💡</span>
          <span className="insight-text">
            {averagePrice > minPrice * 1.1 
              ? "Prices are above average. Consider waiting for a better deal." 
              : "Good time to book! Prices are near historical lows."}
          </span>
        </div>
        <div className="insight">
          <span className="insight-icon">📈</span>
          <span className="insight-text">
            AI recommends booking 2-3 weeks in advance for best prices.
          </span>
        </div>
      </div>
    </div>
  )
}

export default PriceChart

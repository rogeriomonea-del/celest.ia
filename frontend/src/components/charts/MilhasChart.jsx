import React from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'

const data = [
  { name: 'Jan', latam: 19.2, azul: 20.1 },
  { name: 'Feb', latam: 18.5, azul: 20.4 },
  { name: 'Mar', latam: 17.9, azul: 19.9 },
  { name: 'Apr', latam: 18.8, azul: 20.2 },
  { name: 'May', latam: 19.1, azul: 19.5 },
  { name: 'Jun', latam: 18.6, azul: 18.9 },
]

function MilhasChart() {
  return (
    <div>
      <h2>Variação do Milheiro (R$)</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}
          margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis domain={[17, 21]} />
          <Tooltip />
          <Line type="monotone" dataKey="latam" stroke="#8884d8" name="LATAM" />
          <Line type="monotone" dataKey="azul" stroke="#82ca9d" name="Azul" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default MilhasChart

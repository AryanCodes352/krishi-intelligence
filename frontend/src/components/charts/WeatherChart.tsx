'use client';
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface WeatherChartProps {
  currentMonthRainfall: number;
  historicalAvgRainfall: number;
  height?: number;
}

export const WeatherChart = ({ currentMonthRainfall, historicalAvgRainfall, height = 300 }: WeatherChartProps) => {
  const data = [
    {
      name: 'Rainfall (mm)',
      Current: currentMonthRainfall,
      Historical: historicalAvgRainfall,
    }
  ];

  return (
    <div style={{ height }} className="w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" axisLine={false} tickLine={false} />
          <YAxis axisLine={false} tickLine={false} />
          <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
          <Legend />
          <Bar dataKey="Current" fill="#2563eb" radius={[4, 4, 0, 0]} maxBarSize={60} />
          <Bar dataKey="Historical" fill="#9ca3af" radius={[4, 4, 0, 0]} maxBarSize={60} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

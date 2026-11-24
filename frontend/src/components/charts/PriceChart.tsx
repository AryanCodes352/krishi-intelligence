'use client';
import React, { useState, useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { formatINR } from '@/lib/utils';

export type ChartPeriod = '1Y' | '3Y' | '5Y' | 'ALL';

interface PriceChartProps {
  data: Array<{ date: string; modal_price: number; min_price: number; max_price: number }>;
  showMean?: boolean;
  meanValue?: number;
  height?: number;
  defaultPeriod?: ChartPeriod;
  period?: ChartPeriod;
  onPeriodChange?: (period: ChartPeriod) => void;
}

export const PriceChart = ({
  data,
  showMean = false,
  meanValue,
  height = 300,
  defaultPeriod = '3Y',
  period: controlledPeriod,
  onPeriodChange,
}: PriceChartProps) => {
  const [internalPeriod, setInternalPeriod] = useState<ChartPeriod>(defaultPeriod);
  const period = controlledPeriod ?? internalPeriod;

  const handlePeriodChange = (p: ChartPeriod) => {
    if (onPeriodChange) {
      onPeriodChange(p);
    } else {
      setInternalPeriod(p);
    }
  };

  // Filter based on actual calendar dates from the latest available observation
  const filteredData = useMemo(() => {
    if (!data || data.length === 0) return [];
    if (period === 'ALL') return data;

    const latestItem = data[data.length - 1];
    if (!latestItem?.date) return data;

    const latestDate = new Date(latestItem.date);
    if (isNaN(latestDate.getTime())) return data;

    const yearsBack = period === '1Y' ? 1 : period === '3Y' ? 3 : 5;
    const cutoff = new Date(latestDate);
    cutoff.setFullYear(cutoff.getFullYear() - yearsBack);

    return data.filter(item => {
      const itemDate = new Date(item.date);
      return !isNaN(itemDate.getTime()) && itemDate >= cutoff;
    });
  }, [data, period]);

  if (!data || data.length === 0) return <div>No data available</div>;

  return (
    <div className="w-full">
      <div className="flex flex-wrap items-center justify-between mb-4 gap-2">
        <span className="text-xs text-gray-500 font-medium">
          {filteredData.length > 0 && (
            <>
              {new Date(filteredData[0].date).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}
              {' – '}
              {new Date(filteredData[filteredData.length - 1].date).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}
              {' '}({filteredData.length} weekly observations)
            </>
          )}
        </span>
        <div className="flex gap-1.5">
          {(['1Y', '3Y', '5Y', 'ALL'] as const).map(p => (
            <button
              key={p}
              onClick={() => handlePeriodChange(p)}
              className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                period === p 
                  ? 'bg-krishi-green text-white shadow-sm font-semibold' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={filteredData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2d6a4f" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#2d6a4f" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(val) => {
                const d = new Date(val);
                return `${d.toLocaleString('default', { month: 'short' })} ${d.getFullYear().toString().slice(2)}`;
              }}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              minTickGap={40}
            />
            <YAxis 
              tickFormatter={(val) => `₹${val}`} 
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              width={60}
            />
            <Tooltip 
              formatter={(value: number) => [formatINR(value), 'Modal Price']}
              labelFormatter={(label) => new Date(label).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
              })}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
            {showMean && meanValue && (
              <ReferenceLine 
                y={meanValue} 
                stroke="#d4a017" 
                strokeDasharray="3 3" 
                label={{ position: 'insideTopLeft', value: `7Y Avg: ${formatINR(meanValue)}`, fill: '#d4a017', fontSize: 11 }} 
              />
            )}
            <Area type="monotone" dataKey="modal_price" stroke="#2d6a4f" strokeWidth={2} fillOpacity={1} fill="url(#colorPrice)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};


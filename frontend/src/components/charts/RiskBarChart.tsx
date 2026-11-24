import React from 'react';
import { cn } from '@/lib/utils';

interface RiskBarChartProps {
  factors: Array<{
    parameter?: string;
    name?: string; // some APIs might use name instead of parameter
    score: number;
    max_score?: number;
    contribution?: number;
    direction?: string;
  }>;
}

export const RiskBarChart = ({ factors }: RiskBarChartProps) => {
  return (
    <div className="space-y-3">
      {factors.map((factor, i) => {
        const label = factor.parameter || factor.name || 'Factor';
        const val = factor.score || factor.contribution || 0;
        const max = factor.max_score || 100; // default max
        const percentage = Math.min(Math.max((val / max) * 100, 0), 100);
        
        // Color based on value logic (assuming higher is worse for risk, but could vary)
        let colorClass = 'bg-green-500';
        if (percentage > 40) colorClass = 'bg-amber-500';
        if (percentage > 70) colorClass = 'bg-red-500';

        return (
          <div key={i}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-700 font-medium">{label}</span>
              <span className="text-gray-500">{val} / {max}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={cn("h-2 rounded-full", colorClass)} 
                style={{ width: `${percentage}%` }}
              ></div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

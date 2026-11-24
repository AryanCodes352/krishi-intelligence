import React from 'react';
import { cn } from '@/lib/utils';

export const RiskGauge = ({ score, size = 'medium', showLabel = true }: { score: number, size?: 'small' | 'medium' | 'large', showLabel?: boolean }) => {
  const radius = size === 'small' ? 20 : size === 'large' ? 60 : 40;
  const strokeWidth = size === 'small' ? 4 : size === 'large' ? 12 : 8;
  const normalizedScore = Math.min(Math.max(score, 0), 100);
  
  const circumference = radius * Math.PI;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  let color = 'text-risk-low';
  let label = 'LOW';
  if (normalizedScore >= 40) { color = 'text-risk-medium'; label = 'MEDIUM'; }
  if (normalizedScore >= 70) { color = 'text-risk-high'; label = 'HIGH'; }

  return (
    <div className="flex flex-col items-center justify-center">
      <div className={cn("relative flex items-end justify-center", size === 'small' ? 'h-6' : size === 'large' ? 'h-20' : 'h-14')}>
        <svg 
          className="transform rotate-180"
          width={radius * 2} 
          height={radius + strokeWidth}
        >
          <path
            d={`M ${strokeWidth/2} ${radius} A ${radius - strokeWidth/2} ${radius - strokeWidth/2} 0 0 1 ${radius*2 - strokeWidth/2} ${radius}`}
            fill="none"
            className="stroke-gray-200"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          <path
            d={`M ${strokeWidth/2} ${radius} A ${radius - strokeWidth/2} ${radius - strokeWidth/2} 0 0 1 ${radius*2 - strokeWidth/2} ${radius}`}
            fill="none"
            className={cn("transition-all duration-1000", color.replace('text-', 'stroke-'))}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute bottom-0 text-center flex flex-col">
          <span className={cn("font-bold", size === 'small' ? 'text-xs' : size === 'large' ? 'text-3xl' : 'text-xl', color)}>{Math.round(normalizedScore)}</span>
        </div>
      </div>
      {showLabel && (
        <span className={cn("mt-1 font-semibold", size === 'small' ? 'text-[10px]' : 'text-sm', color)}>{label}</span>
      )}
    </div>
  );
};

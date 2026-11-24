import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

interface WhatChangedProps {
  what_changed: {
    available: boolean;
    message?: string;
    changes?: Array<{ metric: string; from: string; to: string; direction: string }>;
  };
}

export const WhatChanged = ({ what_changed }: WhatChangedProps) => {
  if (!what_changed.available) {
    return (
      <div className="text-sm text-gray-500 italic py-2">
        {what_changed.message || "No previous observation available for comparison."}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200">
      <h4 className="text-sm font-semibold text-gray-700 mb-3">What changed since last analysis?</h4>
      <div className="space-y-3">
        {what_changed.changes?.map((change, i) => (
          <div key={i} className="flex items-center justify-between text-sm">
            <span className="text-gray-600">{change.metric}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-400 line-through text-xs">{change.from}</span>
              {change.direction === 'UP' ? (
                <ArrowUpRight className="w-4 h-4 text-red-500" />
              ) : change.direction === 'DOWN' ? (
                <ArrowDownRight className="w-4 h-4 text-green-500" />
              ) : (
                <Minus className="w-4 h-4 text-gray-400" />
              )}
              <span className="font-medium text-gray-900">{change.to}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

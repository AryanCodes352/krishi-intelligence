'use client';
import React, { useState } from 'react';
import { DataBadge } from './DataBadge';
import { AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { cn, formatINR, getRiskColor } from '@/lib/utils';
import { PredictionItem } from '@/lib/types';

interface PredictionCardProps {
  title: string;
  prediction?: PredictionItem;
  data_used?: string[];
  timestamp?: string;
  model_info?: any;
  insufficient_data?: boolean;
}

export const PredictionCard = ({ 
  title, 
  prediction, 
  data_used = [], 
  timestamp, 
  model_info, 
  insufficient_data 
}: PredictionCardProps) => {
  const [showExplanation, setShowExplanation] = useState(false);

  if (
    insufficient_data ||
    !prediction ||
    prediction.min_price == null ||
    prediction.max_price == null ||
    isNaN(Number(prediction.min_price)) ||
    isNaN(Number(prediction.max_price))
  ) {
    return (
      <div className="bg-white p-5 rounded-xl border border-red-100 shadow-sm">
        <div className="flex justify-between items-start mb-3">
          <h3 className="font-serif text-lg text-krishi-green-dark">{title}</h3>
          <DataBadge type="UNAVAILABLE" small />
        </div>
        <div className="flex items-start gap-3 p-4 bg-red-50 text-red-700 rounded-lg">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-sm">Prediction unavailable — insufficient reliable data</p>
            <p className="text-xs text-red-600 mt-0.5">Not enough reliable historical observations for this market/crop combination.</p>
          </div>
        </div>
      </div>
    );
  }

  const confidenceLevel = prediction.confidence_level || 'MEDIUM';
  const confidencePct = prediction.confidence_pct ?? 70;

  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:border-krishi-green/40 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <h3 className="font-serif text-lg text-krishi-green-dark font-bold">{title}</h3>
        <DataBadge type="MODEL_PREDICTION" small />
      </div>

      <div className="mb-4">
        <div className="text-3xl font-bold text-gray-900 mb-1">
          {formatINR(prediction.min_price)} – {formatINR(prediction.max_price)}
        </div>
        <p className="text-sm text-gray-500">
          Expected range per quintal {prediction.point_estimate ? `(est. ${formatINR(prediction.point_estimate)})` : ''}
        </p>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">Confidence:</span>
          <span className={cn("font-medium px-2 py-0.5 rounded text-xs", getRiskColor(confidenceLevel === 'HIGH' ? 'LOW' : confidenceLevel === 'MEDIUM' ? 'MEDIUM' : 'HIGH'))}>
            {confidencePct}% ({confidenceLevel})
          </span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">Based on:</span>
          <span className="text-gray-900 truncate ml-4 text-xs" title={(data_used || []).join(', ')}>
            {(data_used || []).length} data sources
          </span>
        </div>
        <div className="flex justify-between text-[11px] text-gray-400">
          <span>Updated: {timestamp ? new Date(timestamp).toLocaleDateString() : 'Recently'}</span>
          <span>Source: XGBoost</span>
        </div>
      </div>

      <button 
        onClick={() => setShowExplanation(!showExplanation)}
        className="w-full py-2 text-sm text-krishi-green font-medium flex items-center justify-center gap-1 hover:bg-gray-50 rounded-lg transition-colors border border-gray-100"
      >
        Why this prediction? {showExplanation ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {showExplanation && (
        <div className="mt-4 border-t pt-4">
          <h4 className="text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">Model Details</h4>
          <ul className="text-xs text-gray-600 space-y-1.5 mb-3 bg-gray-50 p-3 rounded-lg border border-gray-100">
            <li className="flex justify-between"><span className="text-gray-500">Model Type:</span> <span className="font-medium">{model_info?.type || 'XGBoost Regressor'}</span></li>
            {model_info?.training_data_points ? (
              <li className="flex justify-between"><span className="text-gray-500">Training Samples:</span> <span className="font-medium">{model_info.training_data_points} weekly observations</span></li>
            ) : null}
            {model_info?.mae != null ? (
              <li className="flex justify-between"><span className="text-gray-500">Measured MAE:</span> <span className="font-medium">{formatINR(model_info.mae)}/q</span></li>
            ) : null}
            {model_info?.mape_pct != null ? (
              <li className="flex justify-between"><span className="text-gray-500">Measured MAPE:</span> <span className="font-medium">{model_info.mape_pct}%</span></li>
            ) : null}
          </ul>
          {data_used && data_used.length > 0 && (
            <div>
              <h5 className="text-[11px] font-semibold text-gray-500 mb-1">Key Signals Used:</h5>
              <ul className="list-disc pl-4 text-[11px] text-gray-600 space-y-0.5">
                {data_used.slice(0, 3).map((sig, idx) => (
                  <li key={idx}>{sig}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

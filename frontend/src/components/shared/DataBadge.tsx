import React from 'react';
import { cn } from '@/lib/utils';

type BadgeType = 'LIVE' | 'STALE' | 'MODEL_PREDICTION' | 'HISTORICAL_SEED' | 'REGIONAL_ESTIMATE' | 'DEMO_DATA' | 'UNAVAILABLE' | 'DATA_UNAVAILABLE' | 'MARKET_UNSUPPORTED' | 'LATEST_AVAILABLE' | 'SOIL_HEALTH_CARD' | 'FARMER_ENTERED';

export const DataBadge = ({ type, small = false }: { type: BadgeType; small?: boolean }) => {
  let style = '';
  let dot = false;
  switch (type) {
    case 'LIVE':
      style = 'bg-green-100 text-green-800 border-green-200';
      dot = true;
      break;
    case 'STALE':
      style = 'bg-orange-100 text-orange-800 border-orange-200';
      break;
    case 'LATEST_AVAILABLE':
      style = 'bg-teal-100 text-teal-800 border-teal-200';
      break;
    case 'MODEL_PREDICTION':
      style = 'bg-blue-100 text-blue-800 border-blue-200';
      break;
    case 'HISTORICAL_SEED':
      style = 'bg-amber-100 text-amber-800 border-amber-200';
      break;
    case 'REGIONAL_ESTIMATE':
      style = 'bg-orange-100 text-orange-800 border-orange-200';
      break;
    case 'SOIL_HEALTH_CARD':
      style = 'bg-emerald-100 text-emerald-800 border-emerald-200';
      break;
    case 'FARMER_ENTERED':
      style = 'bg-sky-100 text-sky-800 border-sky-200';
      break;
    case 'DEMO_DATA':
      style = 'bg-gray-100 text-gray-800 border-gray-200';
      break;
    case 'UNAVAILABLE':
    case 'DATA_UNAVAILABLE':
      style = 'bg-red-100 text-red-800 border-red-200';
      break;
    case 'MARKET_UNSUPPORTED':
      style = 'bg-gray-100 text-gray-700 border-gray-200';
      break;
  }



  return (
    <span className={cn('inline-flex items-center gap-1 rounded-full border font-medium', small ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-0.5 text-xs', style)}>
      {dot && <span className="relative flex h-1.5 w-1.5"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span><span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-600"></span></span>}
      {type.replace(/_/g, ' ')}
    </span>
  );
};


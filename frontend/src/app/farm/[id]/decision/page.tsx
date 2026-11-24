'use client';
import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { FullAnalysis, DecisionScenario } from '@/lib/types';
import { ArrowLeft, ArrowRight, Brain, CheckCircle2, TrendingUp, Info } from 'lucide-react';
import { formatINR, cn } from '@/lib/utils';
import { ExplainabilityPanel } from '@/components/shared/ExplainabilityPanel';
import { PredictionCard } from '@/components/shared/PredictionCard';

export default function DecisionPage() {
  const params = useParams();
  const router = useRouter();
  const [data, setData] = useState<FullAnalysis | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);

  useEffect(() => {
    const load = async () => {
      if (typeof params.id === 'string') {
        const res = await api.analyzeIntelligence(params.id);
        setData(res);
      }
    };
    load();
  }, [params.id]);

  if (!data) return <div className="p-8 text-center animate-pulse">Running AI Decision Engine...</div>;

  const { decision, price_prediction, farm_summary } = data;
  const bestAction = decision.recommendation.action;

  const renderScenarioCard = (key: string, title: string, scenario: DecisionScenario, isRecommended: boolean) => (
    <div className={cn(
      "relative bg-white rounded-2xl p-6 border-2 transition-all flex flex-col h-full",
      isRecommended ? "border-krishi-gold shadow-lg transform md:-translate-y-2" : "border-gray-200 shadow-sm hover:border-krishi-green/50"
    )}>
      {isRecommended && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-krishi-gold text-krishi-green-dark px-4 py-1 rounded-full text-xs font-bold flex items-center gap-1 shadow-sm whitespace-nowrap">
          <CheckCircle2 className="w-4 h-4" /> RECOMMENDED
        </div>
      )}
      
      <h3 className="text-xl font-serif font-bold text-center mb-6 text-gray-900">{title}</h3>
      
      <div className="flex-1 space-y-4">
        <div>
          <p className="text-xs text-gray-500 mb-1">Expected Price / qtl</p>
          <p className="text-xl font-bold text-gray-900">
            {scenario.expected_price_min && scenario.expected_price_max 
              ? `${formatINR(scenario.expected_price_min)} - ${formatINR(scenario.expected_price_max)}`
              : formatINR(scenario.expected_price)}
          </p>
        </div>
        
        <div className="space-y-2 text-sm border-t border-gray-100 pt-4">
          <div className="flex justify-between">
            <span className="text-gray-600">Expected Revenue</span>
            <span className="font-medium">{formatINR(scenario.expected_revenue)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Storage Cost</span>
            <span className="text-red-500 font-medium">-{formatINR(scenario.storage_cost)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Weather Risk Penalty</span>
            <span className="text-red-500 font-medium">-{formatINR(scenario.weather_risk_penalty)}</span>
          </div>
        </div>
      </div>
      
      <div className="mt-6 pt-6 border-t-2 border-dashed border-gray-200">
        <p className="text-xs text-gray-500 mb-1">Estimated Net Realization</p>
        <p className={cn("text-3xl font-bold", isRecommended ? "text-krishi-green" : "text-gray-900")}>
          {formatINR(scenario.net_realization)}
        </p>
        
        <div className="mt-4 flex items-center justify-between">
          <span className={cn(
            "text-xs font-bold px-2 py-1 rounded",
            scenario.risk_level === 'LOW' ? 'bg-green-100 text-green-800' :
            scenario.risk_level === 'MEDIUM' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
          )}>
            {scenario.risk_level} RISK
          </span>
          <span className="text-xs text-gray-500">{scenario.confidence_pct}% Confidence</span>
        </div>
      </div>
    </div>
  );

  const acres = Number(farm_summary.farm_area_acres);
  const areaLabel = `${farm_summary.farm_area_acres} ${acres === 1 ? 'acre' : 'acres'}`;
  
  const locationLabel = (() => {
    const loc = farm_summary.location?.trim();
    const dist = farm_summary.district?.trim();
    const isInvalid = (s?: string) => !s || ['farm', 'village name', 'n/a', 'unknown'].includes(s.toLowerCase());
    
    const validLoc = !isInvalid(loc) ? loc : '';
    const validDist = !isInvalid(dist) ? dist : '';
    
    if (validLoc && validDist && validLoc.toLowerCase() !== validDist.toLowerCase()) {
      return `in ${validLoc}, ${validDist}`;
    }
    if (validLoc) {
      return `in ${validLoc}`;
    }
    if (validDist) {
      return `in ${validDist}`;
    }
    return 'for your farm';
  })();

  const isMarketUnavailable = bestAction === 'MARKET_UNAVAILABLE';

  return (
    <div className="space-y-8 pb-20 max-w-6xl mx-auto">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      <div className="text-center max-w-3xl mx-auto mb-10">
        <h1 className="text-4xl md:text-5xl font-serif font-bold text-krishi-green-dark mb-4">Should I Sell Now?</h1>
        <p className="text-xl text-gray-600">Risk-adjusted financial analysis for {areaLabel} of {farm_summary.crop || 'crop'} {locationLabel}.</p>
      </div>

      {isMarketUnavailable ? (
        /* ── Market Unavailable State ─────────────────────────────── */
        <div className="space-y-6">
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-8 text-center max-w-2xl mx-auto">
            <div className="flex justify-center mb-4">
              <div className="bg-amber-100 rounded-full p-4">
                <Info className="w-10 h-10 text-amber-600" />
              </div>
            </div>
            <h2 className="text-2xl font-serif font-bold text-amber-800 mb-3">
              {decision.recommendation.headline}
            </h2>
            <p className="text-amber-700 mb-4">{decision.recommendation.summary}</p>
            <div className="bg-white border border-amber-200 rounded-xl p-4 text-left text-sm text-gray-700">
              <p className="font-semibold text-gray-800 mb-2">Available intelligence for {farm_summary.crop}:</p>
              <ul className="list-disc pl-4 space-y-1 text-gray-600">
                <li><strong>Soil Intelligence</strong> — nutrient analysis and suitability score</li>
                <li><strong>Weather Risk</strong> — 7-day forecasts and agricultural risk scoring</li>
                <li><strong>AI Agronomist</strong> — expert crop management guidance</li>
              </ul>
            </div>
          </div>
        </div>
      ) : (
        /* ── Full Market-Supported Decision UI ───────────────────── */
        <>
          {/* Hero Recommendation Box */}
          <div className="bg-krishi-green-dark text-white rounded-2xl p-6 md:p-8 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-10">
              <Brain className="w-64 h-64" />
            </div>
            <div className="relative z-10 max-w-3xl">
              <div className="flex flex-wrap items-center gap-3 mb-6">
                <span className={cn(
                  "px-4 py-1.5 rounded-full text-sm font-bold tracking-wider",
                  bestAction === 'SELL_NOW' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
                )}>
                  ACTION: {bestAction.replace('_', ' ')}
                </span>
                <span className="text-krishi-gold text-sm font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> {decision.recommendation.confidence} Match
                </span>
              </div>
              
              <h2 className="text-3xl md:text-4xl font-serif font-bold mb-4 leading-tight text-krishi-cream">
                {decision.recommendation.headline}
              </h2>
              <p className="text-lg text-gray-300 mb-8 leading-relaxed">
                {decision.recommendation.summary}
              </p>

              <button 
                onClick={() => setShowExplanation(!showExplanation)}
                className="text-krishi-gold hover:text-krishi-gold-light font-medium flex items-center gap-2 text-sm transition-colors"
              >
                {showExplanation ? 'Hide detailed reasoning' : 'Show detailed reasoning'} <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            {showExplanation && (
              <div className="mt-8 relative z-10">
                <ExplainabilityPanel 
                  signals={data.explainability.data_signals}
                  data_used={data.explainability.data_used}
                  reasoning_steps={data.explainability.reasoning_steps}
                  conclusion={data.explainability.conclusion}
                  confidence={data.explainability.prediction_confidence}
                  data_quality={data.explainability.data_quality_overall}
                  important_note={data.explainability.important_note}
                />
              </div>
            )}
          </div>

          {/* Scenarios Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
            {renderScenarioCard('sell_now', 'Sell Now (Today)', decision.scenarios.sell_now, bestAction === 'SELL_NOW')}
            {renderScenarioCard('wait_7d', 'Wait 7 Days', decision.scenarios.wait_7d, bestAction === 'WAIT_7D')}
            {renderScenarioCard('wait_15d', 'Wait 15 Days', decision.scenarios.wait_15d, bestAction === 'WAIT_15D')}
          </div>

          {/* Prediction Cards */}
          <div className="pt-10">
            <h3 className="text-2xl font-serif font-bold text-krishi-green-dark mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6" /> ML Price Predictions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PredictionCard 
                title="7-Day Price Horizon" 
                prediction={price_prediction?.prediction_7d || price_prediction?.prediction}
                data_used={price_prediction?.data_used}
                timestamp={price_prediction?.timestamp}
                model_info={price_prediction?.model_info}
                insufficient_data={price_prediction?.insufficient_data || !(price_prediction?.prediction_7d || price_prediction?.prediction)}
              />
              <PredictionCard 
                title="15-Day Price Horizon" 
                prediction={price_prediction?.prediction_15d}
                data_used={price_prediction?.data_used}
                timestamp={price_prediction?.timestamp}
                model_info={price_prediction?.model_info}
                insufficient_data={price_prediction?.insufficient_data || !price_prediction?.prediction_15d}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}


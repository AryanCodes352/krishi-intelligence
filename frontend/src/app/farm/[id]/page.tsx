'use client';
import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { FullAnalysis } from '@/lib/types';
import { RiskGauge } from '@/components/shared/RiskGauge';
import { DataBadge } from '@/components/shared/DataBadge';
import { CardSkeleton } from '@/components/shared/LoadingSkeleton';
import { ExplainabilityPanel } from '@/components/shared/ExplainabilityPanel';
import { WhatChanged } from '@/components/shared/WhatChanged';
import { formatINR, getRiskColor, cn } from '@/lib/utils';
import { ArrowRight, Brain, Sprout, CloudRain, TrendingUp, AlertTriangle, RefreshCw } from 'lucide-react';

export default function FarmDashboard() {
  const params = useParams();
  const router = useRouter();
  const [data, setData] = useState<FullAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [reanalyzing, setReanalyzing] = useState(false);
  const [reanalyzeError, setReanalyzeError] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      if (typeof params.id === 'string') {
        const res = await api.analyzeIntelligence(params.id);
        setData(res);
      }
      setLoading(false);
    };
    loadData();
  }, [params.id]);

  const handleReanalyze = async () => {
    if (reanalyzing || typeof params.id !== 'string') return;
    setReanalyzing(true);
    setReanalyzeError(null);
    try {
      const res = await api.analyzeIntelligence(params.id);
      if (res && res.generated_at) {
        setData(res);
      } else {
        setReanalyzeError('Re-analysis failed to return updated data.');
      }
    } catch (err) {
      console.error('Re-analysis error:', err);
      setReanalyzeError('Re-analysis request failed. Please check connection.');
    } finally {
      setReanalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-24 bg-gray-200 animate-pulse rounded-xl" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <CardSkeleton /><CardSkeleton /><CardSkeleton /><CardSkeleton />
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-serif text-red-600 mb-2">Analysis Failed</h2>
        <p className="text-gray-600 mb-6">Could not load intelligence data for this farm.</p>
        <button onClick={() => window.location.reload()} className="px-4 py-2 bg-krishi-green text-white rounded">Retry</button>
      </div>
    );
  }

  const { farm_summary: farm, intelligence_snapshot: snap, decision } = data;
  const bestAction = decision.recommendation.action;

  return (
    <div className="space-y-6 pb-20">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-krishi-green-dark">
            {farm.farmer_name?.trim() ? `${farm.farmer_name}'s Farm` : 'Farm Intelligence Dashboard'}
          </h1>
          <p className="text-gray-600 flex items-center gap-2 text-sm mt-1">
            {farm.crop} ({farm.farm_area_acres} {Number(farm.farm_area_acres) === 1 ? 'acre' : 'acres'}) in {farm.district}, {farm.state}
            <span className="bg-krishi-green/10 text-krishi-green px-2 py-0.5 rounded-full text-xs font-medium">Day {farm.days_after_sowing}</span>
          </p>
        </div>
        <div className="text-right flex flex-col items-end">
          <span className="text-xs text-gray-500">Last analyzed: {new Date(data.generated_at).toLocaleString()}</span>
          <button 
            onClick={handleReanalyze}
            disabled={reanalyzing}
            className="text-sm text-krishi-green font-medium hover:underline mt-1 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
            aria-label={reanalyzing ? "Re-analyzing farm data..." : "Re-analyze farm data"}
          >
            {reanalyzing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-krishi-green" />
                <span>Re-analyzing...</span>
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5 text-krishi-green" />
                <span>Re-analyze Data</span>
              </>
            )}
          </button>
          {reanalyzeError && (
            <span className="text-xs text-red-600 mt-1">{reanalyzeError}</span>
          )}
        </div>
      </div>

      {/* AI Recommendation Hero */}
      <div className={cn(
        "rounded-2xl p-6 md:p-8 text-white relative overflow-hidden shadow-lg border",
        bestAction === 'MARKET_UNAVAILABLE'
          ? "bg-amber-700 border-amber-600"
          : "bg-krishi-green-dark border-krishi-green"
      )}>
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <Brain className="w-48 h-48" />
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-4">
            <span className="bg-krishi-gold text-krishi-green-dark text-xs font-bold px-3 py-1 rounded-full tracking-wider flex items-center gap-1">
              <Brain className="w-3 h-3" /> AI RECOMMENDATION
            </span>
            {bestAction !== 'MARKET_UNAVAILABLE' && (
              <span className={cn("text-xs font-bold px-2 py-1 rounded", bestAction === 'SELL_NOW' ? 'bg-red-500 text-white' : 'bg-green-500 text-white')}>
                {decision.recommendation.confidence} Confidence
              </span>
            )}
          </div>
          
          <h2 className="text-3xl md:text-5xl font-serif font-bold mb-4 text-krishi-cream leading-tight">
            {decision.recommendation.headline}
          </h2>
          <p className="text-lg md:text-xl text-gray-300 max-w-2xl mb-8 leading-relaxed">
            {decision.recommendation.summary}
          </p>
          
          <div className="flex flex-wrap items-center gap-4">
            <Link 
              href={`/farm/${params.id}/decision`}
              className="bg-krishi-gold hover:bg-krishi-gold-light text-krishi-green-dark px-6 py-3 rounded-xl font-bold text-lg transition-colors flex items-center gap-2"
            >
              View Financial Scenarios <ArrowRight className="w-5 h-5" />
            </Link>
            <button 
              onClick={() => setShowExplanation(!showExplanation)}
              className="px-6 py-3 border border-krishi-cream/30 hover:bg-white/10 rounded-xl font-medium transition-colors"
            >
              Why this recommendation?
            </button>
          </div>

          {showExplanation && (
            <div className="mt-6 bg-white/10 backdrop-blur-sm rounded-xl p-1 text-gray-800">
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
      </div>

      {data.what_changed.available && (
        <WhatChanged what_changed={data.what_changed} />
      )}

      {/* 2x2 Intelligence Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* SOIL */}
        <Link href={`/farm/${params.id}/soil`} className="block group">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-full hover:border-krishi-soil transition-colors relative">
            <div className="flex justify-between items-start mb-6">
              <div className="flex items-center gap-2 text-krishi-soil font-serif text-lg font-bold">
                <Sprout className="w-5 h-5" /> Soil Condition
              </div>
              <DataBadge type={data.data_freshness.soil as any} small />
            </div>
            <div className="flex items-center gap-6">
              <RiskGauge score={snap.soil_condition.score} />
              <div>
                <p className={cn("text-xl font-bold", getRiskColor(snap.soil_condition.level))}>{snap.soil_condition.label}</p>
                <p className="text-sm text-gray-500 mt-1">Tap to view nutrient breakdown & recommendations</p>
              </div>
            </div>
          </div>
        </Link>

        {/* WEATHER */}
        <Link href={`/farm/${params.id}/weather`} className="block group">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-full hover:border-krishi-sky transition-colors relative">
            <div className="flex justify-between items-start mb-6">
              <div className="flex items-center gap-2 text-krishi-sky font-serif text-lg font-bold">
                <CloudRain className="w-5 h-5" /> Weather Risk
              </div>
              <DataBadge type={data.data_freshness.weather as any} small />
            </div>
            <div className="flex items-center gap-6">
              <RiskGauge score={snap.weather_risk.score} />
              <div>
                <p className={cn("text-xl font-bold", getRiskColor(snap.weather_risk.level))}>{snap.weather_risk.label}</p>
                <p className="text-sm text-gray-500 mt-1">Tap for 7-day forecast & anomaly alerts</p>
              </div>
            </div>
          </div>
        </Link>

        {/* CROP */}
        <Link 
          href={`/farm/${params.id}/expert`} 
          className="block group rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-krishi-green focus-visible:ring-offset-2"
          aria-label={`Crop Risk: ${snap.crop_risk.label} (${snap.crop_risk.score}/100) during ${farm.crop_stage} stage. Click to consult AI Agronomist.`}
        >
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-full hover:border-krishi-green-dark hover:shadow-md transition-all relative">
            <div className="flex justify-between items-start mb-6">
              <div className="flex items-center gap-2 text-krishi-green-dark font-serif text-lg font-bold">
                <AlertTriangle className="w-5 h-5" /> Crop Risk
              </div>
              <DataBadge type="MODEL_PREDICTION" small />
            </div>
            <div className="flex items-center gap-6">
              <RiskGauge score={snap.crop_risk.score} />
              <div>
                <p className={cn("text-xl font-bold", getRiskColor(snap.crop_risk.level))}>{snap.crop_risk.label}</p>
                <p className="text-sm text-gray-500 mt-1">Vulnerability during {farm.crop_stage} stage</p>
                <p className="text-xs text-krishi-green font-medium mt-1 flex items-center gap-1 group-hover:underline">
                  Tap to consult AI Agronomist <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                </p>
              </div>
            </div>
          </div>
        </Link>

        {/* MARKET */}
        <Link href={`/farm/${params.id}/market`} className="block group">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-full hover:border-krishi-gold transition-colors relative">
            <div className="flex justify-between items-start mb-6">
              <div className="flex items-center gap-2 text-krishi-gold font-serif text-lg font-bold">
                <TrendingUp className="w-5 h-5" /> Market Trend
              </div>
              <DataBadge type={data.data_freshness.market as any} small />
            </div>
            <div className="mt-2">
              {snap.market_trend.market_supported === false ? (
                <>
                  <p className="text-lg font-semibold text-amber-700 mb-1">Not Available</p>
                  <p className="text-sm text-amber-600">
                    Market Intelligence for {farm.crop} is planned for the next version.
                  </p>
                </>
              ) : (
                <>
                  <p className="text-3xl font-bold text-gray-900 mb-1">{formatINR(snap.market_trend.current_price)}<span className="text-sm text-gray-500 font-normal">/q</span></p>
                  <p className={cn("text-md font-medium flex items-center gap-1", snap.market_trend.direction === 'UP' ? 'text-green-600' : snap.market_trend.direction === 'DOWN' ? 'text-red-600' : 'text-gray-600')}>
                    {snap.market_trend.label}
                  </p>
                </>
              )}
            </div>
          </div>
        </Link>
      </div>


      <div className="flex justify-center mt-8">
        <Link href={`/farm/${params.id}/data-sources`} className="text-sm text-gray-500 hover:text-krishi-green underline">
          View Data Sources & Transparency Report
        </Link>
      </div>
    </div>
  );
}

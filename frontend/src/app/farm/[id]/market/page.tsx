'use client';
import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { MarketIntelligence, FarmProfile } from '@/lib/types';
import { ArrowLeft, TrendingUp, TrendingDown, Minus, Info, Wifi, WifiOff } from 'lucide-react';
import { DataBadge } from '@/components/shared/DataBadge';
import { PriceChart, ChartPeriod } from '@/components/charts/PriceChart';
import { formatINR } from '@/lib/utils';

function MarketUnsupportedPanel({ crop, onBack }: { crop: string; onBack: () => void }) {
  return (
    <div className="space-y-6 pb-20 max-w-5xl mx-auto">
      <button onClick={onBack} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>
      <div>
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-serif font-bold text-krishi-gold flex items-center gap-3">
            <TrendingUp className="w-8 h-8" /> Market Intelligence
          </h1>
        </div>
        <div className="mt-2 flex items-center text-xs sm:text-sm">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-50/70 border border-amber-200/80 font-medium text-slate-700">
            <span className="text-amber-700 text-sm leading-none shrink-0">🌾</span>
            <span>
              <span className="font-semibold text-amber-900">{crop}</span>
              <span className="mx-1.5 text-slate-300">•</span>
              <span className="text-slate-600 font-medium">Regional APMC Mandi</span>
            </span>
          </div>
        </div>
      </div>
      <div className="bg-amber-50 border border-amber-200 rounded-2xl p-8 text-center max-w-2xl mx-auto">
        <div className="flex justify-center mb-4">
          <div className="bg-amber-100 rounded-full p-4">
            <Info className="w-10 h-10 text-amber-600" />
          </div>
        </div>
        <h2 className="text-2xl font-serif font-bold text-amber-800 mb-3">Market Intelligence Not Yet Available</h2>
        <p className="text-amber-700 text-lg mb-2">Market Intelligence for <strong>{crop}</strong> is not yet available in this prototype.</p>
        <p className="text-amber-600 text-sm mb-6">{crop} market prediction is planned for the next version. Currently, reliable market intelligence and XGBoost price prediction is available for <strong>Wheat</strong> only.</p>
        <div className="bg-white border border-amber-200 rounded-xl p-4 text-left text-sm text-gray-700">
          <p className="font-semibold text-gray-800 mb-2">What you can do:</p>
          <ul className="list-disc pl-4 space-y-1 text-gray-600">
            <li>Use <strong>Soil Intelligence</strong> for nutrient and suitability analysis</li>
            <li>Check <strong>Weather Risk</strong> for 7-day forecasts</li>
            <li>Consult the <strong>AI Agronomist</strong> for expert crop guidance</li>
            <li>Contact local mandi commission agents for current {crop} prices</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default function MarketPage() {
  const params = useParams();
  const router = useRouter();
  const [farm, setFarm] = useState<FarmProfile | null>(null);
  const [data, setData] = useState<MarketIntelligence | null>(null);
  const [unsupported, setUnsupported] = useState(false);
  const [loading, setLoading] = useState(true);
  const [chartPeriod, setChartPeriod] = useState<ChartPeriod>('3Y');

  const getPriceHistoryTitle = (period: ChartPeriod) => {
    switch (period) {
      case '1Y':
        return 'Price History (1 Year)';
      case '3Y':
        return 'Price History (3 Years)';
      case '5Y':
        return 'Price History (5 Years)';
      case 'ALL':
        return 'Price History (All Available Data)';
      default:
        return 'Price History';
    }
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      if (typeof params.id !== 'string') { setLoading(false); return; }
      const farmRes = await api.getFarm(params.id);
      if (!farmRes) { setLoading(false); return; }
      setFarm(farmRes);
      const res = await api.getMarket(farmRes.crop, farmRes.district, farmRes.state);
      if (!res || !res.current || (res.data_source?.type === 'MARKET_UNSUPPORTED')) {
        setUnsupported(true);
      } else {
        setData(res);
      }
      setLoading(false);
    };
    load();
  }, [params.id]);

  if (loading) return <div className="p-8 text-center animate-pulse">Loading market intelligence...</div>;
  if (unsupported || !data) return <MarketUnsupportedPanel crop={farm?.crop || 'this crop'} onBack={() => router.back()} />;

  const current = data.current;
  const stats = data.historical.statistics;
  const dsType = data.data_source?.type;
  const isLive = dsType === 'LIVE';
  const isLatestAvailable = dsType === 'LATEST_AVAILABLE';
  const isStale = dsType === 'STALE';
  const isHistoricalSeed = dsType === 'HISTORICAL_SEED';
  const isOfficialSource = isLive || isLatestAvailable || isStale;
  const badgeType: 'LIVE' | 'LATEST_AVAILABLE' | 'STALE' | 'HISTORICAL_SEED' = isLive
    ? 'LIVE'
    : isLatestAvailable
    ? 'LATEST_AVAILABLE'
    : isStale
    ? 'STALE'
    : 'HISTORICAL_SEED';

  const retrievedAtLabel = current.retrieved_at
    ? new Date(current.retrieved_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
    : null;

  const cropDisplay = farm?.crop || current?.commodity || 'Wheat';
  const regionDisplay = farm?.district 
    ? `${farm.district} Mandi${farm.state ? `, ${farm.state}` : ''}`
    : current?.market 
    ? `${current.market} Mandi` 
    : 'Lucknow Mandi, Uttar Pradesh';

  return (
    <div className="space-y-6 pb-20 max-w-5xl mx-auto">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>
      <div>
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-serif font-bold text-krishi-gold flex items-center gap-3">
            <TrendingUp className="w-8 h-8" /> Market Intelligence
          </h1>
          <div className="flex items-center gap-3">
            {isOfficialSource ? <Wifi className="w-4 h-4 text-green-600" /> : <WifiOff className="w-4 h-4 text-amber-500" />}
            <DataBadge type={badgeType} />
          </div>
        </div>
        <div className="mt-2 flex items-center text-xs sm:text-sm">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-50/70 border border-amber-200/80 font-medium text-slate-700">
            <span className="text-amber-700 text-sm leading-none shrink-0">🌾</span>
            <span>
              <span className="font-semibold text-amber-900">{cropDisplay}</span>
              <span className="mx-1.5 text-slate-300">•</span>
              <span className="text-slate-600 font-medium">{regionDisplay}</span>
            </span>
          </div>
        </div>
      </div>

      {/* LIVE provenance bar */}
      {isLive && (
        <div className="flex items-center gap-3 bg-green-50 border border-green-200 rounded-xl px-4 py-2.5 text-sm text-green-800">
          <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-green-600"></span></span>
          <span><strong>Live mandi data</strong> from AGMARKNET via data.gov.in. Market observation: {current.date}.</span>
          {retrievedAtLabel && <span className="text-green-700 ml-auto text-xs">Retrieved: {retrievedAtLabel}</span>}
        </div>
      )}

      {/* LATEST_AVAILABLE provenance bar */}
      {isLatestAvailable && (
        <div className="flex items-center gap-3 bg-teal-50 border border-teal-200 rounded-xl px-4 py-2.5 text-sm text-teal-800">
          <Info className="w-4 h-4 flex-shrink-0" />
          <span>
            <strong>Latest available official data:</strong> Market observation from <strong>{current.date}</strong> ({current.days_old ?? data.data_source?.days_old ?? '?'} days ago) via AGMARKNET (data.gov.in) — not current enough to qualify as LIVE.
          </span>
          {retrievedAtLabel && <span className="text-teal-700 ml-auto text-xs">Retrieved: {retrievedAtLabel}</span>}
        </div>
      )}

      {/* STALE provenance bar */}
      {isStale && (
        <div className="flex items-center gap-3 bg-orange-50 border border-orange-200 rounded-xl px-4 py-2.5 text-sm text-orange-800">
          <Info className="w-4 h-4 flex-shrink-0" />
          <span>
            <strong>STALE:</strong> Market data is too old for current-market intelligence (observed <strong>{current.date}</strong>, {current.days_old ?? data.data_source?.days_old ?? '?'} days ago).
          </span>
          {retrievedAtLabel && <span className="text-orange-700 ml-auto text-xs">Retrieved: {retrievedAtLabel}</span>}
        </div>
      )}

      {/* HISTORICAL_SEED notice */}
      {isHistoricalSeed && (
        <div className="flex items-center gap-3 bg-amber-50 border border-amber-200 rounded-xl px-4 py-2.5 text-sm text-amber-800">
          <Info className="w-4 h-4 flex-shrink-0" />
          <span>Showing <strong>calibrated regional mandi benchmark data</strong> (2020–2026 APMC baseline). Offline resilience mode active.</span>
        </div>
      )}



      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 lg:col-span-1">
          <div className="flex items-center justify-between mb-1">
            <p className="text-sm text-gray-500">{current.market} Mandi &bull; {new Date(current.date).toLocaleDateString()}</p>
            {isOfficialSource && <DataBadge type={badgeType} small />}
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">{formatINR(current.modal_price)}<span className="text-sm text-gray-500 font-normal ml-1">/ {current.unit}</span></h2>
          <div className="space-y-3 pt-4 border-t border-gray-100">
            <div className="flex justify-between text-sm"><span className="text-gray-600">Min Price</span><span className="font-semibold text-gray-900">{formatINR(current.min_price)}</span></div>
            <div className="flex justify-between text-sm"><span className="text-gray-600">Max Price</span><span className="font-semibold text-gray-900">{formatINR(current.max_price)}</span></div>
            <div className="flex justify-between text-sm"><span className="text-gray-600">Arrivals</span><span className="font-semibold text-gray-900">{current.arrivals_tonnes} tonnes</span></div>
            {isOfficialSource && retrievedAtLabel && (
              <div className="flex justify-between text-sm pt-1 border-t border-gray-100">
                <span className="text-gray-500">Retrieved</span>
                <span className="text-xs text-gray-500">{retrievedAtLabel}</span>
              </div>
            )}
          </div>
          <div className="mt-6 bg-krishi-gold/10 p-4 rounded-lg border border-krishi-gold/20">
            <div className="flex items-center gap-2 text-krishi-gold-dark font-semibold mb-1">
              {data.historical.seasonal_trend.direction === 'INCREASING' ? <TrendingUp className="w-4 h-4" /> : data.historical.seasonal_trend.direction === 'DECREASING' ? <TrendingDown className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
              Seasonal Trend
            </div>
            <p className="text-xs text-gray-700">{data.historical.seasonal_trend.description}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 lg:col-span-2">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-serif font-bold text-xl">{getPriceHistoryTitle(chartPeriod)}</h2>
            <span className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-600">Top {data.historical.statistics.percentile_rank}% all-time</span>
          </div>
          <PriceChart
            data={data.historical.price_series}
            showMean={true}
            meanValue={stats.mean_price}
            height={300}
            period={chartPeriod}
            onPeriodChange={setChartPeriod}
          />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-100">
            <div><p className="text-xs text-gray-500">Historical Avg</p><p className="font-semibold">{formatINR(stats.mean_price)}</p></div>
            <div><p className="text-xs text-gray-500">All-time High</p><p className="font-semibold text-green-600">{formatINR(stats.max_price_all_time)}</p></div>
            <div><p className="text-xs text-gray-500">All-time Low</p><p className="font-semibold text-red-600">{formatINR(stats.min_price_all_time)}</p></div>
            <div><p className="text-xs text-gray-500">Vs Average</p><p className={`font-semibold ${stats.current_vs_avg_pct > 0 ? 'text-green-600' : 'text-red-600'}`}>{stats.current_vs_avg_pct > 0 ? '+' : ''}{stats.current_vs_avg_pct}%</p></div>
          </div>
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-100"><h2 className="font-serif font-bold text-xl">Nearby Mandi Comparison</h2><p className="text-sm text-gray-500 mt-1">Calculated net realization considering transport costs.</p></div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-600"><tr><th className="px-6 py-3">Market</th><th className="px-6 py-3">Modal Price</th><th className="px-6 py-3">Distance</th><th className="px-6 py-3">Transport Cost</th><th className="px-6 py-3 font-bold text-gray-900">Net Price</th></tr></thead>
            <tbody className="divide-y divide-gray-100">
              {data.mandi_comparison.map((m, i) => (
                <tr key={i} className={i === 0 ? "bg-krishi-green/5" : "bg-white hover:bg-gray-50"}>
                  <td className="px-6 py-4 font-medium text-gray-900">{m.market} {i === 0 && <span className="ml-2 text-[10px] bg-krishi-green text-white px-1.5 py-0.5 rounded">BEST</span>}</td>
                  <td className="px-6 py-4">{formatINR(m.modal_price)}</td>
                  <td className="px-6 py-4 text-gray-500">{m.distance_km} km</td>
                  <td className="px-6 py-4 text-red-500">-{formatINR(m.transport_cost_per_q)}</td>
                  <td className="px-6 py-4 font-bold text-gray-900">{formatINR(m.net_price)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-500 border border-gray-200">
        <strong>Data Source:</strong> {data.data_source.provider || data.data_source.type}. {data.data_source.note}
        {isOfficialSource && data.data_source.retrieved_at && (
          <span className="ml-2 text-green-700 font-medium">● Retrieved: {new Date(data.data_source.retrieved_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}</span>
        )}
      </div>
    </div>
  );
}
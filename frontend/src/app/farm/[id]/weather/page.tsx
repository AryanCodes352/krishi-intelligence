'use client';
import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { WeatherIntelligence, FarmProfile } from '@/lib/types';
import { ArrowLeft, CloudRain, Droplets, Thermometer, Wind, MapPin } from 'lucide-react';
import { DataBadge } from '@/components/shared/DataBadge';
import { RiskGauge } from '@/components/shared/RiskGauge';
import { WeatherChart } from '@/components/charts/WeatherChart';

export default function WeatherPage() {
  const params = useParams();
  const router = useRouter();
  const [data, setData] = useState<WeatherIntelligence | null>(null);
  const [farm, setFarm] = useState<FarmProfile | null>(null);

  useEffect(() => {
    const load = async () => {
      if (typeof params.id === 'string') {
        api.getFarm(params.id).then((farmData) => {
          if (farmData) setFarm(farmData);
        }).catch(() => {});
      }
      const res = await api.getWeather(26.8467, 80.9462);
      setData(res);
    };
    load();
  }, [params.id]);

  if (!data) return <div className="p-8 text-center animate-pulse">Loading weather intelligence...</div>;

  const latDisplay = farm?.lat != null ? Number(farm.lat).toFixed(4) : '26.8467';
  const lonDisplay = farm?.lon != null ? Number(farm.lon).toFixed(4) : '80.9462';
  const locationName = farm
    ? `${farm.location ? `${farm.location}, ` : ''}${farm.district}, ${farm.state}`
    : 'Lucknow, Uttar Pradesh';

  return (
    <div className="space-y-6 pb-20 max-w-5xl mx-auto">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      <div>
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-serif font-bold text-krishi-sky flex items-center gap-3">
            <CloudRain className="w-8 h-8" /> Weather Intelligence
          </h1>
          <DataBadge type="LIVE" />
        </div>
        <div className="mt-2 flex items-center text-xs sm:text-sm">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-50/70 border border-blue-100/80 font-medium text-slate-700">
            <MapPin className="w-3.5 h-3.5 text-blue-600 shrink-0" />
            <span>
              {locationName}
              <span className="mx-1.5 text-slate-300">•</span>
              <span className="font-mono text-slate-600">
                {latDisplay}°N, {lonDisplay}°E
              </span>
            </span>
          </div>
        </div>
      </div>

      {/* Current Strip */}
      <div className="bg-white rounded-xl shadow-sm border border-blue-100 p-6 flex flex-wrap gap-8 items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">Current Conditions</p>
          <div className="flex items-end gap-3">
            <span className="text-5xl font-bold text-gray-900">{data.current.temperature_c}°</span>
            <span className="text-lg text-gray-600 mb-1 capitalize">{data.current.description}</span>
          </div>
        </div>
        <div className="flex gap-8">
          <div className="flex items-center gap-2">
            <Droplets className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-xs text-gray-500">Humidity</p>
              <p className="font-semibold">{data.current.humidity_pct}%</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Wind className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Wind</p>
              <p className="font-semibold">{data.current.wind_kmh} km/h</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <CloudRain className="w-5 h-5 text-blue-400" />
            <div>
              <p className="text-xs text-gray-500">Rainfall</p>
              <p className="font-semibold">{data.current.precipitation_mm} mm</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risks */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="font-serif font-bold text-xl mb-6">Agricultural Risk</h2>
          <div className="flex justify-center mb-8">
            <RiskGauge score={data.agricultural_risk.overall_weather_risk} size="large" />
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Rainfall Risk</span>
              <RiskGauge score={data.agricultural_risk.rainfall_risk.score} size="small" />
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Temperature Risk</span>
              <RiskGauge score={data.agricultural_risk.temperature_risk.score} size="small" />
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Humidity Risk</span>
              <RiskGauge score={data.agricultural_risk.humidity_risk.score} size="small" />
            </div>
          </div>
        </div>

        {/* Forecast & History */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="font-serif font-bold text-xl mb-4">7-Day Forecast</h2>
            <div className="flex overflow-x-auto gap-4 pb-2">
              {data.forecast_7day.map((day, i) => {
                const d = new Date(day.date);
                return (
                  <div key={i} className="flex-none w-24 text-center p-3 rounded-lg border border-gray-100 bg-gray-50">
                    <p className="text-xs font-semibold text-gray-600 mb-2">
                      {i === 0 ? 'Today' : d.toLocaleDateString('en-US', { weekday: 'short' })}
                    </p>
                    <div className="text-2xl mb-2">
                      {day.weather_code < 3 ? '☀️' : day.weather_code < 60 ? '☁️' : '🌧️'}
                    </div>
                    <p className="text-sm font-bold text-gray-900">{day.temp_max_c}° <span className="text-gray-400 font-normal">{day.temp_min_c}°</span></p>
                    <p className="text-[10px] text-blue-600 mt-1 flex items-center justify-center gap-1">
                      <Droplets className="w-3 h-3" /> {day.rain_probability_pct}%
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="font-serif font-bold text-xl mb-4">Historical Comparison</h2>
            <div className="mb-4 text-sm text-gray-600">
              <span className="font-semibold text-gray-900">Current Month Rainfall: </span> 
              {data.historical_comparison.current_month_rainfall_mm} mm 
              <span className="ml-2 text-xs">
                ({data.historical_comparison.deviation_pct > 0 ? '+' : ''}{data.historical_comparison.deviation_pct}% vs historical average)
              </span>
            </div>
            <WeatherChart 
              currentMonthRainfall={data.historical_comparison.current_month_rainfall_mm}
              historicalAvgRainfall={data.historical_comparison.historical_avg_rainfall_mm}
              height={200}
            />
          </div>
        </div>
      </div>
      
      <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-500 border border-gray-200">
        <strong>Data Source:</strong> {data.data_source.provider}. Last updated: {new Date(data.data_source.last_updated).toLocaleString()}
      </div>
    </div>
  );
}

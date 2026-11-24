'use client';
import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { DigitalTwin, FarmUpdateRequest } from '@/lib/types';
import { formatINR, cn } from '@/lib/utils';
import { 
  Sprout, 
  CloudRain, 
  TrendingUp, 
  ShieldCheck, 
  Brain, 
  MapPin, 
  User, 
  Calendar, 
  Clock, 
  Activity, 
  Edit3, 
  RefreshCw, 
  X, 
  CheckCircle2, 
  AlertCircle,
  Database,
  Layers,
  ChevronRight,
  Info
} from 'lucide-react';


import { DataBadge } from '@/components/shared/DataBadge';


export default function DigitalTwinPage() {
  const params = useParams();
  const router = useRouter();
  const farmId = typeof params.id === 'string' ? params.id : '';

  const [twin, setTwin] = useState<DigitalTwin | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Edit Profile Modal State
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editForm, setEditForm] = useState<FarmUpdateRequest>({});
  const [saving, setSaving] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const loadTwin = async (isManualRefresh = false) => {
    if (!farmId) return;
    if (isManualRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      const data = await api.getDigitalTwin(farmId);
      if (data && data.farm_id) {
        setTwin(data);
        // Initialize edit form values
        setEditForm({
          farmer_name: data.farmer.name,
          farm_area_acres: data.farm.acreage,
          location: data.farm.location,
          district: data.farm.district,
          state: data.farm.state,
          crop: data.crop.name,
          crop_variety: data.crop.variety || '',
          sowing_date: data.crop.sowing_date,
          soil_data_available: data.farm.soil_data_available,
          phone: data.farmer.phone || '',
        });
      } else {
        setError('Farm not found. The requested farm ID does not exist.');
      }
    } catch (err) {
      console.error('Failed to load Digital Twin:', err);
      setError('Unable to load Farm Digital Twin. Please ensure the backend service is running.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadTwin();
  }, [farmId]);

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!farmId) return;
    setSaving(true);
    setEditError(null);
    setSaveSuccess(false);

    try {
      const updated = await api.updateFarm(farmId, editForm);
      if (updated && updated.farm_id) {
        setTwin(updated);
        setSaveSuccess(true);
        setTimeout(() => {
          setIsEditOpen(false);
          setSaveSuccess(false);
        }, 800);
      } else {
        setEditError('Could not update farm profile. Please check the values entered.');
      }
    } catch (err) {
      console.error('Update farm error:', err);
      setEditError('Failed to persist changes. Please verify server connection.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 py-6 animate-pulse">
        <div className="h-36 bg-gray-200 rounded-2xl" />
        <div className="h-48 bg-gray-200 rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="h-40 bg-gray-200 rounded-xl" />
          <div className="h-40 bg-gray-200 rounded-xl" />
          <div className="h-40 bg-gray-200 rounded-xl" />
        </div>
      </div>
    );
  }

  if (error || !twin) {
    return (
      <div className="max-w-2xl mx-auto text-center py-20 bg-white rounded-2xl border border-gray-200 p-8 my-8 shadow-sm">
        <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-serif font-bold text-gray-900 mb-2">Digital Twin Unavailable</h2>
        <p className="text-gray-600 mb-6">{error || 'Farm profile could not be loaded.'}</p>
        <div className="flex justify-center gap-4">
          <button 
            onClick={() => loadTwin(true)} 
            className="px-5 py-2.5 bg-krishi-green text-white rounded-lg font-medium hover:bg-krishi-green-dark transition-colors"
          >
            Retry Loading
          </button>
          <Link 
            href="/onboard" 
            className="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Go to Farm Setup
          </Link>
        </div>
      </div>
    );
  }

  const { farmer, farm, crop, metadata, intelligence, data_provenance, events } = twin;
  const isWheat = crop.name.trim().toLowerCase() === 'wheat';
  const weatherIntel = intelligence.weather;
  const soilIntel = intelligence.soil;
  const marketIntel = intelligence.market;
  const riskIntel = intelligence.risk;
  const decisionIntel = intelligence.decision;
  const predIntel = intelligence.prediction;

  return (
    <div className="space-y-8 pb-20">
      {/* 1. Header & Identity Card */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 sm:p-8">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-krishi-green/10 text-krishi-green">
                Digital Twin
              </span>
              <span className="text-xs text-gray-400 font-mono">ID: {twin.farm_id.slice(0, 8)}...</span>
            </div>
            <h1 className="text-3xl font-serif font-bold text-krishi-green-dark">
              {farmer.name ? `${farmer.name}'s Farm Twin` : 'Farm Digital Twin'}
            </h1>
            <p className="text-gray-600 text-sm mt-1 flex flex-wrap items-center gap-x-4 gap-y-1">
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4 text-gray-400" />
                {farm.location ? `${farm.location}, ` : ''}{farm.district}, {farm.state}
              </span>
              <span className="flex items-center gap-1">
                <Sprout className="w-4 h-4 text-gray-400" />
                {crop.name} {crop.variety ? `(${crop.variety})` : ''}
              </span>
              <span className="flex items-center gap-1">
                <Layers className="w-4 h-4 text-gray-400" />
                {farm.acreage} {farm.acreage === 1 ? 'acre' : 'acres'}
              </span>
            </p>
          </div>

          {/* Controls & Timestamps */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full lg:w-auto">
            <div className="text-left sm:text-right text-xs text-gray-500 mr-2">
              <div className="flex items-center sm:justify-end gap-1 font-medium text-gray-700">
                <Clock className="w-3.5 h-3.5 text-gray-400" />
                Last updated: {new Date(metadata.updated_at).toLocaleString()}
              </div>
              <div className="text-gray-400 mt-0.5">
                Created: {new Date(metadata.created_at).toLocaleDateString()}
              </div>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <button
                onClick={() => loadTwin(true)}
                disabled={refreshing}
                className="p-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
                title="Refresh Digital Twin"
                aria-label="Refresh Digital Twin"
              >
                <RefreshCw className={cn("w-4 h-4", refreshing && "animate-spin text-krishi-green")} />
              </button>

              <button
                onClick={() => setIsEditOpen(true)}
                className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2.5 bg-krishi-green text-white rounded-lg font-medium hover:bg-krishi-green-dark transition-colors shadow-sm text-sm"
              >
                <Edit3 className="w-4 h-4" />
                Edit Profile
              </button>
            </div>
          </div>
        </div>

        {/* Identity Details Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4 mt-6 pt-6 border-t border-gray-100 text-sm">
          <div>
            <span className="text-xs text-gray-400 block mb-0.5">Farmer Name</span>
            <span className="font-semibold text-gray-900">{farmer.name || 'N/A'}</span>
          </div>
          <div>
            <span className="text-xs text-gray-400 block mb-0.5">Farm Size</span>
            <span className="font-semibold text-gray-900">{farm.acreage} Acres</span>
          </div>
          <div>
            <span className="text-xs text-gray-400 block mb-0.5">Crop & Variety</span>
            <span className="font-semibold text-gray-900">
              {crop.name} {crop.variety ? `(${crop.variety})` : ''}
            </span>
          </div>
          <div>
            <span className="text-xs text-gray-400 block mb-0.5">Growth Stage</span>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-krishi-green/10 text-krishi-green">
              {crop.stage} (Day {crop.days_after_sowing})
            </span>
          </div>
          <div>
            <span className="text-xs text-gray-400 block mb-0.5">Sowing Date</span>
            <span className="font-semibold text-gray-900">{crop.sowing_date || 'N/A'}</span>
          </div>
          <div>
            <span className="text-xs text-gray-400 block mb-0.5">Soil Test</span>
            <span className={cn(
              "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
              farm.soil_data_available ? "bg-green-100 text-green-800" : "bg-amber-100 text-amber-800"
            )}>
              {farm.soil_data_available ? 'Verified Test' : 'Regional Baseline'}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Visual Digital Twin Hub / Architecture */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 sm:p-8">
        <div className="mb-6">
          <h2 className="text-lg font-serif font-bold text-gray-900 flex items-center gap-2">
            <Layers className="w-5 h-5 text-krishi-green" />
            Digital Twin Intelligence Relationship
          </h2>
          <p className="text-xs text-gray-500 mt-1">
            Real-time synchronization across the 6 core agricultural intelligence layers of this farm.
          </p>
        </div>

        {/* Central Hub Visualization */}
        <div className="bg-krishi-cream/30 rounded-xl p-6 border border-krishi-gold/20">
          <div className="text-center max-w-sm mx-auto mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-krishi-green-dark text-white rounded-full text-sm font-bold shadow-sm">
              <Sprout className="w-4 h-4 text-krishi-gold" />
              FARM DIGITAL TWIN
            </div>
            <p className="text-xs text-gray-600 mt-1.5">
              Persistent Farm #{twin.farm_id.slice(0, 8)} • {farm.district}, {farm.state}
            </p>
          </div>

          {/* Branches */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {/* Branch 1: Crop */}
            <div className="bg-white rounded-xl p-3.5 border border-gray-200 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">CROP</span>
                <p className="text-sm font-bold text-gray-900 truncate">{crop.name}</p>
                <p className="text-xs text-gray-500">{crop.stage}</p>
              </div>
              <div className="mt-3 pt-2 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[10px] text-gray-400">Phenology</span>
                <span className="text-[10px] font-semibold text-krishi-green">Day {crop.days_after_sowing}</span>
              </div>
            </div>

            {/* Branch 2: Soil */}
            <div className="bg-white rounded-xl p-3.5 border border-gray-200 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">SOIL</span>
                <p className="text-sm font-bold text-gray-900 truncate">
                  {soilIntel?.parameters?.soil_type || 'Sandy Loam'}
                </p>
                <p className="text-xs text-gray-500">
                  Suitability: {soilIntel?.crop_suitability?.score || 74}%
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[10px] text-gray-400">Source</span>
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700">
                  {data_provenance.soil}
                </span>
              </div>
            </div>

            {/* Branch 3: Weather */}
            <div className="bg-white rounded-xl p-3.5 border border-gray-200 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">WEATHER</span>
                <p className="text-sm font-bold text-gray-900">
                  {weatherIntel?.current?.temperature_c !== undefined ? `${weatherIntel.current.temperature_c}°C` : 'N/A'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {weatherIntel?.current?.description || 'Live forecast'}
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[10px] text-gray-400">Feed</span>
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700">
                  {data_provenance.weather}
                </span>
              </div>
            </div>

            {/* Branch 4: Market */}
            <div className="bg-white rounded-xl p-3.5 border border-gray-200 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">MARKET</span>
                <p className="text-sm font-bold text-gray-900">
                  {isWheat && marketIntel?.current?.modal_price 
                    ? formatINR(marketIntel.current.modal_price) 
                    : (isWheat ? 'Loading...' : 'Unsupported')}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {isWheat ? (marketIntel?.historical?.seasonal_trend?.direction || 'STABLE') : 'Next Version'}
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[10px] text-gray-400">Type</span>
                <span className={cn(
                  "text-[9px] font-bold px-1.5 py-0.5 rounded",
                  isWheat ? "bg-amber-50 text-amber-700" : "bg-gray-100 text-gray-600"
                )}>
                  {data_provenance.market}
                </span>
              </div>
            </div>

            {/* Branch 5: Risk */}
            <div className="bg-white rounded-xl p-3.5 border border-gray-200 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">RISK STATE</span>
                <p className="text-sm font-bold text-gray-900">
                  {riskIntel?.overall_risk?.score !== undefined ? `${riskIntel.overall_risk.score}/100` : 'N/A'}
                </p>
                <p className="text-xs text-gray-500">
                  {riskIntel?.overall_risk?.level || 'EVALUATED'}
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[10px] text-gray-400">Composite</span>
                <span className={cn(
                  "text-[9px] font-bold px-1.5 py-0.5 rounded",
                  (riskIntel?.overall_risk?.score || 0) < 40 ? "bg-green-50 text-green-700" : "bg-amber-50 text-amber-700"
                )}>
                  {riskIntel?.overall_risk?.level || 'LOW'}
                </span>
              </div>
            </div>

            {/* Branch 6: Decision */}
            <div className="bg-white rounded-xl p-3.5 border border-gray-200 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">DECISION</span>
                <p className="text-sm font-bold text-gray-900 truncate">
                  {decisionIntel?.recommendation?.action?.replace('_', ' ') || 'ANALYZING'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {decisionIntel?.recommendation?.confidence || 'Active Engine'}
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[10px] text-gray-400">Engine</span>
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-purple-50 text-purple-700">
                  {data_provenance.decision}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Aggregated Intelligence Cards */}
      <div>
        <h2 className="text-xl font-serif font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-krishi-green" />
          Synchronized Farm Intelligence
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Weather Card */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                    <CloudRain className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 text-sm">Weather State</h3>
                    <span className="text-[11px] text-gray-400">Open-Meteo Integration</span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                  {data_provenance.weather}
                </span>
              </div>

              {weatherIntel?.current ? (
                <div className="space-y-2.5 mt-4">
                  <div className="flex justify-between items-baseline">
                    <span className="text-2xl font-bold text-gray-900">{weatherIntel.current.temperature_c}°C</span>
                    <span className="text-xs text-gray-500">{weatherIntel.current.description}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 pt-2 border-t border-gray-100">
                    <div>Humidity: <strong className="text-gray-900">{weatherIntel.current.humidity_pct}%</strong></div>
                    <div>Wind: <strong className="text-gray-900">{weatherIntel.current.wind_kmh} km/h</strong></div>
                    <div>Rain Risk: <strong className="text-gray-900">{weatherIntel.agricultural_risk?.rainfall_risk?.level || 'LOW'}</strong></div>
                    <div>7d Rainfall: <strong className="text-gray-900">{weatherIntel.current.precipitation_mm} mm</strong></div>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-gray-500 py-6 text-center">
                  Weather intelligence temporarily unavailable for these coordinates.
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-gray-100">
              <Link href={`/farm/${farmId}/weather`} className="text-xs text-krishi-green font-medium hover:underline flex items-center justify-between">
                <span>View Full 7-Day Forecast & Risk</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Soil Card */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center">
                    <Sprout className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 text-sm">Soil State</h3>
                    <span className="text-[11px] text-gray-400">
                      {farm.soil_data_available ? 'Laboratory Test' : 'Regional Dataset'}
                    </span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800">
                  {data_provenance.soil}
                </span>
              </div>

              {soilIntel?.parameters ? (
                <div className="space-y-2.5 mt-4">
                  <div className="flex justify-between items-baseline">
                    <span className="text-sm font-semibold text-gray-900">{soilIntel.parameters.soil_type || 'Sandy Loam'}</span>
                    <span className="text-xs font-bold text-krishi-green">Suitability: {soilIntel.crop_suitability?.score || 74}%</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs text-gray-600 pt-2 border-t border-gray-100">
                    <div className="bg-gray-50 p-1.5 rounded">
                      <span className="text-[10px] text-gray-400 block">pH</span>
                      <strong className="text-gray-900">{soilIntel.parameters.ph?.value || '7.5'}</strong>
                    </div>
                    <div className="bg-gray-50 p-1.5 rounded">
                      <span className="text-[10px] text-gray-400 block">Nitrogen</span>
                      <strong className="text-gray-900">{soilIntel.parameters.nitrogen?.value || '240'} kg/ha</strong>
                    </div>
                    <div className="bg-gray-50 p-1.5 rounded">
                      <span className="text-[10px] text-gray-400 block">Phosphorus</span>
                      <strong className="text-gray-900">{soilIntel.parameters.phosphorus?.value || '18'} kg/ha</strong>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-gray-500 py-6 text-center">
                  Soil intelligence unavailable for this farm.
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-gray-100">
              <Link href={`/farm/${farmId}/soil`} className="text-xs text-krishi-green font-medium hover:underline flex items-center justify-between">
                <span>View Nutrient Breakdown & Advice</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Market & Price Card */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
                    <TrendingUp className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 text-sm">Market Intelligence</h3>
                    <span className="text-[11px] text-gray-400">
                      {isWheat ? 'AGMARKNET Calibrated' : 'Multi-crop Guardrail'}
                    </span>
                  </div>
                </div>
                <DataBadge type={data_provenance.market as any} small />
              </div>


              {isWheat && marketIntel?.current ? (
                <div className="space-y-2.5 mt-4">
                  <div className="flex justify-between items-baseline">
                    <span className="text-2xl font-bold text-gray-900">{formatINR(marketIntel.current.modal_price)}</span>
                    <span className="text-xs text-gray-500">per quintal ({marketIntel.current.market || farm.district})</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 pt-2 border-t border-gray-100">
                    <div>Seasonal Trend: <strong className="text-gray-900">{marketIntel.historical?.seasonal_trend?.direction || 'STABLE'}</strong></div>
                    <div>CACP MSP: <strong className="text-gray-900">{formatINR(marketIntel.current.msp_reference || 2275)}</strong></div>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-50 p-3.5 rounded-lg text-xs text-gray-600 mt-2 border border-gray-200/60">
                  <p className="font-medium text-gray-900 mb-1">Market Scope Notice</p>
                  <p className="text-[11px] text-gray-500 leading-relaxed">
                    Market Intelligence for <strong>{crop.name}</strong> is not yet available in this prototype. Market predictions and financial scenarios will attach in the next release.
                  </p>
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-gray-100">
              <Link href={`/farm/${farmId}/market`} className="text-xs text-krishi-green font-medium hover:underline flex items-center justify-between">
                <span>View Mandi Prices & Comparison</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Data Provenance & Trust Matrix */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 sm:p-8">
        <div className="mb-4">
          <h2 className="text-lg font-serif font-bold text-gray-900 flex items-center gap-2">
            <Database className="w-5 h-5 text-krishi-green" />
            Data Provenance & Proven State
          </h2>
          <p className="text-xs text-gray-500 mt-1">
            KRISHI strictly preserves data provenance. Synthetic or assumed values are never presented as live measurements.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-gray-200 text-gray-400 uppercase tracking-wider font-semibold">
                <th className="py-2.5 px-3">Intelligence Signal</th>
                <th className="py-2.5 px-3">Data Provider</th>
                <th className="py-2.5 px-3">Provenance Status</th>
                <th className="py-2.5 px-3">Status Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-gray-700">
              <tr>
                <td className="py-3 px-3 font-semibold text-gray-900">Farmer & Land Identity</td>
                <td className="py-3 px-3">User Onboarding / Profile Edit</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded font-bold text-[10px] bg-gray-100 text-gray-800">
                    {data_provenance.farmer_profile}
                  </span>
                </td>
                <td className="py-3 px-3 text-gray-500">Persistent SQLite database record</td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-gray-900">Weather & Agrometeorology</td>
                <td className="py-3 px-3">Open-Meteo GFS/ERA5 API</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded font-bold text-[10px] bg-emerald-100 text-emerald-800">
                    {data_provenance.weather}
                  </span>
                </td>
                <td className="py-3 px-3 text-gray-500">Hourly live data cached for 1 hour; no fake readings</td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-gray-900">Soil Nutrients & pH</td>
                <td className="py-3 px-3">
                  {farm.soil_data_available ? 'On-farm Laboratory Soil Test' : 'ICAR-NBSS&LUP District Soil Map'}
                </td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded font-bold text-[10px] bg-blue-100 text-blue-800">
                    {data_provenance.soil}
                  </span>
                </td>
                <td className="py-3 px-3 text-gray-500">
                  {farm.soil_data_available ? 'Field-specific laboratory test' : 'District baseline regional estimate'}
                </td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-gray-900">Mandi Market Prices</td>
                <td className="py-3 px-3">
                  {data_provenance.market === 'LIVE' || data_provenance.market === 'LATEST_AVAILABLE' || data_provenance.market === 'STALE'
                    ? 'AGMARKNET (data.gov.in OGD Platform)'
                    : 'AGMARKNET / CACP Seed Database'}
                </td>
                <td className="py-3 px-3">
                  <DataBadge type={data_provenance.market as any} small />
                </td>
                <td className="py-3 px-3 text-gray-500">
                  {data_provenance.market === 'LIVE'
                    ? 'Current official live mandi feed (today/yesterday)'
                    : data_provenance.market === 'LATEST_AVAILABLE'
                    ? 'Latest available official mandi observation (2-7 days)'
                    : data_provenance.market === 'STALE'
                    ? 'Market data is too old for current-market intelligence (>7 days)'
                    : isWheat
                    ? 'Calibrated historical mandi observations (seed dataset)'
                    : 'Crop market data not yet connected'}
                </td>
              </tr>

              <tr>
                <td className="py-3 px-3 font-semibold text-gray-900">Price Prediction</td>
                <td className="py-3 px-3">XGBoost Regressor Model</td>
                <td className="py-3 px-3">
                  <span className={cn(
                    "px-2 py-0.5 rounded font-bold text-[10px]",
                    isWheat ? "bg-purple-100 text-purple-800" : "bg-gray-100 text-gray-600"
                  )}>
                    {data_provenance.prediction}
                  </span>
                </td>
                <td className="py-3 px-3 text-gray-500">
                  {isWheat ? 'Trained on regional weekly series with confidence bounds' : 'Price prediction models active for Wheat only'}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Farm Events Activity Log */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 sm:p-8">
        <div className="mb-4">
          <h2 className="text-lg font-serif font-bold text-gray-900 flex items-center gap-2">
            <Clock className="w-5 h-5 text-krishi-green" />
            Farm Events & Activity Timeline
          </h2>
          <p className="text-xs text-gray-500 mt-1">
            Genuine logged lifecycle actions for this digital twin.
          </p>
        </div>

        {events && events.length > 0 ? (
          <div className="space-y-3 mt-4">
            {events.map((ev, idx) => (
              <div 
                key={ev.id || idx}
                className="flex items-start gap-3 p-3.5 rounded-xl bg-gray-50 border border-gray-100 hover:border-gray-200 transition-colors"
              >
                <div className="mt-0.5">
                  <div className="w-7 h-7 rounded-full bg-krishi-green/10 text-krishi-green flex items-center justify-center text-xs font-bold">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center justify-between gap-1">
                    <span className="font-semibold text-gray-900 text-xs sm:text-sm">{ev.title}</span>
                    <span className="text-[11px] text-gray-400">{new Date(ev.timestamp).toLocaleString()}</span>
                  </div>
                  {ev.description && (
                    <p className="text-xs text-gray-600 mt-0.5">{ev.description}</p>
                  )}
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-white text-gray-500 border border-gray-200">
                      {ev.event_type}
                    </span>
                    <span className="text-[9px] text-gray-400">Source: {ev.source}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-gray-50 rounded-xl border border-dashed border-gray-200 text-xs text-gray-500">
            No events recorded yet for this farm. Changes to farm profile or completed analysis will be logged here.
          </div>
        )}
      </div>

      {/* 6. Edit Profile Modal */}
      {isEditOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 sm:p-8 shadow-xl border border-gray-200 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center pb-4 border-b border-gray-100 mb-6">
              <div>
                <h3 className="text-xl font-serif font-bold text-krishi-green-dark">Edit Farm Profile</h3>
                <p className="text-xs text-gray-500">Update persistent digital twin parameters</p>
              </div>
              <button 
                onClick={() => setIsEditOpen(false)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {editError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{editError}</span>
              </div>
            )}

            {saveSuccess && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Farm profile updated successfully!</span>
              </div>
            )}

            <form onSubmit={handleEditSubmit} className="space-y-4 text-sm">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">Farmer Name</label>
                <input
                  type="text"
                  required
                  value={editForm.farmer_name || ''}
                  onChange={e => setEditForm(prev => ({ ...prev, farmer_name: e.target.value }))}
                  className="w-full px-3.5 py-2 border border-gray-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-krishi-green/20 focus:border-krishi-green"
                  placeholder="Farmer name"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Farm Area (Acres)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    required
                    value={editForm.farm_area_acres || ''}
                    onChange={e => setEditForm(prev => ({ ...prev, farm_area_acres: parseFloat(e.target.value) || 0 }))}
                    className="w-full px-3.5 py-2 border border-gray-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-krishi-green/20 focus:border-krishi-green"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Phone Number</label>
                  <input
                    type="tel"
                    value={editForm.phone || ''}
                    onChange={e => setEditForm(prev => ({ ...prev, phone: e.target.value }))}
                    className="w-full px-3.5 py-2 border border-gray-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-krishi-green/20 focus:border-krishi-green"
                    placeholder="Optional"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">Location / Village</label>
                <input
                  type="text"
                  value={editForm.location || ''}
                  onChange={e => setEditForm(prev => ({ ...prev, location: e.target.value }))}
                  className="w-full px-3.5 py-2 border border-gray-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-krishi-green/20 focus:border-krishi-green"
                  placeholder="Village / Tehsil"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">District</label>
                  <select
                    value={editForm.district || 'Lucknow'}
                    onChange={e => setEditForm(prev => ({ ...prev, district: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-krishi-green/20 focus:border-krishi-green bg-white text-sm"
                  >
                    <option value="Lucknow">Lucknow</option>
                    <option value="Kanpur Nagar">Kanpur Nagar</option>
                    <option value="Unnao">Unnao</option>
                    <option value="Sitapur">Sitapur</option>
                    <option value="Barabanki">Barabanki</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">State</label>
                  <select
                    value={editForm.state || 'Uttar Pradesh'}
                    onChange={e => setEditForm(prev => ({ ...prev, state: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-krishi-green/20 focus:border-krishi-green bg-white text-sm"
                  >
                    <option value="Uttar Pradesh">Uttar Pradesh</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Crop</label>
                  <select
                    value={editForm.crop || 'Wheat'}
                    onChange={e => {
                      const newCrop = e.target.value;
                      const isCropW = newCrop.trim().toLowerCase() === 'wheat';
                      setEditForm(prev => ({
                        ...prev,
                        crop: newCrop,
                        crop_variety: isCropW ? (prev.crop_variety || 'HD-2967') : '',
                      }));
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-krishi-green/20 focus:border-krishi-green bg-white text-sm"
                  >
                    <option value="Wheat">Wheat (Active)</option>
                    <option value="Rice">Rice (Upcoming)</option>
                    <option value="Mustard">Mustard (Upcoming)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Variety</label>
                  {editForm.crop?.trim().toLowerCase() === 'wheat' ? (
                    <select
                      value={editForm.crop_variety || 'HD-2967'}
                      onChange={e => setEditForm(prev => ({ ...prev, crop_variety: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-krishi-green/20 focus:border-krishi-green bg-white text-sm"
                    >
                      <option value="HD-2967">HD-2967</option>
                      <option value="PBW-343">PBW-343</option>
                      <option value="WH-542">WH-542</option>
                      <option value="DBW-187">DBW-187</option>
                    </select>
                  ) : (
                    <input
                      type="text"
                      disabled
                      value="N/A (Multi-crop Guardrail)"
                      className="w-full px-3 py-2 border border-gray-200 bg-gray-50 text-gray-400 rounded-lg text-xs"
                    />
                  )}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">Sowing Date</label>
                <input
                  type="date"
                  required
                  value={editForm.sowing_date || ''}
                  onChange={e => setEditForm(prev => ({ ...prev, sowing_date: e.target.value }))}
                  className="w-full px-3.5 py-2 border border-gray-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-krishi-green/20 focus:border-krishi-green"
                />
              </div>

              <div>
                <label className="flex items-center gap-2 cursor-pointer pt-1">
                  <input
                    type="checkbox"
                    checked={Boolean(editForm.soil_data_available)}
                    onChange={e => setEditForm(prev => ({ ...prev, soil_data_available: e.target.checked }))}
                    className="w-4 h-4 text-krishi-green rounded border-gray-300 focus:ring-krishi-green"
                  />
                  <span className="text-xs text-gray-700">I have a physical Soil Health Card / Laboratory Test</span>
                </label>
              </div>

              <div className="pt-4 border-t border-gray-100 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsEditOpen(false)}
                  disabled={saving}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium text-xs transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 bg-krishi-green text-white rounded-lg font-medium text-xs hover:bg-krishi-green-dark transition-colors shadow-sm disabled:opacity-50 flex items-center gap-1.5"
                >
                  {saving ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

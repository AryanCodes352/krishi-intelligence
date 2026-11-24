'use client';
import React, { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { SoilIntelligence, FarmProfile, SoilExtractionResponse } from '@/lib/types';
import { 
  ArrowLeft, 
  Sprout, 
  Upload, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  AlertTriangle, 
  X, 
  Loader2, 
  Info, 
  Calendar, 
  Check, 
  Sparkles,
  Edit3,
  Layers
} from 'lucide-react';
import { DataBadge } from '@/components/shared/DataBadge';
import { RiskBarChart } from '@/components/charts/RiskBarChart';
import { cn } from '@/lib/utils';

interface ParamFieldMeta {
  key: string;
  label: string;
  unit: string;
  min?: number;
  max?: number;
  placeholder: string;
  category: 'core' | 'micro';
}

const PARAM_METAS: ParamFieldMeta[] = [
  { key: 'ph', label: 'Soil pH', unit: '', min: 0, max: 14, placeholder: 'e.g. 7.2', category: 'core' },
  { key: 'nitrogen', label: 'Available Nitrogen (N)', unit: 'kg/ha', min: 0, placeholder: 'e.g. 240', category: 'core' },
  { key: 'phosphorus', label: 'Available Phosphorus (P)', unit: 'kg/ha', min: 0, placeholder: 'e.g. 18', category: 'core' },
  { key: 'potassium', label: 'Available Potassium (K)', unit: 'kg/ha', min: 0, placeholder: 'e.g. 220', category: 'core' },
  { key: 'organic_carbon', label: 'Organic Carbon (OC)', unit: '%', min: 0, max: 100, placeholder: 'e.g. 0.55', category: 'core' },
  { key: 'ec', label: 'Electrical Conductivity (EC)', unit: 'dS/m', min: 0, placeholder: 'e.g. 0.8', category: 'core' },
  { key: 'sulphur', label: 'Available Sulphur (S)', unit: 'ppm', min: 0, placeholder: 'e.g. 12.5', category: 'micro' },
  { key: 'zinc', label: 'Available Zinc (Zn)', unit: 'ppm', min: 0, placeholder: 'e.g. 0.85', category: 'micro' },
  { key: 'iron', label: 'Available Iron (Fe)', unit: 'ppm', min: 0, placeholder: 'e.g. 6.2', category: 'micro' },
  { key: 'copper', label: 'Available Copper (Cu)', unit: 'ppm', min: 0, placeholder: 'e.g. 0.45', category: 'micro' },
  { key: 'manganese', label: 'Available Manganese (Mn)', unit: 'ppm', min: 0, placeholder: 'e.g. 3.1', category: 'micro' },
  { key: 'boron', label: 'Available Boron (B)', unit: 'ppm', min: 0, placeholder: 'e.g. 0.6', category: 'micro' },
];

export default function SoilPage() {
  const params = useParams();
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [data, setData] = useState<SoilIntelligence | null>(null);
  const [farm, setFarm] = useState<FarmProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Upload Modal State
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Review & Confirmation Modal State
  const [isReviewOpen, setIsReviewOpen] = useState(false);
  const [extraction, setExtraction] = useState<SoilExtractionResponse | null>(null);
  const [reviewValues, setReviewValues] = useState<Record<string, string>>({});
  const [fieldSources, setFieldSources] = useState<Record<string, string>>({});
  const [textureVal, setTextureVal] = useState<string>('Sandy Loam');
  const [testDateVal, setTestDateVal] = useState<string>(new Date().toISOString().split('T')[0]);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [confirming, setConfirming] = useState(false);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const [successToast, setSuccessToast] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    if (typeof params.id === 'string') {
      const farmRes = await api.getFarm(params.id);
      if (farmRes) {
        setFarm(farmRes);
        const res = await api.getSoil(
          farmRes.district,
          farmRes.state,
          farmRes.farm_id,
          farmRes.crop,
          farmRes.crop_stage
        );
        setData(res);
        setLoading(false);
        return;
      }
    }
    const res = await api.getSoil('Lucknow', 'Uttar Pradesh');
    setData(res);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [params.id]);

  // Handle File Selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setUploadError(null);
    if (!file) {
      setSelectedFile(null);
      return;
    }
    const allowed = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!allowed.includes(file.type)) {
      setUploadError('Invalid file type. Please upload a PDF, JPG, or PNG document.');
      setSelectedFile(null);
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File size exceeds 10MB limit. Please upload a smaller file.');
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
  };

  // Upload and Extract via OCR
  const handleUploadAndExtract = async () => {
    if (!selectedFile || !farm) return;
    setUploading(true);
    setUploadError(null);

    try {
      const result = await api.uploadSoilDocument(farm.farm_id, selectedFile);
      if (!result) {
        throw new Error('No response received from OCR service.');
      }
      setExtraction(result);

      // Pre-fill review form with extracted values
      const initialValues: Record<string, string> = {};
      const initialSources: Record<string, string> = {};

      PARAM_METAS.forEach((meta) => {
        const extracted = result.parameters?.[meta.key];
        if (extracted && extracted.value !== null && extracted.value !== undefined && extracted.valid) {
          initialValues[meta.key] = String(extracted.value);
          initialSources[meta.key] = 'SOIL_HEALTH_CARD';
        } else {
          initialValues[meta.key] = '';
          initialSources[meta.key] = 'FARMER_ENTERED';
        }
      });

      const extractedTexture = result.parameters?.texture?.value || result.parameters?.soil_texture?.value;
      if (extractedTexture && typeof extractedTexture === 'string') {
        setTextureVal(extractedTexture);
      } else {
        setTextureVal(data?.parameters?.soil_type || 'Sandy Loam');
      }

      if (result.test_date) {
        setTestDateVal(result.test_date);
      } else {
        setTestDateVal(new Date().toISOString().split('T')[0]);
      }

      setReviewValues(initialValues);
      setFieldSources(initialSources);
      setValidationErrors({});
      setIsUploadOpen(false);
      setIsReviewOpen(true);
    } catch (err: any) {
      console.error('Soil upload failed:', err);
      setUploadError(err.message || 'Failed to process document. Please verify the file and try again.');
    } finally {
      setUploading(false);
    }
  };

  // Manual Entry Initiation (without uploading a document)
  const handleOpenManualEntry = () => {
    setExtraction(null);
    const initialValues: Record<string, string> = {};
    const initialSources: Record<string, string> = {};

    PARAM_METAS.forEach((meta) => {
      initialValues[meta.key] = '';
      initialSources[meta.key] = 'FARMER_ENTERED';
    });

    setReviewValues(initialValues);
    setFieldSources(initialSources);
    setTextureVal(data?.parameters?.soil_type || 'Sandy Loam');
    setTestDateVal(new Date().toISOString().split('T')[0]);
    setValidationErrors({});
    setIsUploadOpen(false);
    setIsReviewOpen(true);
  };

  // Validate single field
  const validateField = (key: string, valStr: string): string | null => {
    if (!valStr || valStr.trim() === '') return null;
    const num = parseFloat(valStr);
    if (isNaN(num)) return 'Must be a valid number';
    if (key === 'ph') {
      if (num < 0 || num > 14) return 'pH must be between 0.0 and 14.0';
    } else {
      if (num < 0) return 'Value cannot be negative';
    }
    return null;
  };

  // Handle Farmer Value Edit
  const handleValueChange = (key: string, newValue: string) => {
    setReviewValues((prev) => ({ ...prev, [key]: newValue }));
    
    // Once farmer modifies a field, mark provenance as FARMER_ENTERED
    setFieldSources((prev) => ({ ...prev, [key]: 'FARMER_ENTERED' }));

    const error = validateField(key, newValue);
    setValidationErrors((prev) => {
      const next = { ...prev };
      if (error) next[key] = error;
      else delete next[key];
      return next;
    });
  };

  // Confirm and Submit Profile
  const handleConfirmSoilProfile = async () => {
    if (!farm) return;

    // Run full validation check
    const errors: Record<string, string> = {};
    PARAM_METAS.forEach((meta) => {
      const val = reviewValues[meta.key];
      const err = validateField(meta.key, val);
      if (err) errors[meta.key] = err;
    });

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    setConfirming(true);
    setConfirmError(null);

    try {
      const parsedParams: Record<string, any> = {
        soil_texture: textureVal.trim() || undefined,
        texture: textureVal.trim() || undefined,
      };

      PARAM_METAS.forEach((meta) => {
        const valStr = reviewValues[meta.key];
        if (valStr && valStr.trim() !== '') {
          parsedParams[meta.key] = parseFloat(valStr);
        } else {
          parsedParams[meta.key] = null;
        }
      });

      const payload = {
        farm_id: farm.farm_id,
        document_id: extraction?.document_id,
        test_date: testDateVal || undefined,
        parameters: parsedParams,
        field_sources: fieldSources,
      };

      const res = await api.confirmSoilProfile(payload);
      if (!res) {
        throw new Error('Failed to confirm soil profile.');
      }

      setIsReviewOpen(false);
      setSuccessToast('Soil Health Card confirmed successfully! Farm Digital Twin updated.');
      setTimeout(() => setSuccessToast(null), 6000);

      // Reload fresh data from backend
      await loadData();
    } catch (err: any) {
      console.error('Confirmation error:', err);
      setConfirmError(err.message || 'Failed to confirm soil data. Please try again.');
    } finally {
      setConfirming(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="p-12 text-center space-y-4">
        <Loader2 className="w-8 h-8 animate-spin mx-auto text-krishi-green" />
        <p className="text-gray-600 font-medium">Loading soil intelligence...</p>
      </div>
    );
  }

  const isConfirmedProfile = ['SOIL_HEALTH_CARD', 'FARMER_ENTERED'].includes(data.data_source.type);
  const coreParams = PARAM_METAS.filter((m) => m.category === 'core');
  const microParams = PARAM_METAS.filter((m) => m.category === 'micro');

  return (
    <div className="space-y-6 pb-20 max-w-5xl mx-auto">
      {/* Back Navigation */}
      <button 
        onClick={() => router.back()} 
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      {/* Success Notification Banner */}
      {successToast && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl flex items-center justify-between shadow-xs animate-in fade-in slide-in-from-top-2">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <span className="font-medium text-sm">{successToast}</span>
          </div>
          <button onClick={() => setSuccessToast(null)} className="text-emerald-600 hover:text-emerald-900">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Header Section */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-krishi-soil/10 flex items-center justify-center text-krishi-soil">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-serif font-bold text-gray-900">Granular Soil Intelligence</h1>
              {farm && (
                <p className="text-sm text-gray-500 mt-0.5">
                  {farm.farmer_name ? `${farm.farmer_name} • ` : ''}{farm.crop} ({farm.farm_area_acres} {Number(farm.farm_area_acres) === 1 ? 'acre' : 'acres'}) • Crop Stage: <strong className="text-gray-800">{farm.crop_stage}</strong>
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <DataBadge type={data.data_source.type as any} />
          {farm && (
            <button
              onClick={() => setIsUploadOpen(true)}
              className={cn(
                "px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all shadow-xs",
                isConfirmedProfile
                  ? "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
                  : "bg-krishi-green text-white hover:bg-krishi-green-dark"
              )}
            >
              <Upload className="w-4 h-4" />
              {isConfirmedProfile ? 'Update / Upload New Card' : 'Upload Soil Health Card'}
            </button>
          )}
        </div>
      </div>

      {/* Provenance Context Banner */}
      {isConfirmedProfile ? (
        <div className="bg-emerald-50/80 border border-emerald-200 p-4 rounded-xl flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
          <div className="text-sm text-emerald-950">
            <span className="font-semibold text-emerald-900">
              {data.data_source.type === 'SOIL_HEALTH_CARD' ? 'Verified Laboratory Soil Profile Active' : 'Farmer-Entered Soil Profile Active'}
            </span>
            <p className="text-emerald-800 text-xs mt-0.5">
              Source: {data.data_source.provider}. {data.data_source.test_date ? `Sample tested on ${data.data_source.test_date}. ` : ''}
              Nutrient suitability and stage-specific fertilizer advisories are calibrated to this farm.
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-amber-50/80 border border-amber-200 p-4 rounded-xl flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="text-sm text-amber-950">
              <span className="font-semibold text-amber-900">Regional District Baseline Active (ICAR-NBSS&LUP)</span>
              <p className="text-amber-800 text-xs mt-0.5">
                Current figures are regional district estimates for {farm?.district || 'this area'}. Upload your official Soil Health Card to unlock precision, farm-specific soil intelligence.
              </p>
            </div>
          </div>
          {farm && (
            <button
              onClick={() => setIsUploadOpen(true)}
              className="text-xs bg-amber-600 text-white font-medium px-3 py-1.5 rounded-md hover:bg-amber-700 shrink-0 whitespace-nowrap"
            >
              Upload Card
            </button>
          )}
        </div>
      )}

      {/* Main Grid: Parameters & Suitability */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Nutrient Parameters Card */}
        <div className="md:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col justify-between">
          <div>
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
              <div>
                <h2 className="font-serif font-bold text-lg text-gray-800">Primary Soil Parameters</h2>
                <p className="text-xs text-gray-500">Core nutrients & physicochemical status</p>
              </div>
              <span className="text-xs font-medium px-2.5 py-1 rounded bg-white border border-gray-200 text-gray-700">
                Texture: {data.parameters.soil_type || data.parameters.texture || 'Sandy Loam'}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-gray-50/70 text-gray-600 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="px-5 py-3">Parameter</th>
                    <th className="px-5 py-3">Measurement</th>
                    <th className="px-5 py-3">Evaluation</th>
                    <th className="px-5 py-3">Optimal Target</th>
                    <th className="px-5 py-3 text-right">Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {coreParams.map((meta) => {
                    const param = (data.parameters as any)[meta.key];
                    const val = param?.value;
                    const hasVal = val !== null && val !== undefined;
                    const status = param?.status || (hasVal ? 'GOOD' : 'UNAVAILABLE');
                    const source = param?.source || data.data_source.type;

                    return (
                      <tr key={meta.key} className="bg-white hover:bg-gray-50/80 transition-colors">
                        <td className="px-5 py-3.5 font-medium text-gray-900 flex items-center gap-1.5">
                          {meta.label}
                        </td>
                        <td className="px-5 py-3.5">
                          {hasVal ? (
                            <span className="font-semibold text-gray-800">
                              {val} {param?.unit || meta.unit}
                            </span>
                          ) : (
                            <span className="text-xs italic text-gray-400">Not recorded</span>
                          )}
                        </td>
                        <td className="px-5 py-3.5">
                          <span className={cn(
                            "px-2 py-0.5 rounded text-xs font-semibold inline-block",
                            status === 'GOOD' ? 'bg-green-100 text-green-800 border border-green-200' :
                            status === 'MEDIUM' || status === 'MODERATE' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                            status === 'LOW' || status === 'HIGH' || status === 'POOR' ? 'bg-orange-100 text-orange-800 border border-orange-200' :
                            'bg-gray-100 text-gray-600 border border-gray-200'
                          )}>
                            {status}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 text-xs text-gray-500">
                          {param?.optimal_min !== undefined && param?.optimal_max !== undefined ? (
                            `${param.optimal_min} – ${param.optimal_max} ${param.unit || meta.unit}`
                          ) : (
                            'N/A'
                          )}
                        </td>
                        <td className="px-5 py-3.5 text-right">
                          <span className={cn(
                            "text-[10px] font-semibold px-2 py-0.5 rounded-full border",
                            source === 'SOIL_HEALTH_CARD' ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                            source === 'FARMER_ENTERED' ? "bg-sky-50 text-sky-700 border-sky-200" :
                            "bg-orange-50 text-orange-700 border-orange-200"
                          )}>
                            {source.replace(/_/g, ' ')}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Micronutrients Section if Available */}
          {microParams.some((m) => (data.parameters as any)[m.key]?.value !== undefined && (data.parameters as any)[m.key]?.value !== null) && (
            <div className="border-t border-gray-200 bg-gray-50/50 p-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-krishi-green" /> Micronutrient Profile (ppm)
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {microParams.map((meta) => {
                  const param = (data.parameters as any)[meta.key];
                  if (!param || param.value === null || param.value === undefined) return null;
                  return (
                    <div key={meta.key} className="bg-white p-2.5 rounded-lg border border-gray-200 text-xs shadow-2xs">
                      <div className="text-gray-500 font-medium">{meta.label}</div>
                      <div className="flex items-center justify-between mt-1">
                        <span className="font-bold text-gray-800">{param.value} {param.unit || 'ppm'}</span>
                        <span className={cn(
                          "px-1.5 py-0.2 rounded text-[10px] font-semibold",
                          param.status === 'GOOD' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'
                        )}>
                          {param.status}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Suitability & Risk */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 text-center">
            <h2 className="font-serif font-bold text-gray-800 mb-1">Crop Soil Suitability</h2>
            <p className="text-xs text-gray-500 mb-4">{data.crop_suitability.provenance_note || 'Soil-crop compatibility index'}</p>
            
            <div className="relative w-32 h-32 mx-auto mb-4">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="64" cy="64" r="60" stroke="#f3f4f6" strokeWidth="8" fill="none" />
                <circle 
                  cx="64" 
                  cy="64" 
                  r="60" 
                  stroke="#16a34a" 
                  strokeWidth="8" 
                  fill="none" 
                  strokeDasharray="377" 
                  strokeDashoffset={377 - (data.crop_suitability.score / 100) * 377} 
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="text-3xl font-bold text-gray-900">{data.crop_suitability.score}</span>
                <span className="text-xs text-gray-500">/ 100</span>
              </div>
            </div>
            <p className="font-medium text-green-700">{data.crop_suitability.label}</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h2 className="font-serif font-bold text-gray-800 mb-3">Suitability Factors</h2>
            <RiskBarChart 
              factors={data.crop_suitability.factors.map(f => ({ 
                parameter: f.parameter, 
                score: f.score, 
                max_score: f.max_score 
              }))} 
            />
          </div>
        </div>
      </div>

      {/* Stage-Specific Recommendations */}
      <div className="bg-krishi-cream p-6 rounded-xl border border-krishi-soil/20 shadow-xs">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-krishi-soil" />
            <h2 className="font-serif font-bold text-xl text-krishi-soil">Field Management Advisories</h2>
          </div>
          {farm && (
            <span className="text-xs text-gray-700 bg-white/80 px-2.5 py-1 rounded-md border border-krishi-soil/20 font-medium">
              Crop Stage: {farm.crop_stage}
            </span>
          )}
        </div>
        <ul className="space-y-2.5 text-gray-700 text-sm">
          {data.recommendations.map((rec, i) => (
            <li key={i} className="flex items-start gap-2.5">
              <span className="w-1.5 h-1.5 rounded-full bg-krishi-soil mt-2 shrink-0" />
              <span>{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Data Source Footer */}
      <div className="bg-gray-50 p-4 rounded-lg text-xs text-gray-500 border border-gray-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div>
          <strong>Data Provenance:</strong> {data.data_source.provider} ({data.data_source.type}). {data.data_source.note}
        </div>
        {data.data_source.test_date && (
          <div className="text-gray-400 shrink-0">
            Test Date: {data.data_source.test_date}
          </div>
        )}
      </div>

      {/* ────────────────────────────────────────────────────────────────── */}
      {/* 1. UPLOAD MODAL */}
      {/* ────────────────────────────────────────────────────────────────── */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-gray-100 relative">
            <button
              onClick={() => { setIsUploadOpen(false); setSelectedFile(null); setUploadError(null); }}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <Upload className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-serif font-bold text-gray-900">Upload Soil Health Card</h3>
                <p className="text-xs text-gray-500">Official Government or Laboratory Soil Test</p>
              </div>
            </div>

            {uploadError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{uploadError}</span>
              </div>
            )}

            <div 
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors",
                selectedFile ? "border-emerald-400 bg-emerald-50/30" : "border-gray-200 hover:border-krishi-green bg-gray-50/50"
              )}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange}
                accept=".pdf,image/jpeg,image/png,image/jpg" 
                className="hidden" 
              />
              {selectedFile ? (
                <div className="space-y-2">
                  <FileText className="w-10 h-10 mx-auto text-emerald-600" />
                  <p className="font-semibold text-gray-800 text-sm">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • {selectedFile.type}</p>
                  <p className="text-xs text-emerald-600 font-medium">Click or drag another file to replace</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="w-10 h-10 mx-auto text-gray-400" />
                  <p className="font-medium text-gray-700 text-sm">Click to browse or drop your document here</p>
                  <p className="text-xs text-gray-400">Supported formats: PDF, JPG, PNG (Max 10MB)</p>
                </div>
              )}
            </div>

            <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-500 flex items-start gap-2">
              <Info className="w-4 h-4 text-gray-400 shrink-0 mt-0.5" />
              <span>
                Our OCR parser scans the Soil Health Card for pH, N, P, K, Organic Carbon, and micronutrients. You will have full opportunity to review and edit all extracted numbers before confirming.
              </span>
            </div>

            <div className="mt-6 flex flex-col sm:flex-row gap-3">
              <button
                onClick={handleUploadAndExtract}
                disabled={!selectedFile || uploading}
                className="flex-1 bg-krishi-green text-white font-medium py-2.5 px-4 rounded-xl hover:bg-krishi-green-dark disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm transition-all"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Extracting Soil Parameters...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Extract with OCR</span>
                  </>
                )}
              </button>
              
              <button
                onClick={handleOpenManualEntry}
                disabled={uploading}
                type="button"
                className="px-4 py-2.5 text-xs font-medium text-gray-600 hover:text-gray-900 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                Enter Manually
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────────────────────────────── */}
      {/* 2. MANDATORY FARMER REVIEW & CONFIRMATION MODAL */}
      {/* ────────────────────────────────────────────────────────────────── */}
      {isReviewOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4 backdrop-blur-xs overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 my-8 shadow-2xl border border-gray-100 max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-gray-100">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-xl font-serif font-bold text-gray-900">Review & Confirm Soil Values</h3>
                  <span className={cn(
                    "text-[10px] font-bold px-2 py-0.5 rounded-full uppercase",
                    extraction ? "bg-emerald-100 text-emerald-800" : "bg-sky-100 text-sky-800"
                  )}>
                    {extraction ? `OCR: ${extraction.ocr_status.replace(/_/g, ' ')}` : 'Manual Entry'}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Please verify extracted numbers against your physical report. You may edit any value or fill in missing fields before confirmation.
                </p>
              </div>
              <button
                onClick={() => setIsReviewOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {confirmError && (
              <div className="my-3 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{confirmError}</span>
              </div>
            )}

            {/* Scrollable Content Body */}
            <div className="overflow-y-auto pr-1 py-4 space-y-5 flex-1">
              {/* Metadata row: Test Date and Texture */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-gray-50 p-3.5 rounded-xl border border-gray-100">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1 flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-gray-500" /> Soil Test Date
                  </label>
                  <input
                    type="date"
                    value={testDateVal}
                    onChange={(e) => setTestDateVal(e.target.value)}
                    className="w-full text-xs bg-white border border-gray-200 rounded-lg px-3 py-2 text-gray-800 focus:outline-hidden focus:ring-2 focus:ring-krishi-green"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Soil Texture Class
                  </label>
                  <select
                    value={textureVal}
                    onChange={(e) => setTextureVal(e.target.value)}
                    className="w-full text-xs bg-white border border-gray-200 rounded-lg px-3 py-2 text-gray-800 focus:outline-hidden focus:ring-2 focus:ring-krishi-green"
                  >
                    <option value="Sandy Loam">Sandy Loam</option>
                    <option value="Loam">Loam</option>
                    <option value="Clay Loam">Clay Loam</option>
                    <option value="Silt Loam">Silt Loam</option>
                    <option value="Clay">Clay</option>
                    <option value="Sandy Clay Loam">Sandy Clay Loam</option>
                    <option value="Silty Clay">Silty Clay</option>
                  </select>
                </div>
              </div>

              {/* Core Macronutrients Table */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-600 mb-2">
                  Primary Parameters (Core Macronutrients & Reaction)
                </h4>
                <div className="border border-gray-200 rounded-xl overflow-hidden">
                  <div className="divide-y divide-gray-100">
                    {coreParams.map((meta) => {
                      const val = reviewValues[meta.key] ?? '';
                      const source = fieldSources[meta.key] || 'FARMER_ENTERED';
                      const err = validationErrors[meta.key];
                      const wasExtracted = extraction?.parameters?.[meta.key]?.value !== undefined && extraction?.parameters?.[meta.key]?.value !== null;

                      return (
                        <div key={meta.key} className="p-3 bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-gray-50/50">
                          <div className="min-w-[140px]">
                            <div className="text-xs font-semibold text-gray-900">{meta.label}</div>
                            <div className="text-[11px] text-gray-400">
                              {meta.unit ? `Unit: ${meta.unit}` : 'Unitless scale'}
                            </div>
                          </div>

                          <div className="flex-1 max-w-xs">
                            <div className="relative">
                              <input
                                type="text"
                                inputMode="decimal"
                                value={val}
                                onChange={(e) => handleValueChange(meta.key, e.target.value)}
                                placeholder={wasExtracted ? meta.placeholder : "Not detected — enter manually"}
                                className={cn(
                                  "w-full text-xs rounded-lg px-3 py-1.5 border font-mono transition-colors",
                                  err ? "border-red-400 bg-red-50/30 text-red-900 focus:ring-red-300" : "border-gray-200 focus:border-krishi-green",
                                  val ? "text-gray-900 font-semibold" : "text-gray-400 italic font-normal"
                                )}
                              />
                            </div>
                            {err && <p className="text-[10px] text-red-600 mt-0.5">{err}</p>}
                          </div>

                          <div className="sm:w-32 flex justify-end">
                            <span className={cn(
                              "text-[10px] font-bold px-2 py-0.5 rounded-full border flex items-center gap-1",
                              source === 'SOIL_HEALTH_CARD' 
                                ? "bg-emerald-50 text-emerald-700 border-emerald-200" 
                                : "bg-sky-50 text-sky-700 border-sky-200"
                            )}>
                              {source === 'SOIL_HEALTH_CARD' ? <Check className="w-3 h-3" /> : <Edit3 className="w-3 h-3" />}
                              {source === 'SOIL_HEALTH_CARD' ? 'CARD' : 'FARMER'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Micronutrients Section */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-600 mb-2">
                  Secondary & Micronutrients (ppm)
                </h4>
                <div className="border border-gray-200 rounded-xl overflow-hidden">
                  <div className="divide-y divide-gray-100">
                    {microParams.map((meta) => {
                      const val = reviewValues[meta.key] ?? '';
                      const source = fieldSources[meta.key] || 'FARMER_ENTERED';
                      const err = validationErrors[meta.key];
                      const wasExtracted = extraction?.parameters?.[meta.key]?.value !== undefined && extraction?.parameters?.[meta.key]?.value !== null;

                      return (
                        <div key={meta.key} className="p-3 bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-gray-50/50">
                          <div className="min-w-[140px]">
                            <div className="text-xs font-semibold text-gray-900">{meta.label}</div>
                            <div className="text-[11px] text-gray-400">Unit: {meta.unit}</div>
                          </div>

                          <div className="flex-1 max-w-xs">
                            <input
                              type="text"
                              inputMode="decimal"
                              value={val}
                              onChange={(e) => handleValueChange(meta.key, e.target.value)}
                              placeholder={wasExtracted ? meta.placeholder : "Not detected — enter if available"}
                              className={cn(
                                "w-full text-xs rounded-lg px-3 py-1.5 border font-mono transition-colors",
                                err ? "border-red-400 bg-red-50/30 text-red-900" : "border-gray-200 focus:border-krishi-green",
                                val ? "text-gray-900 font-semibold" : "text-gray-400 italic font-normal"
                              )}
                            />
                            {err && <p className="text-[10px] text-red-600 mt-0.5">{err}</p>}
                          </div>

                          <div className="sm:w-32 flex justify-end">
                            <span className={cn(
                              "text-[10px] font-bold px-2 py-0.5 rounded-full border flex items-center gap-1",
                              source === 'SOIL_HEALTH_CARD' 
                                ? "bg-emerald-50 text-emerald-700 border-emerald-200" 
                                : "bg-sky-50 text-sky-700 border-sky-200"
                            )}>
                              {source === 'SOIL_HEALTH_CARD' ? <Check className="w-3 h-3" /> : <Edit3 className="w-3 h-3" />}
                              {source === 'SOIL_HEALTH_CARD' ? 'CARD' : 'FARMER'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* Confirmation Footer */}
            <div className="pt-4 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-3">
              <p className="text-[11px] text-gray-500 leading-tight max-w-xs sm:max-w-sm">
                Clicking confirm immediately activates your farm soil profile and updates the Digital Twin. Missing fields remain unrecorded.
              </p>
              
              <div className="flex items-center gap-2.5 w-full sm:w-auto shrink-0 justify-end">
                <button
                  onClick={() => setIsReviewOpen(false)}
                  disabled={confirming}
                  className="px-4 py-2.5 text-xs font-semibold text-gray-700 hover:text-gray-900 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors whitespace-nowrap"
                >
                  Cancel
                </button>
                
                <button
                  onClick={handleConfirmSoilProfile}
                  disabled={confirming || Object.keys(validationErrors).length > 0}
                  className="bg-krishi-green text-white font-bold py-2.5 px-5 rounded-xl hover:bg-krishi-green-dark disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-xs shadow-sm transition-all whitespace-nowrap shrink-0"
                >
                  {confirming ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Saving Profile...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      <span>CONFIRM SOIL DATA</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

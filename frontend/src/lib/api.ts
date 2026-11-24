import { 
  FullAnalysis, 
  FarmProfile, 
  WeatherIntelligence, 
  SoilIntelligence, 
  SoilExtractionResponse,
  SoilConfirmationRequest,
  SoilProfileResponse,
  MarketIntelligence, 

  PricePrediction, 
  PredictionItem,
  ExpertResponse, 
  DataSourcesResponse,
  DigitalTwin,
  FarmUpdateRequest
} from './types';

const API_URL = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');

async function fetchWithHandleError<T>(url: string, options?: RequestInit): Promise<T | null> {
  try {
    const cleanUrl = url.startsWith('/') ? url : `/${url}`;
    const endpoint = API_URL ? `${API_URL}${cleanUrl}` : cleanUrl;
    const res = await fetch(endpoint, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      }
    });
    if (!res.ok) {
      console.error(`API Error: ${res.status} on ${url}`);
      return null;
    }
    return res.json();
  } catch (err) {
    console.error(`Fetch Error on ${url}:`, err);
    return null;
  }
}

export function normalizePredictionItem(raw: any): PredictionItem | undefined {
  if (!raw || typeof raw !== 'object') return undefined;

  const min_price = Number(raw.min_price ?? raw.min ?? raw.expected_price_min ?? 0);
  const max_price = Number(raw.max_price ?? raw.max ?? raw.expected_price_max ?? min_price);
  const point_estimate = Number(raw.point_estimate ?? raw.point ?? raw.expected_price ?? Math.round((min_price + max_price) / 2));
  const confidence_pct = Number(raw.confidence_pct ?? raw.confidence ?? 50);

  let confidence_level: 'HIGH' | 'MEDIUM' | 'LOW' = 'MEDIUM';
  if (raw.confidence_level && ['HIGH', 'MEDIUM', 'LOW'].includes(String(raw.confidence_level).toUpperCase())) {
    confidence_level = String(raw.confidence_level).toUpperCase() as 'HIGH' | 'MEDIUM' | 'LOW';
  } else if (confidence_pct >= 80) {
    confidence_level = 'HIGH';
  } else if (confidence_pct < 50) {
    confidence_level = 'LOW';
  }

  return {
    min_price,
    max_price,
    point_estimate,
    confidence_pct,
    confidence_level,
    min: min_price,
    max: max_price,
    point: point_estimate,
  };
}

export function normalizePricePrediction(raw: any): PricePrediction {
  if (!raw || typeof raw !== 'object') {
    return {
      current_price: 0,
      horizon_days: 7,
      prediction: undefined,
      prediction_7d: undefined,
      prediction_15d: undefined,
      model_info: {
        type: 'XGBoost Regressor',
        training_data_points: 0,
        training_period: 'N/A',
        mae: 0,
        rmse: 0,
        mape_pct: 0,
      },
      data_used: [],
      data_type: 'UNAVAILABLE',
      timestamp: new Date().toISOString(),
      insufficient_data: true,
      reason: 'Prediction data unavailable',
    };
  }

  const pred7 = normalizePredictionItem(raw.prediction_7d);
  const pred15 = normalizePredictionItem(raw.prediction_15d);
  const genericPred = normalizePredictionItem(raw.prediction) || pred7 || pred15;

  const isInsufficient = Boolean(
    raw.insufficient_data ||
    (!genericPred && !pred7 && !pred15) ||
    (genericPred && (isNaN(genericPred.min_price) || isNaN(genericPred.max_price)))
  );

  return {
    current_price: Number(raw.current_price ?? 0),
    horizon_days: Number(raw.horizon_days ?? 7),
    prediction: genericPred,
    prediction_7d: pred7 || genericPred,
    prediction_15d: pred15,
    model_info: {
      type: raw.model_info?.type || 'XGBoost Regressor',
      training_data_points: Number(raw.model_info?.training_data_points ?? 0),
      training_period: String(raw.model_info?.training_period || 'N/A'),
      mae: Number(raw.model_info?.mae ?? 0),
      rmse: Number(raw.model_info?.rmse ?? 0),
      mape_pct: Number(raw.model_info?.mape_pct ?? 0),
      trained_at: raw.model_info?.trained_at,
    },
    data_used: Array.isArray(raw.data_used) ? raw.data_used : [],
    data_type: raw.data_type || (isInsufficient ? 'UNAVAILABLE' : 'MODEL_PREDICTION'),
    timestamp: raw.timestamp || new Date().toISOString(),
    insufficient_data: isInsufficient,
    reason: raw.reason,
  };
}

export function normalizeFullAnalysis(raw: any): FullAnalysis | null {
  if (!raw || typeof raw !== 'object') return null;

  return {
    ...raw,
    price_prediction: normalizePricePrediction(raw.price_prediction),
  };
}

export function normalizeExpertResponse(raw: any): ExpertResponse {
  if (!raw || typeof raw !== 'object') {
    return {
      answer: 'Unable to generate guidance from the available farm data.',
      confidence: 'Not available',
      data_used: [],
      what_to_do: [],
      possible_causes: [],
      recommended_actions: [],
      local_resources: ['Kisan Call Centre: 1800-180-1551'],
      expert_verification_required: true,
      engine: 'krishi_data_engine',
    };
  }

  const rawResp = raw.response && typeof raw.response === 'object' ? raw.response : {};

  const answer = String(
    raw.answer ||
    rawResp.answer ||
    raw.preliminary_guidance ||
    rawResp.preliminary_guidance ||
    raw.guidance ||
    rawResp.guidance ||
    ''
  ).trim();

  const rawConf = raw.confidence || rawResp.confidence;
  const confidence = (rawConf && typeof rawConf === 'string' && rawConf.trim())
    ? rawConf.trim().toUpperCase()
    : 'Not available';

  const why = String(raw.why || rawResp.why || '').trim();

  const what_to_do = Array.isArray(raw.what_to_do)
    ? raw.what_to_do
    : Array.isArray(raw.recommended_actions)
    ? raw.recommended_actions
    : Array.isArray(rawResp.recommended_actions)
    ? rawResp.recommended_actions
    : [];

  const possible_causes = Array.isArray(raw.possible_causes)
    ? raw.possible_causes
    : Array.isArray(rawResp.possible_causes)
    ? rawResp.possible_causes
    : [];

  const data_used = Array.isArray(raw.data_used)
    ? raw.data_used
    : Array.isArray(rawResp.data_used)
    ? rawResp.data_used
    : [];

  const local_resources = Array.isArray(raw.local_resources)
    ? raw.local_resources
    : Array.isArray(rawResp.local_resources)
    ? rawResp.local_resources
    : typeof raw.local_resources === 'string'
    ? [raw.local_resources]
    : ['Kisan Call Centre: 1800-180-1551'];

  return {
    answer: answer || 'Unable to generate guidance from the available farm data.',
    why: why || undefined,
    what_to_do: what_to_do.length > 0 ? what_to_do : undefined,
    when_to_escalate: raw.when_to_escalate || rawResp.when_to_escalate || rawResp.escalation_message,
    data_used: data_used.length > 0 ? data_used : undefined,
    possible_causes: possible_causes.length > 0 ? possible_causes : undefined,
    recommended_actions: what_to_do.length > 0 ? what_to_do : undefined,
    confidence: confidence,
    farm_context: raw.farm_context || raw.farm_context_used,
    local_resources: local_resources,
    expert_verification_required: Boolean(raw.expert_verification_required ?? rawResp.expert_verification_required ?? true),
    engine: raw.engine || 'krishi_data_engine',
    disclaimer: raw.disclaimer || raw.note,
  };
}

export const api = {
  onboardFarm: (data: any) => fetchWithHandleError<FarmProfile>('/api/farm/onboard', { method: 'POST', body: JSON.stringify(data) }),
  getFarm: (id: string) => fetchWithHandleError<FarmProfile>(`/api/farm/${id}`),
  getWeather: (lat: number, lon: number) => fetchWithHandleError<WeatherIntelligence>(`/api/weather/intelligence?lat=${lat}&lon=${lon}`),
  getSoil: (district: string, state: string, farmId?: string, crop?: string, cropStage?: string) => {
    const params = new URLSearchParams({ district, state });
    if (farmId) params.set('farm_id', farmId);
    if (crop) params.set('crop', crop);
    if (cropStage) params.set('crop_stage', cropStage);
    return fetchWithHandleError<SoilIntelligence>(`/api/soil/intelligence?${params.toString()}`);
  },
  getMarket: (commodity: string, district: string, state: string) => fetchWithHandleError<MarketIntelligence>(`/api/market/intelligence?commodity=${encodeURIComponent(commodity)}&district=${encodeURIComponent(district)}&state=${encodeURIComponent(state)}`),
  analyzeIntelligence: async (farmId: string): Promise<FullAnalysis | null> => {
    const raw = await fetchWithHandleError<any>('/api/intelligence/analyze', { 
      method: 'POST', 
      body: JSON.stringify({ farm_id: farmId }) 
    });
    return normalizeFullAnalysis(raw);
  },
  predictPrice: async (data: any): Promise<PricePrediction | null> => {
    const raw = await fetchWithHandleError<any>('/api/prediction/price', { 
      method: 'POST', 
      body: JSON.stringify(data) 
    });
    return raw ? normalizePricePrediction(raw) : null;
  },
  askExpert: async (farmId: string, question: string): Promise<ExpertResponse | null> => {
    const raw = await fetchWithHandleError<any>('/api/expert/ask', { 
      method: 'POST', 
      body: JSON.stringify({ farm_id: farmId, question }) 
    });
    return normalizeExpertResponse(raw);
  },
  getDataSources: () => fetchWithHandleError<DataSourcesResponse>('/api/data-sources'),
  getDigitalTwin: (farmId: string) => fetchWithHandleError<DigitalTwin>(`/api/farm/${farmId}/digital-twin`),
  updateFarm: (farmId: string, data: FarmUpdateRequest) => fetchWithHandleError<DigitalTwin>(`/api/farm/${farmId}`, { method: 'PUT', body: JSON.stringify(data) }),
  uploadSoilDocument: async (farmId: string, file: File): Promise<SoilExtractionResponse | null> => {
    const formData = new FormData();
    formData.append('farm_id', farmId);
    formData.append('file', file);
    try {
      const res = await fetch(`${API_URL}/api/soil/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Upload failed with status ${res.status}`);
      }
      return res.json();
    } catch (err: any) {
      console.error('Upload Error:', err);
      throw err;
    }
  },
  confirmSoilProfile: async (payload: SoilConfirmationRequest): Promise<SoilProfileResponse | null> => {
    return fetchWithHandleError<SoilProfileResponse>('/api/soil/confirm', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  getSoilProfile: (farmId: string) => fetchWithHandleError<SoilProfileResponse>(`/api/soil/profile/${farmId}`),
};


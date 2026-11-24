export interface FarmProfile {
  farm_id: string;
  farmer_name: string;
  crop: string;
  crop_variety: string;
  location: string;
  district: string;
  state: string;
  sowing_date: string;
  farm_area_acres: number;
  days_after_sowing: number;
  crop_stage: string;
  lat: number;
  lon: number;
  created_at: string;
}

export interface WeatherCurrent {
  temperature_c: number;
  feels_like_c: number;
  humidity_pct: number;
  precipitation_mm: number;
  wind_kmh: number;
  weather_code: number;
  description: string;
  timestamp: string;
}

export interface WeatherForecastDay {
  date: string;
  temp_max_c: number;
  temp_min_c: number;
  precipitation_mm: number;
  rain_probability_pct: number;
  humidity_pct: number;
  description: string;
  weather_code: number;
}

export interface RiskScore {
  score: number;
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  reason?: string;
}

export interface WeatherIntelligence {
  current: WeatherCurrent;
  forecast_7day: WeatherForecastDay[];
  historical_comparison: {
    current_month_rainfall_mm: number;
    historical_avg_rainfall_mm: number;
    deviation_pct: number;
    current_temp_c: number;
    historical_avg_temp_c: number;
    data_period: string;
  };
  agricultural_risk: {
    rainfall_risk: RiskScore;
    temperature_risk: RiskScore;
    humidity_risk: RiskScore;
    overall_weather_risk: number;
    overall_level: string;
  };
  data_source: {
    provider: string;
    model: string;
    last_updated: string;
    status: string;
    data_quality: string;
  };
}

export interface SoilParameter {
  value: number | null;
  unit: string;
  status: 'GOOD' | 'MEDIUM' | 'LOW' | 'HIGH' | 'POOR' | 'UNAVAILABLE' | 'NOT_DETECTED' | 'INVALID';
  optimal_min?: number;
  optimal_max?: number;
  source?: string;
  note?: string;
}

export interface SoilIntelligence {
  parameters: {
    ph: SoilParameter;
    nitrogen: SoilParameter;
    phosphorus: SoilParameter;
    potassium: SoilParameter;
    organic_carbon: SoilParameter;
    ec?: SoilParameter;
    soil_type: string;
    texture: string;
    sulphur?: SoilParameter;
    zinc?: SoilParameter;
    iron?: SoilParameter;
    copper?: SoilParameter;
    manganese?: SoilParameter;
    boron?: SoilParameter;
    [key: string]: any;
  };
  crop_suitability: {
    score: number;
    label: string;
    provenance_note?: string;
    factors: Array<{
      parameter: string;
      score: number;
      max_score: number;
      status: string;
      reason: string;
    }>;
  };
  overall_soil_risk: { score: number; level: string };
  recommendations: string[];
  data_source: {
    type: string;
    provider: string;
    coverage: string;
    last_updated: string;
    test_date?: string;
    status: string;
    data_quality: string;
    note: string;
  };
}

export interface ExtractedSoilField {
  value: number | string | null;
  raw_value?: any;
  unit: string;
  status: string;
  valid: boolean;
  source: string;
  extraction_state: string;
  note?: string;
  optimal_min?: number;
  optimal_max?: number;
}

export interface SoilExtractionResponse {
  document_id: string;
  farm_id: string;
  filename: string;
  file_type: string;
  ocr_status: 'SUCCESS' | 'PARTIAL_EXTRACTION' | 'OCR_FAILED' | 'UNSUPPORTED_FILE' | 'REVIEW_REQUIRED';
  test_date?: string;
  parameters: Record<string, ExtractedSoilField>;
  extraction_state: string;
  message: string;
}

export interface SoilConfirmationRequest {
  farm_id: string;
  document_id?: string;
  test_date?: string;
  parameters: Record<string, any>;
  field_sources?: Record<string, string>;
}

export interface SoilProfileResponse {
  id: string;
  farm_id: string;
  document_id?: string;
  provenance: string;
  is_active: boolean;
  test_date?: string;
  confirmation_status: string;
  confirmed_at: string;
  parameters: Record<string, any>;
  field_sources: Record<string, string>;
}


export interface MarketIntelligence {
  current: {
    market: string;
    commodity: string;
    date: string;
    min_price: number;
    max_price: number;
    modal_price: number;
    arrivals_tonnes: number;
    unit: string;
    data_type: string;
    data_source: string;
    note: string;
    msp_reference?: number;
    // Live data fields (present when DATA_GOV_IN_API_KEY is set and fetch succeeds)
    source?: string;
    status?: 'LIVE' | 'LATEST_AVAILABLE' | 'STALE' | 'HISTORICAL_SEED';
    retrieved_at?: string;
    days_old?: number;
  };
  historical: {
    years: number;
    data_points: number;
    price_series: Array<{ date: string; modal_price: number; min_price: number; max_price: number }>;
    statistics: {
      mean_price: number;
      std_price: number;
      min_price_all_time: number;
      max_price_all_time: number;
      current_vs_avg_pct: number;
      percentile_rank: number;
    };
    seasonal_trend: {
      direction: 'INCREASING' | 'DECREASING' | 'STABLE';
      magnitude: string;
      current_month_avg_historical: number;
      description: string;
    };
    yoy_comparison: Array<{ year: number; month_avg: number; label: string }>;
  };
  mandi_comparison: Array<{
    market: string;
    modal_price: number;
    distance_km: number;
    transport_cost_per_q: number;
    net_price: number;
  }>;
  data_source: {
    type: string;
    provider: string;
    note: string;
    data_quality: string;
    date_range: string;
    total_observations: number;
    // Live data extra fields
    status?: string;
    market_date?: string;
    retrieved_at?: string;
    days_old?: number;
  };
}


export interface PredictionItem {
  min_price: number;
  max_price: number;
  point_estimate: number;
  confidence_pct: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  min?: number;
  max?: number;
  point?: number;
}

export interface PricePrediction {
  current_price: number;
  horizon_days?: number;
  prediction?: PredictionItem;
  prediction_7d?: PredictionItem;
  prediction_15d?: PredictionItem;
  model_info: {
    type: string;
    training_data_points: number;
    training_period: string;
    mae: number;
    rmse: number;
    mape_pct: number;
    trained_at?: string;
  };
  data_used: string[];
  data_type: string;
  timestamp: string;
  insufficient_data: boolean;
  reason?: string;
}

export interface DecisionScenario {
  label: string;
  expected_price: number;
  expected_price_min?: number;
  expected_price_max?: number;
  expected_revenue: number;
  storage_cost: number;
  weather_risk_penalty: number;
  transport_cost: number;
  net_realization: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence_pct: number;
}

export interface FullAnalysis {
  farm_summary: FarmProfile;
  intelligence_snapshot: {
    soil_condition: { score: number; label: string; level: string };
    weather_risk: { score: number; label: string; level: string };
    crop_risk: { score: number; label: string; level: string };
    market_trend: { direction: string; label: string; current_price: number; market_supported?: boolean };
  };
  risk_breakdown: {
    weather_risk: { score: number; level: string; factors: any[] };
    soil_risk: { score: number; level: string; factors: any[] };
    crop_risk: { score: number; level: string; factors: any[] };
    market_risk: { score: number; level: string; factors: any[] };
    overall_risk: { score: number; level: string };
  };
  price_prediction: PricePrediction;
  decision: {
    farm_area_acres: number;
    estimated_yield_qtl: number;
    market_prediction_available?: boolean;
    scenarios: {
      sell_now: DecisionScenario;
      wait_7d: DecisionScenario;
      wait_15d: DecisionScenario;
    };
    recommendation: {
      action: 'SELL_NOW' | 'WAIT_7D' | 'WAIT_15D' | 'MONITOR' | 'MARKET_UNAVAILABLE';
      confidence: string;
      headline: string;
      summary: string;
      risk_adjusted_best: string;
    };
  };
  explainability: {
    data_signals: Array<{ signal: string; value: string; direction: string; weight: string }>;
    data_used: string[];
    reasoning_steps: string[];
    conclusion: string;
    prediction_confidence: string;
    data_quality_overall: string;
    important_note: string;
    market_prediction_available?: boolean;
  };
  what_changed: {
    available: boolean;
    message?: string;
    changes?: Array<{ metric: string; from: string; to: string; direction: string }>;
  };
  generated_at: string;
  data_freshness: {
    weather: string;
    market: string;
    soil: string;
    ml_model: string;
    market_supported?: boolean;
  };
}

export interface ExpertResponse {
  answer: string;
  why?: string;
  what_to_do?: string[];
  when_to_escalate?: string;
  data_used?: string[];
  possible_causes?: string[];
  recommended_actions?: string[];
  confidence: string;
  farm_context?: {
    crop?: string;
    stage?: string;
    location?: string;
    soil_source?: string;
  };
  local_resources?: string[];
  expert_verification_required?: boolean;
  engine?: string;
  disclaimer?: string;
}

export interface DataSourcesResponse {
  sources: Array<{
    name: string;
    provider: string;
    status: 'CONNECTED' | 'SEED_DATA' | 'DISCONNECTED' | 'REGIONAL_ESTIMATE';
    variables: string[];
    coverage: string;
    last_updated: string;
    data_quality: 'HIGH' | 'MEDIUM' | 'LOW';
    notes?: string;
  }>;
  overall_quality: string;
  active_count: number;
  total_count: number;
}

export interface FarmEvent {
  id: string;
  farm_id: string;
  event_type: string;
  timestamp: string;
  title: string;
  description?: string;
  source: string;
}

export interface FarmUpdateRequest {
  farmer_name?: string;
  location?: string;
  district?: string;
  state?: string;
  crop?: string;
  crop_variety?: string;
  sowing_date?: string;
  farm_area_acres?: number;
  soil_data_available?: boolean;
  phone?: string;
}

export interface DigitalTwinFarmer {
  name: string;
  phone?: string;
}

export interface DigitalTwinFarm {
  state: string;
  district: string;
  location: string;
  acreage: number;
  soil_data_available: boolean;
  lat?: number;
  lon?: number;
}

export interface DigitalTwinCrop {
  name: string;
  variety?: string;
  sowing_date: string;
  stage: string;
  days_after_sowing: number;
}

export interface DigitalTwinMetadata {
  created_at: string;
  updated_at: string;
}

export interface DigitalTwinProvenance {
  farmer_profile: string;
  weather: string;
  soil: string;
  market: string;
  prediction: string;
  decision: string;
}

export interface DigitalTwin {
  farm_id: string;
  farmer: DigitalTwinFarmer;
  farm: DigitalTwinFarm;
  crop: DigitalTwinCrop;
  metadata: DigitalTwinMetadata;
  intelligence: {
    weather?: WeatherIntelligence;
    soil?: SoilIntelligence;
    market?: MarketIntelligence;
    risk?: {
      weather_risk: { score: number; level: string; factors?: any[] };
      soil_risk: { score: number; level: string; factors?: any[] };
      crop_risk: { score: number; level: string; factors?: any[] };
      market_risk: { score: number; level: string; factors?: any[] };
      overall_risk: { score: number; level: string };
    };
    prediction?: PricePrediction;
    decision?: {
      farm_area_acres: number;
      estimated_yield_qtl: number;
      market_prediction_available?: boolean;
      scenarios?: {
        sell_now?: DecisionScenario;
        wait_7d?: DecisionScenario;
        wait_15d?: DecisionScenario;
      };
      recommendation?: {
        action: string;
        confidence: string;
        headline: string;
        summary: string;
        risk_adjusted_best?: string;
      };
    };
  };
  data_provenance: DigitalTwinProvenance;
  events: FarmEvent[];
  decision_history: Array<{
    observed_at?: string;
    overall_risk_score?: number;
    current_price?: number;
    recommendation_action?: string;
    recommendation_confidence?: string;
  }>;
}


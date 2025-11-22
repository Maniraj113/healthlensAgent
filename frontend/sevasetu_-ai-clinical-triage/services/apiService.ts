import { PatientInput } from "../types";

// Backend API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface BackendTriageResponse {
  visit_id: string;
  risk_scores: {
    anemia: { score: number; level: string };
    maternal: { score: number; level: string };
    sugar: { score: number; level: string };
    infection?: { score: number; level: string };
    nutrition?: { score: number; level: string };
  };
  triage_level: string;
  summary_text: string;
  action_checklist: string[];
  emergency_signs: string[];
  voice_text: string;
  reasons: Array<{
    fact: string;
    weight: number;
    confidence: number;
  }>;
  image_evidence?: {
    pallor: boolean;
    pallor_confidence: number;
    edema_detected: boolean;
    edema_confidence: number;
    malnutrition_flag: boolean;
    malnutrition_confidence: number;
    skin_infection: boolean;
    skin_infection_confidence: number;
    dehydration: boolean;
    dehydration_confidence: number;
  };
  timestamp: string;
  offline_processed: boolean;
}

/**
 * Transform frontend PatientInput to backend InputPayload format
 */
const transformToBackendPayload = (data: PatientInput) => {
  // Map sex values
  const sexMap: Record<string, string> = {
    'M': 'male',
    'F': 'female',
    'Other': 'other'
  };

  // Map language values
  const languageMap: Record<string, string> = {
    'English': 'english',
    'Hindi': 'hindi',
    'Tamil': 'tamil',
    'Telugu': 'telugu',
    'Bengali': 'bengali'
  };

  return {
    vitals: {
      bp_systolic: data.bp_systolic || null,
      bp_diastolic: data.bp_diastolic || null,
      random_glucose: data.random_glucose || null,
      temperature_c: data.temperature_c || null,
      heart_rate: data.heart_rate || null,
      spo2: data.spo2 || null
    },
    symptoms: data.symptoms,
    camera_inputs: {
      conjunctiva_photo: data.images.conjunctiva || null,
      swelling_photo: data.images.swelling || null,
      child_arm_photo: null,
      skin_photo: data.images.skin || null,
      breathing_video: null
    },
    age: data.age,
    sex: sexMap[data.sex] || 'other',
    pregnant: data.pregnant,
    gestational_weeks: data.pregnant ? (data.gestational_weeks || null) : null,
    worker_id: data.worker_id,
    patient_id: data.patient_id,
    language: languageMap[data.language] || 'english',
    offline_mode: false
  };
};

/**
 * Call the backend /api/v1/analyze endpoint
 */
export const analyzePatientCase = async (data: PatientInput): Promise<BackendTriageResponse> => {
  try {
    const payload = transformToBackendPayload(data);
    
    console.log('Sending request to backend:', `${API_BASE_URL}/api/v1/analyze`);
    console.log('Payload:', JSON.stringify(payload, null, 2));

    const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Backend response:', result);
    
    return result;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

/**
 * Health check endpoint
 */
export const checkHealth = async (): Promise<{ status: string; service: string; version: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * Get visit by ID
 */
export const getVisit = async (visitId: string): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/visit/${visitId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch visit: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Get visit failed:', error);
    throw error;
  }
};

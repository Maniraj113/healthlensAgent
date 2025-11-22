
export interface PatientVitals {
  bp_systolic: number;
  bp_diastolic: number;
  random_glucose: number;
  temperature_c: number;
  heart_rate: number;
  spo2: number;
}

export interface PatientDemographics {
  age: number;
  sex: 'M' | 'F' | 'Other';
  pregnant: boolean;
  gestational_weeks?: number;
  worker_id: string;
  patient_id: string;
  language: string;
  name?: string;
}

export interface PatientInput extends PatientVitals, PatientDemographics {
  symptoms: string[];
  images: {
    conjunctiva?: string; // base64
    swelling?: string; // base64
    skin?: string; // base64
  };
}

export interface User {
  name: string;
  role: 'ASHA' | 'PATIENT';
  id: string;
  phone: string;
  language?: string;
}

export interface ProgressStage {
  stage: string;
  status: string;
}

export interface RecommendedAction {
  action: string;
  priority: 'High' | 'Medium' | 'Low';
}

export interface RiskScore {
  score: number;
  level: string;
}

export interface RiskScores {
  anemia: RiskScore;
  maternal: RiskScore;
  sugar: RiskScore;
  infection?: RiskScore;
  nutrition?: RiskScore;
}

export interface ReasoningFact {
  fact: string;
  weight: number;
  confidence: number;
}

export interface ImageEvidence {
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
}

export interface TriageResponse {
  visit_id: string;
  risk_scores: RiskScores;
  triage_level: string;
  summary_text: string;
  action_checklist: string[];
  emergency_signs: string[];
  voice_text: string;
  reasons: ReasoningFact[];
  image_evidence?: ImageEvidence;
  timestamp: string;
  offline_processed: boolean;
}

// New Types for Workflow
export interface ScreeningRequest {
  id: string;
  patient_id: string;
  patient_name: string;
  asha_id: string;
  status: 'Pending' | 'Completed';
  date: string;
}

export interface PatientProfile {
  id: string;
  name: string;
  age: number;
  sex: 'M' | 'F' | 'Other';
  phone: string;
  assigned_asha_id: string;
}

// Pre-defined symptoms list for the UI
export const SYMPTOM_OPTIONS = [
  "fatigue",
  "dizziness",
  "breathlessness",
  "cough",
  "fever",
  "abdominal_pain",
  "headache",
  "blurred_vision",
  "swelling",
  "decreased_fetal_movement",
  "chest_pain",
  "nausea",
  "vomiting",
  "frequent_urination",
  "excessive_thirst"
];

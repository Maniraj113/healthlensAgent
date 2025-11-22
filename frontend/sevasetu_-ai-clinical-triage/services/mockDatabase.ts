
import { User, PatientProfile, ScreeningRequest } from '../types';

// ASHA Workers Data
export const ASHA_USERS = [
  { worker_id: "ASHA_101", username: "Lakshmi", phone: "9876543210", role: 'ASHA' },
  { worker_id: "ASHA_102", username: "Akshay", phone: "9000011223", role: 'ASHA' },
  { worker_id: "ASHA_103", username: "Renu", phone: "9123456780", role: 'ASHA' }
];

// Patients Data (Mapped to specific ASHAs)
export const PATIENT_USERS = [
  { id: "P001", name: "Ramesh", phone: "9000001111", age: 45, sex: 'M', assigned_asha_id: "ASHA_101", role: 'PATIENT' },
  { id: "P002", name: "Sita", phone: "9988776655", age: 28, sex: 'F', assigned_asha_id: "ASHA_101", role: 'PATIENT' },
  { id: "P003", name: "Abdul", phone: "8877665544", age: 60, sex: 'M', assigned_asha_id: "ASHA_102", role: 'PATIENT' },
  { id: "P004", name: "Gita", phone: "7766554433", age: 32, sex: 'F', assigned_asha_id: "ASHA_103", role: 'PATIENT' }
];

// Initial Screening Requests
// Using 'let' so we can update it in memory during the session
let REQUESTS: ScreeningRequest[] = [
  { id: "R101", patient_id: "P001", patient_name: "Ramesh", asha_id: "ASHA_101", status: "Pending", date: "2023-10-26" },
  { id: "R102", patient_id: "P002", patient_name: "Sita", asha_id: "ASHA_101", status: "Completed", date: "2023-10-25" },
  { id: "R103", patient_id: "P003", patient_name: "Abdul", asha_id: "ASHA_102", status: "Pending", date: "2023-10-26" }
];

// Login Logic
export const loginUser = (phone: string, otp: string, role: 'ASHA' | 'PATIENT'): User | null => {
  // In a real app, OTP would be validated strictly. 
  // For this demo, we allow any OTP or specific demo ones.
  
  if (role === 'ASHA') {
    const user = ASHA_USERS.find(u => u.phone === phone);
    if (user) return { name: user.username, role: 'ASHA', id: user.worker_id, phone: user.phone };
  } else {
    const user = PATIENT_USERS.find(u => u.phone === phone);
    if (user) return { name: user.name, role: 'PATIENT', id: user.id, phone: user.phone };
  }
  return null;
};

// Get requests filtered by ASHA ID
export const getRequestsForAsha = (ashaId: string) => {
  return REQUESTS.filter(r => r.asha_id === ashaId).sort((a, b) => b.status === 'Pending' ? 1 : -1);
};

// Get requests filtered by Patient ID
export const getRequestsForPatient = (patientId: string) => {
  return REQUESTS.filter(r => r.patient_id === patientId);
};

// Create a new request
export const createScreeningRequest = (patientId: string): boolean => {
  const patient = PATIENT_USERS.find(p => p.id === patientId);
  if (!patient) return false;
  
  const newReq: ScreeningRequest = {
    id: `R${Date.now().toString().slice(-4)}`,
    patient_id: patient.id,
    patient_name: patient.name,
    asha_id: patient.assigned_asha_id,
    status: 'Pending',
    date: new Date().toISOString().split('T')[0]
  };
  
  REQUESTS = [newReq, ...REQUESTS];
  return true;
};

// Mark request as completed
export const completeRequest = (requestId: string) => {
  REQUESTS = REQUESTS.map(r => r.id === requestId ? { ...r, status: 'Completed' } : r);
};

// Get ASHA details for a patient
export const getAshaForPatient = (patientId: string) => {
  const patient = PATIENT_USERS.find(p => p.id === patientId);
  if (!patient) return null;
  return ASHA_USERS.find(a => a.worker_id === patient.assigned_asha_id);
};

// Get Patient Details
export const getPatientDetails = (patientId: string) => {
    return PATIENT_USERS.find(p => p.id === patientId);
};

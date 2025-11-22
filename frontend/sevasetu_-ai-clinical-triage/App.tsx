
import React, { useState } from 'react';
import { 
  Activity, 
  Camera, 
  ChevronDown, 
  HeartPulse, 
  Stethoscope, 
  User as UserIcon, 
  AlertCircle,
  LogOut,
  Check,
  Globe,
  ArrowLeft
} from 'lucide-react';
import { analyzePatientCase } from './services/apiService';
import { PatientInput, SYMPTOM_OPTIONS, TriageResponse, User, ScreeningRequest } from './types';
import { getPatientDetails, completeRequest } from './services/mockDatabase';
import ResultView from './components/ResultView';
import LoadingOverlay from './components/LoadingOverlay';
import LoginView from './components/LoginView';
import PatientDashboard from './components/PatientDashboard';
import AshaDashboard from './components/AshaDashboard';

// Basic UI Translations for key headers
const UI_TEXT: Record<string, any> = {
  "English": {
    title: "Patient Assessment",
    subtitle: "Enter vitals and symptoms for AI clinical triage.",
    patientDetails: "Patient Details",
    vitals: "Critical Vitals",
    symptoms: "Symptoms Reported",
    camera: "Visual Evidence",
    submit: "Analyze & Triage Patient",
    analyzing: "Analyzing..."
  },
  "Tamil": {
    title: "நோயாளியின் மதிப்பீடு",
    subtitle: "AI மருத்துவ பரிசோதனைக்காக முக்கிய அளவுகள் மற்றும் அறிகுறிகளை உள்ளிடவும்.",
    patientDetails: "நோயாளி விவரங்கள்",
    vitals: "முக்கிய அறிகுறிகள்",
    symptoms: "அறிகுறிகள்",
    camera: "காட்சி ஆதாரம்",
    submit: "நோயாளியை சோதித்து வகைப்படுத்தவும்",
    analyzing: "பகுப்பாய்வு செய்கிறது..."
  },
  "Hindi": {
    title: "रोगी का आकलन",
    subtitle: "AI नैदानिक ​​​​ट्राइएज के लिए महत्वपूर्ण संकेत और लक्षण दर्ज करें।",
    patientDetails: "रोगी का विवरण",
    vitals: "महत्वपूर्ण संकेत",
    symptoms: "लक्षण",
    camera: "दृश्य प्रमाण",
    submit: "विश्लेषण और ट्राइएज",
    analyzing: "विश्लेषण कर रहा है..."
  }
};

const INITIAL_FORM_DATA: PatientInput = {
  age: 0,
  sex: "M",
  pregnant: false,
  bp_systolic: undefined,
  bp_diastolic: undefined,
  random_glucose: undefined,
  temperature_c: undefined,
  heart_rate: undefined,
  spo2: undefined,
  symptoms: [],
  worker_id: "",
  patient_id: "",
  language: "English",
  images: {}
};

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [view, setView] = useState<'dashboard' | 'form' | 'result'>('dashboard');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<PatientInput>(INITIAL_FORM_DATA);
  const [result, setResult] = useState<TriageResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showSubmissionToast, setShowSubmissionToast] = useState(false);
  
  // Track which request we are fulfilling
  const [activeRequestId, setActiveRequestId] = useState<string | null>(null);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    setView('dashboard');
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setResult(null);
    setView('dashboard');
    setFormData(INITIAL_FORM_DATA);
    setActiveRequestId(null);
  };

  const handleStartAssessment = (request?: ScreeningRequest) => {
    let initialData = { ...INITIAL_FORM_DATA, worker_id: currentUser?.id || '' };
    
    if (request) {
      setActiveRequestId(request.id);
      const patient = getPatientDetails(request.patient_id);
      if (patient) {
        initialData = {
          ...initialData,
          patient_id: patient.id,
          age: patient.age,
          sex: patient.sex as 'M' | 'F' | 'Other',
          language: (currentUser?.language || 'English').toLowerCase()
        };
      }
    } else {
      setActiveRequestId(null);
    }
    
    setFormData(initialData);
    setView('form');
  };

  const handleInputChange = (field: keyof PatientInput, value: any) => {
    // For number fields, treat empty strings as undefined, otherwise convert to number
    if (typeof value === 'string' && value.trim() === '' && 
        ['bp_systolic', 'bp_diastolic', 'random_glucose', 'temperature_c', 'heart_rate', 'spo2'].includes(field)) {
      value = undefined;
    } else if (['bp_systolic', 'bp_diastolic', 'random_glucose', 'temperature_c', 'heart_rate', 'spo2'].includes(field)) {
      const numValue = Number(value);
      value = isNaN(numValue) ? undefined : numValue;
    }
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const toggleSymptom = (symptom: string) => {
    setFormData(prev => {
      const symptoms = prev.symptoms.includes(symptom)
        ? prev.symptoms.filter(s => s !== symptom)
        : [...prev.symptoms, symptom];
      return { ...prev, symptoms };
    });
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>, type: 'conjunctiva' | 'swelling' | 'skin') => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result as string;
        const base64Data = base64String.split(',')[1];
        setFormData(prev => ({
          ...prev,
          images: { ...prev.images, [type]: base64Data }
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    setShowSubmissionToast(true);
    setTimeout(() => setShowSubmissionToast(false), 4000);
    
    try {
      const aiResponse = await analyzePatientCase(formData);
      setResult(aiResponse);
      
      // Mark request as completed if applicable
      if (activeRequestId) {
        completeRequest(activeRequestId);
      }

      setView('result');
    } catch (err: any) {
      const errorMessage = err?.message || "Unable to analyze data. Please try again or check internet connection.";
      setError(`Analysis failed: ${errorMessage}`);
      console.error('Analysis error:', err);
      setShowSubmissionToast(false);
    } finally {
      setLoading(false);
    }
  };

  // Get UI text based on current language
  const currentLang = currentUser?.language || 'English';
  const t = UI_TEXT[currentLang] || UI_TEXT['English'];

  // View Routing
  if (!currentUser) {
    return <LoginView onLogin={handleLogin} />;
  }

  if (currentUser.role === 'PATIENT') {
    return <PatientDashboard user={currentUser} onLogout={handleLogout} />;
  }

  // ASHA Dashboard View
  if (view === 'dashboard') {
    return <AshaDashboard user={currentUser} onLogout={handleLogout} onStartAssessment={handleStartAssessment} />;
  }

  // ASHA Form & Result Views
  return (
    <div className="min-h-screen bg-slate-50 text-gray-900 font-sans selection:bg-blue-100 safe-area-inset">
      <LoadingOverlay isActive={loading} />

      {/* Notification Toast */}
      {showSubmissionToast && (
          <div className="fixed top-20 right-4 z-50 bg-slate-900 text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-4 animate-in slide-in-from-right duration-300">
            <div className="bg-green-500 rounded-full p-1">
                <Check className="w-4 h-4 text-white" />
            </div>
            <div>
                <h4 className="font-bold">Report Generated</h4>
                <p className="text-sm text-gray-300">Notification sent to patient via WhatsApp.</p>
            </div>
          </div>
      )}

      {/* Header */}
      <header className="bg-blue-700 text-white shadow-md sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {view === 'form' && (
                <button onClick={() => setView('dashboard')} className="mr-2 p-1 hover:bg-blue-600 rounded-full transition-colors">
                    <ArrowLeft className="w-6 h-6" />
                </button>
            )}
            <div className="bg-white p-1.5 rounded-lg">
              <Activity className="w-6 h-6 text-blue-700" />
            </div>
            <span className="font-bold text-xl tracking-tight hidden sm:inline">SevaSetu</span>
          </div>
          <div className="flex items-center gap-4">
             <div className="flex items-center gap-1 text-xs bg-blue-800 px-2 py-1 rounded">
                <Globe className="w-3 h-3" />
                {currentLang}
             </div>
             <div className="hidden sm:block text-right">
                <div className="text-sm font-bold opacity-90">{currentUser.name}</div>
             </div>
             <button 
               onClick={handleLogout}
               className="bg-blue-800 p-2 rounded-lg hover:bg-blue-900 transition-colors"
               title="Logout"
             >
                <LogOut className="w-5 h-5" />
             </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-4 sm:py-6">
        
        {view === 'form' && (
          <div className="animate-in slide-in-from-bottom-4 duration-500">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-slate-900">{t.title}</h1>
              <p className="text-slate-600">{t.subtitle}</p>
              {activeRequestId && (
                  <div className="mt-2 inline-flex items-center gap-2 bg-orange-100 text-orange-800 px-3 py-1 rounded-lg text-sm font-bold border border-orange-200">
                      <Check className="w-4 h-4" /> Fulfilling Request #{activeRequestId}
                  </div>
              )}
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-8">
              
              {/* Section: Demographics */}
              <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                <h2 className="text-lg font-bold text-blue-800 mb-4 flex items-center gap-2 border-b pb-2">
                  <UserIcon className="w-5 h-5" /> {t.patientDetails}
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Patient ID</label>
                    <input 
                      type="text" 
                      value={formData.patient_id} 
                      onChange={e => handleInputChange('patient_id', e.target.value)}
                      className="w-full p-3 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="P_XXXX"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Age</label>
                    <input 
                      type="number" 
                      value={formData.age} 
                      onChange={e => handleInputChange('age', Number(e.target.value) || 0)}
                      className="w-full p-3 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Sex</label>
                    <div className="relative">
                      <select 
                        value={formData.sex} 
                        onChange={e => handleInputChange('sex', e.target.value)}
                        className="w-full p-3 bg-white text-gray-900 border border-gray-300 rounded-lg appearance-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                        <option value="Other">Other</option>
                      </select>
                      <ChevronDown className="absolute right-3 top-3.5 w-5 h-5 text-gray-400 pointer-events-none" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Language</label>
                    <div className="relative">
                      <select 
                        value={formData.language} 
                        onChange={e => handleInputChange('language', e.target.value)}
                        className="w-full p-3 bg-white text-gray-900 border border-gray-300 rounded-lg appearance-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="english">English</option>
                        <option value="hindi">हिंदी (Hindi)</option>
                        <option value="tamil">தமிழ் (Tamil)</option>
                      </select>
                      <ChevronDown className="absolute right-3 top-3.5 w-5 h-5 text-gray-400 pointer-events-none" />
                    </div>
                  </div>

                </div>
              </section>
              <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                <h2 className="text-lg font-bold text-blue-800 mb-4 flex items-center gap-2 border-b pb-2">
                  <HeartPulse className="w-5 h-5" /> {t.vitals}
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">Systolic BP (Upper)</label>
                    <div className="relative">
                        <input 
                          type="number" 
                          value={formData.bp_systolic || ''}
                          onChange={e => handleInputChange('bp_systolic', e.target.value)}
                          className="w-full p-4 text-lg font-mono bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" 
                          placeholder="120"
                        />
                        <span className="absolute right-3 top-4 text-xs text-gray-400 font-bold">mmHg</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">Diastolic BP (Lower)</label>
                    <div className="relative">
                        <input 
                          type="number" 
                          value={formData.bp_diastolic || ''}
                          onChange={e => handleInputChange('bp_diastolic', e.target.value)}
                          className="w-full p-4 text-lg font-mono bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="80"
                        />
                        <span className="absolute right-3 top-4 text-xs text-gray-400 font-bold">mmHg</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">Random Glucose</label>
                    <div className="relative">
                        <input 
                          type="number" 
                          value={formData.random_glucose || ''}
                          onChange={e => handleInputChange('random_glucose', e.target.value)}
                          className={`w-full p-4 text-lg font-mono bg-white text-gray-900 border rounded-lg focus:ring-2 focus:ring-blue-500 ${formData.random_glucose && formData.random_glucose > 200 ? 'border-red-300 text-red-700 bg-red-50' : 'border-gray-300'}`}
                          placeholder="100"
                        />
                        <span className="absolute right-3 top-4 text-xs text-gray-400 font-bold">mg/dL</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">Temperature</label>
                    <div className="relative">
                        <input 
                          type="number" 
                          step="0.1"
                          value={formData.temperature_c || ''}
                          onChange={e => handleInputChange('temperature_c', e.target.value)}
                          className="w-full p-4 text-lg font-mono bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="37.0"
                        />
                        <span className="absolute right-3 top-4 text-xs text-gray-400 font-bold">°C</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">Heart Rate</label>
                    <div className="relative">
                        <input 
                          type="number" 
                          value={formData.heart_rate || ''}
                          onChange={e => handleInputChange('heart_rate', e.target.value)}
                          className="w-full p-4 text-lg font-mono bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="72"
                        />
                        <span className="absolute right-3 top-4 text-xs text-gray-400 font-bold">bpm</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">SpO2</label>
                    <div className="relative">
                        <input 
                          type="number" 
                          value={formData.spo2 || ''}
                          onChange={e => handleInputChange('spo2', e.target.value)}
                          className="w-full p-4 text-lg font-mono bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="98"
                        />
                        <span className="absolute right-3 top-4 text-xs text-gray-400 font-bold">%</span>
                    </div>
                  </div>
                </div>
              </section>
              <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                <h2 className="text-lg font-bold text-blue-800 mb-4 flex items-center gap-2 border-b pb-2">
                  <Stethoscope className="w-5 h-5" /> {t.symptoms}
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                  {SYMPTOM_OPTIONS.map(symptom => (
                    <button
                      type="button"
                      key={symptom}
                      onClick={() => toggleSymptom(symptom)}
                      className={`p-3 rounded-lg text-sm font-semibold text-left transition-all capitalize ${
                        formData.symptoms.includes(symptom)
                          ? 'bg-blue-600 text-white shadow-md ring-2 ring-blue-300'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {symptom.replace(/_/g, ' ')}
                    </button>
                  ))}
                </div>
              </section>

              {/* Section: Camera */}
              <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                <h2 className="text-lg font-bold text-blue-800 mb-4 flex items-center gap-2 border-b pb-2">
                  <Camera className="w-5 h-5" /> {t.camera}
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                   {/* Conjunctiva */}
                   <div className="border-2 border-dashed border-gray-300 rounded-xl p-4 hover:bg-gray-50 transition-colors text-center">
                      <label className="cursor-pointer block">
                        <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-2">
                           <Camera className="w-6 h-6" />
                        </div>
                        <span className="block font-medium text-gray-700">Conjunctiva (Eye)</span>
                        <span className="block text-xs text-gray-500 mt-1">For Anemia check</span>
                        <input type="file" accept="image/*" className="hidden" onChange={(e) => handleImageUpload(e, 'conjunctiva')} />
                        {formData.images.conjunctiva && (
                          <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded">Photo Added</span>
                        )}
                      </label>
                   </div>

                   {/* Swelling */}
                   <div className="border-2 border-dashed border-gray-300 rounded-xl p-4 hover:bg-gray-50 transition-colors text-center">
                      <label className="cursor-pointer block">
                        <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-2">
                           <Camera className="w-6 h-6" />
                        </div>
                        <span className="block font-medium text-gray-700">Leg Swelling</span>
                        <span className="block text-xs text-gray-500 mt-1">For Edema check</span>
                        <input type="file" accept="image/*" className="hidden" onChange={(e) => handleImageUpload(e, 'swelling')} />
                        {formData.images.swelling && (
                          <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded">Photo Added</span>
                        )}
                      </label>
                   </div>
                </div>
              </section>

              {/* Action Button */}
              <div className="sticky bottom-4 pt-4">
                <button
                  type="submit"
                  className="w-full bg-blue-700 hover:bg-blue-800 text-white text-xl font-bold py-4 rounded-xl shadow-lg transform transition active:scale-95 flex items-center justify-center gap-3"
                >
                  <Activity className="w-6 h-6" />
                  {t.submit}
                </button>
              </div>

            </form>
          </div>
        )}

        {view === 'result' && result && (
          <ResultView result={result} onReset={() => setView('dashboard')} />
        )}
      </main>
    </div>
  );
}

export default App;

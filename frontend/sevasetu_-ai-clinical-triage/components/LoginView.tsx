
import React, { useState } from 'react';
import { User as UserIcon, Shield, Smartphone, ArrowRight, CheckCircle, Globe } from 'lucide-react';
import { User } from '../types';
import { loginUser } from '../services/mockDatabase';

interface LoginViewProps {
  onLogin: (user: User) => void;
}

const LoginView: React.FC<LoginViewProps> = ({ onLogin }) => {
  const [role, setRole] = useState<'ASHA' | 'PATIENT'>('ASHA');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'PHONE' | 'OTP'>('PHONE');
  const [error, setError] = useState('');
  const [language, setLanguage] = useState('English');

  const handlePhoneSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // We simulate checking if user exists by "logging in" just with phone first for UI flow
    // In this mock, we just move to OTP if phone has length
    if (phone.length >= 10) {
      setStep('OTP');
    } else {
      setError('Please enter a valid phone number.');
    }
  };

  const handleOtpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validate against Mock DB
    const user = loginUser(phone, otp, role);

    if (user) {
      // Inject selected language into user profile for session
      onLogin({ ...user, language }); 
    } else {
      setError('Invalid Credentials. For demo, check the list of available users.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
      
      {/* Header / Branding */}
      <div className="mb-8 text-center">
        <div className="bg-blue-700 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
          <Shield className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-extrabold text-blue-900 tracking-tight">SevaSetu</h1>
        <p className="text-slate-600 font-medium">Rural Health AI Assistant</p>
      </div>

      <div className="bg-white w-full max-w-md rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
        
        {/* Language Bar */}
        <div className="bg-slate-100 px-6 py-3 flex justify-end border-b border-slate-200">
           <div className="flex items-center gap-2 text-sm font-bold text-slate-700 cursor-pointer">
              <Globe className="w-4 h-4" />
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-transparent border-none focus:ring-0 cursor-pointer"
              >
                <option value="English">English</option>
                <option value="Hindi">हिंदी (Hindi)</option>
                <option value="Telugu">తెలుగు (Telugu)</option>
                <option value="Tamil">தமிழ் (Tamil)</option>
              </select>
           </div>
        </div>

        <div className="p-8">
          {/* Role Selection */}
          {step === 'PHONE' && (
            <div className="flex gap-4 mb-8">
              <button
                onClick={() => setRole('ASHA')}
                className={`flex-1 py-4 rounded-xl border-2 font-bold text-center transition-all ${
                  role === 'ASHA' 
                    ? 'border-blue-600 bg-blue-50 text-blue-800 ring-2 ring-blue-200' 
                    : 'border-gray-200 text-gray-500 hover:bg-gray-50'
                }`}
              >
                <Shield className={`w-6 h-6 mx-auto mb-2 ${role === 'ASHA' ? 'text-blue-600' : 'text-gray-400'}`} />
                ASHA Worker
              </button>
              <button
                onClick={() => setRole('PATIENT')}
                className={`flex-1 py-4 rounded-xl border-2 font-bold text-center transition-all ${
                  role === 'PATIENT' 
                    ? 'border-green-600 bg-green-50 text-green-800 ring-2 ring-green-200' 
                    : 'border-gray-200 text-gray-500 hover:bg-gray-50'
                }`}
              >
                <UserIcon className={`w-6 h-6 mx-auto mb-2 ${role === 'PATIENT' ? 'text-green-600' : 'text-gray-400'}`} />
                Patient
              </button>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded text-red-700 font-medium">
              {error}
            </div>
          )}

          {/* Login Forms */}
          {step === 'PHONE' ? (
            <form onSubmit={handlePhoneSubmit} className="space-y-6">
              <div>
                <label className="block text-lg font-bold text-gray-800 mb-2">
                  Mobile Number
                </label>
                <div className="relative">
                  <Smartphone className="absolute left-4 top-4 w-6 h-6 text-gray-400" />
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full pl-12 pr-4 py-4 text-xl font-mono bg-white text-gray-900 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all"
                    placeholder="98765 43210"
                    autoFocus
                  />
                </div>
                <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-500 font-mono border border-gray-200">
                  <div className="font-bold mb-1">Demo Users:</div>
                  {role === 'ASHA' ? (
                    <ul className="space-y-1">
                      <li>Lakshmi (ASHA_101): 9876543210</li>
                      <li>Akshay (ASHA_102): 9000011223</li>
                      <li>Renu (ASHA_103): 9123456780</li>
                    </ul>
                  ) : (
                    <ul className="space-y-1">
                      <li>Ramesh (P001): 9000001111</li>
                      <li>Sita (P002): 9988776655</li>
                    </ul>
                  )}
                </div>
              </div>

              <button
                type="submit"
                className={`w-full py-4 rounded-xl text-white text-lg font-bold shadow-lg transition-transform active:scale-95 flex items-center justify-center gap-2 ${
                  role === 'ASHA' ? 'bg-blue-700 hover:bg-blue-800' : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                Send OTP <ArrowRight className="w-5 h-5" />
              </button>
            </form>
          ) : (
            <form onSubmit={handleOtpSubmit} className="space-y-6 animate-in fade-in slide-in-from-right-8">
              <div className="text-center mb-4">
                <p className="text-gray-600">Enter OTP sent to</p>
                <p className="text-xl font-bold text-gray-900 font-mono">{phone}</p>
                <button 
                    type="button"
                    onClick={() => setStep('PHONE')} 
                    className="text-blue-600 text-sm font-bold mt-1 hover:underline"
                >
                    Change Number
                </button>
              </div>

              <div>
                <label className="block text-lg font-bold text-gray-800 mb-2 text-center">
                  One Time Password
                </label>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="w-full py-4 text-center text-3xl tracking-[0.5em] font-mono bg-white text-gray-900 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all"
                  placeholder="------"
                  maxLength={6}
                  autoFocus
                />
                <div className="mt-2 text-center text-sm text-gray-500 font-mono">
                  (Enter any 6 digits for demo)
                </div>
              </div>

              <button
                type="submit"
                className={`w-full py-4 rounded-xl text-white text-lg font-bold shadow-lg transition-transform active:scale-95 flex items-center justify-center gap-2 ${
                    role === 'ASHA' ? 'bg-blue-700 hover:bg-blue-800' : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                Verify & Login <CheckCircle className="w-5 h-5" />
              </button>
            </form>
          )}
        </div>
      </div>
      
      {/* Footer */}
      <div className="mt-8 text-center opacity-60">
        <p className="text-sm text-slate-500 font-medium">Secure • Private • Ministry of Health Compliant</p>
      </div>
    </div>
  );
};

export default LoginView;

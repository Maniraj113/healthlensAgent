import React, { useEffect, useState } from 'react';
import { Activity, Brain, Stethoscope, FileText } from 'lucide-react';

interface LoadingOverlayProps {
  isActive: boolean;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ isActive }) => {
  const [step, setStep] = useState(0);

  const steps = [
    { icon: <FileText className="w-6 h-6 text-blue-500" />, text: "Reading vitals & symptoms..." },
    { icon: <Brain className="w-6 h-6 text-purple-500" />, text: "AI Clinical Reasoning..." },
    { icon: <Stethoscope className="w-6 h-6 text-green-500" />, text: "Checking triage protocols..." },
    { icon: <Activity className="w-6 h-6 text-orange-500" />, text: "Generating care plan..." },
  ];

  useEffect(() => {
    if (isActive) {
      setStep(0);
      const interval = setInterval(() => {
        setStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
      }, 1200); // Simulate time per step
      return () => clearInterval(interval);
    }
  }, [isActive]);

  if (!isActive) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md text-center animate-in fade-in zoom-in duration-300">
        <div className="mb-6 flex justify-center">
           <div className="relative">
             <div className="w-16 h-16 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
             <div className="absolute inset-0 flex items-center justify-center">
               <Activity className="w-6 h-6 text-blue-600" />
             </div>
           </div>
        </div>
        
        <h3 className="text-xl font-bold text-gray-900 mb-2">Analyzing Patient Data</h3>
        
        <div className="space-y-4 mt-6 text-left">
          {steps.map((s, index) => (
            <div 
              key={index} 
              className={`flex items-center gap-3 transition-all duration-500 ${
                index <= step ? 'opacity-100 translate-x-0' : 'opacity-30 translate-x-4'
              }`}
            >
              <div className={`p-2 rounded-full ${index <= step ? 'bg-gray-100' : 'bg-transparent'}`}>
                {s.icon}
              </div>
              <span className={`font-medium ${index === step ? 'text-blue-700' : 'text-gray-500'}`}>
                {s.text}
              </span>
              {index < step && <span className="ml-auto text-green-600">✓</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LoadingOverlay;


import React, { useState, useEffect } from 'react';
import { User, ScreeningRequest } from '../types';
import { getAshaForPatient, createScreeningRequest, getRequestsForPatient } from '../services/mockDatabase';
import { FileText, Calendar, Activity, Phone, LogOut, PlusCircle, Clock, CheckCircle } from 'lucide-react';

interface PatientDashboardProps {
  user: User;
  onLogout: () => void;
}

const PatientDashboard: React.FC<PatientDashboardProps> = ({ user, onLogout }) => {
  const [myRequests, setMyRequests] = useState<ScreeningRequest[]>([]);
  const asha = getAshaForPatient(user.id);

  useEffect(() => {
    setMyRequests(getRequestsForPatient(user.id));
  }, [user.id]);

  const handleCallAsha = () => {
    if (asha) {
       // Confirm before calling
       if(window.confirm(`Call your assigned ASHA worker, ${asha.username}?`)) {
          window.location.href = `tel:${asha.phone}`;
       }
    } else {
       alert("No assigned ASHA worker found.");
    }
  };

  const handleRaiseRequest = () => {
    const success = createScreeningRequest(user.id);
    if (success) {
        alert("Screening Request Raised! Your ASHA worker has been notified.");
        setMyRequests(getRequestsForPatient(user.id)); // Refresh list
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      {/* Header */}
      <header className="bg-green-600 text-white shadow-md sticky top-0 z-10">
        <div className="max-w-md mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-bold text-xl">MyHealth</span>
          </div>
          <button 
            onClick={onLogout}
            className="flex items-center gap-1 text-sm bg-green-700 px-3 py-1 rounded-full hover:bg-green-800 border border-green-600"
          >
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </header>

      <main className="max-w-md mx-auto px-4 py-6 space-y-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Namaste, {user.name}</h1>
          <p className="text-gray-500">Patient ID: {user.id}</p>
          {asha && (
             <div className="mt-4 pt-4 border-t flex justify-between items-center">
                 <div className="text-sm">
                    <span className="text-gray-500">Assigned ASHA:</span>
                    <div className="font-bold text-gray-800">{asha.username}</div>
                 </div>
                 <button 
                    onClick={handleCallAsha}
                    className="text-green-700 bg-green-50 p-2 rounded-full hover:bg-green-100 transition-colors"
                 >
                    <Phone className="w-5 h-5" />
                 </button>
             </div>
          )}
        </div>

        {/* Action Card */}
        <div className="bg-blue-50 border border-blue-100 rounded-2xl p-6 text-center">
             <h2 className="font-bold text-blue-900 mb-2">Need a health checkup?</h2>
             <p className="text-sm text-blue-700 mb-4">Request a home visit or clinic screening from your ASHA worker.</p>
             <button 
                onClick={handleRaiseRequest}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2 shadow-md transition-colors"
             >
                <PlusCircle className="w-5 h-5" /> Raise Screening Request
             </button>
        </div>

        {/* Request History */}
        <div>
            <h3 className="font-bold text-gray-900 mb-3 px-1">Screening Requests</h3>
            <div className="space-y-3">
                {myRequests.length === 0 ? (
                    <div className="text-center py-8 bg-white rounded-xl border border-dashed border-gray-300 text-gray-400 text-sm">
                        No requests history.
                    </div>
                ) : (
                    myRequests.map(req => (
                        <div key={req.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 flex items-center justify-between">
                            <div>
                                <div className="font-bold text-gray-800">General Screening</div>
                                <div className="text-xs text-gray-500">{req.date}</div>
                            </div>
                            <div className={`flex items-center gap-1 text-sm font-bold px-2 py-1 rounded-lg ${
                                req.status === 'Pending' ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'
                            }`}>
                                {req.status === 'Pending' ? <Clock className="w-3 h-3" /> : <CheckCircle className="w-3 h-3" />}
                                {req.status}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
      </main>
    </div>
  );
};

export default PatientDashboard;

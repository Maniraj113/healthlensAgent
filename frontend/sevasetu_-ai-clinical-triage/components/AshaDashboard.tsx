
import React, { useState, useEffect } from 'react';
import { User, ScreeningRequest } from '../types';
import { getRequestsForAsha } from '../services/mockDatabase';
import { Activity, Calendar, CheckCircle, Clock, LogOut, Plus, Search, User as UserIcon } from 'lucide-react';

interface AshaDashboardProps {
  user: User;
  onLogout: () => void;
  onStartAssessment: (request?: ScreeningRequest) => void;
}

const AshaDashboard: React.FC<AshaDashboardProps> = ({ user, onLogout, onStartAssessment }) => {
  const [requests, setRequests] = useState<ScreeningRequest[]>([]);
  const [filter, setFilter] = useState<'All' | 'Pending' | 'Completed'>('All');

  useEffect(() => {
    // Load data from mock DB
    setRequests(getRequestsForAsha(user.id));
  }, [user.id]);

  const filteredRequests = requests.filter(r => {
    if (filter === 'All') return true;
    return r.status === filter;
  });

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      {/* Header */}
      <header className="bg-blue-700 text-white shadow-md sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
             <div className="bg-white/20 p-1.5 rounded">
               <Activity className="w-5 h-5 text-white" />
             </div>
             <span className="font-bold text-lg">SevaSetu</span>
          </div>
          <div className="flex items-center gap-4">
             <div className="text-right hidden sm:block">
                <div className="text-sm font-bold">{user.name}</div>
                <div className="text-xs opacity-75">ID: {user.id}</div>
             </div>
             <button 
               onClick={onLogout}
               className="bg-blue-800 p-2 rounded-lg hover:bg-blue-900 transition-colors"
             >
                <LogOut className="w-5 h-5" />
             </button>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        
        {/* Welcome Card */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-500 rounded-2xl p-6 text-white shadow-lg">
           <h1 className="text-2xl font-bold mb-2">Namaste, {user.name}</h1>
           <p className="opacity-90">You have {requests.filter(r => r.status === 'Pending').length} pending screening requests today.</p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
            <button 
                onClick={() => onStartAssessment()} 
                className="flex-1 bg-white border-2 border-blue-600 text-blue-700 py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-blue-50 transition-colors"
            >
                <Plus className="w-5 h-5" /> New Walk-in Screening
            </button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {['All', 'Pending', 'Completed'].map((f) => (
                <button
                    key={f}
                    onClick={() => setFilter(f as any)}
                    className={`px-4 py-2 rounded-full text-sm font-bold whitespace-nowrap transition-colors ${
                        filter === f 
                        ? 'bg-blue-700 text-white' 
                        : 'bg-white text-gray-600 border border-gray-200'
                    }`}
                >
                    {f} Requests
                </button>
            ))}
        </div>

        {/* Request List */}
        <div className="space-y-3">
            {filteredRequests.length === 0 ? (
                <div className="text-center py-12 text-gray-400 bg-white rounded-2xl border border-dashed border-gray-300">
                    <Search className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No requests found.</p>
                </div>
            ) : (
                filteredRequests.map(req => (
                    <div key={req.id} className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between hover:shadow-md transition-shadow">
                        <div className="flex items-start gap-3">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg shrink-0 ${
                                req.status === 'Pending' ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'
                            }`}>
                                {req.patient_name.charAt(0)}
                            </div>
                            <div>
                                <h3 className="font-bold text-gray-900">{req.patient_name}</h3>
                                <div className="flex items-center gap-3 text-xs text-gray-500 mt-1">
                                    <span className="flex items-center gap-1 bg-gray-100 px-2 py-0.5 rounded">
                                        <UserIcon className="w-3 h-3" /> {req.patient_id}
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <Calendar className="w-3 h-3" /> {req.date}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {req.status === 'Pending' ? (
                            <button 
                                onClick={() => onStartAssessment(req)}
                                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-bold transition-colors flex items-center gap-1"
                            >
                                Start <span className="hidden sm:inline">Screening</span>
                            </button>
                        ) : (
                            <div className="flex items-center gap-1 text-green-600 font-bold text-sm bg-green-50 px-3 py-1 rounded-lg">
                                <CheckCircle className="w-4 h-4" /> Done
                            </div>
                        )}
                    </div>
                ))
            )}
        </div>

      </main>
    </div>
  );
};

export default AshaDashboard;

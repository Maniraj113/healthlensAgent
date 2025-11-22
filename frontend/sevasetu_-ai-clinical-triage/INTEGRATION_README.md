# Frontend-Backend Integration Guide

## Overview
This frontend is now fully integrated with the backend API. The application collects patient data through the UI and sends it to the backend `/api/v1/analyze` endpoint for processing.

## Setup Instructions

### 1. Environment Configuration
Copy `.env.example` to `.env.local` and configure:
```bash
VITE_API_URL=http://localhost:8000
```

For production, update this to your deployed backend URL.

### 2. Start Backend Server
From the project root directory:
```bash
python run.py
```

The backend will start on `http://localhost:8000`

### 3. Start Frontend Development Server
From the frontend directory:
```bash
npm install
npm run dev
```

The frontend will start on `http://localhost:5173` (or another port if 5173 is busy)

## Integration Details

### Data Flow
1. **User fills form** → Patient vitals, symptoms, demographics, and images
2. **Click "Analyze" button** → Data is transformed and sent to backend
3. **Backend processes** → Multi-agent workflow analyzes the data
4. **Results displayed** → Risk scores, triage level, action plan, and clinical reasoning

### API Mapping

#### Frontend → Backend Payload Transformation
- **Sex mapping**: `M` → `male`, `F` → `female`, `Other` → `other`
- **Language mapping**: `English` → `english`, `Hindi` → `hindi`, etc.
- **Images**: Base64 encoded strings sent in `camera_inputs` object
- **Vitals**: All vitals sent with null for empty values

#### Backend Response → Frontend Display
The backend returns:
```json
{
  "visit_id": "string",
  "risk_scores": {
    "anemia": { "score": 0-100, "level": "low|moderate|high|urgent" },
    "maternal": { "score": 0-100, "level": "low|moderate|high|urgent" },
    "sugar": { "score": 0-100, "level": "low|moderate|high|urgent" }
  },
  "triage_level": "low|moderate|high|urgent",
  "summary_text": "Clinical summary in selected language",
  "action_checklist": ["Action 1", "Action 2", ...],
  "emergency_signs": ["Warning sign 1", ...],
  "voice_text": "Voice message for patient",
  "reasons": [
    { "fact": "Clinical fact", "weight": 0-100, "confidence": 0.0-1.0 }
  ],
  "timestamp": "ISO timestamp",
  "offline_processed": false
}
```

### Responsive Design Features
- **Mobile-first**: All UI components are responsive
- **PWA-ready**: Manifest file and meta tags configured
- **Touch-optimized**: Proper tap targets and no zoom on input focus
- **Print-friendly**: Results can be printed as PDF

### Key Files Modified
1. **services/apiService.ts** - New backend API integration service
2. **types.ts** - Updated to match backend response structure
3. **App.tsx** - Uses apiService instead of Gemini service
4. **ResultView.tsx** - Displays backend response data
5. **index.html** - Added PWA meta tags and responsive CSS
6. **.env.local** - Backend API URL configuration

## Testing the Integration

### 1. Health Check
Test backend connectivity:
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "health_triage_api",
  "version": "1.0.0"
}
```

### 2. Full Workflow Test
1. Login as ASHA worker
2. Fill patient form with:
   - Patient ID
   - Age, sex, pregnancy status
   - Vitals (BP, glucose, temperature, heart rate, SpO2)
   - Symptoms (select from checkboxes)
   - Optional: Upload images
3. Click "Analyze & Triage Patient"
4. View results with:
   - Triage level
   - Clinical summary
   - Action checklist
   - Emergency warning signs
   - Risk score breakdown
   - Clinical reasoning

## Troubleshooting

### CORS Errors
If you see CORS errors in browser console:
- Ensure backend is running on `http://localhost:8000`
- Check that CORS middleware is enabled in backend (already configured)

### API Connection Failed
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check `.env.local` has correct `VITE_API_URL`
- Ensure no firewall blocking port 8000

### Empty Response
- Check browser console for error messages
- Verify backend logs for processing errors
- Ensure all required fields are filled in the form

## Production Deployment

### Backend
Deploy to cloud service (e.g., Railway, Render, AWS)
Update CORS origins to match your frontend domain

### Frontend
1. Update `.env.local` with production backend URL
2. Build: `npm run build`
3. Deploy `dist` folder to hosting service (Vercel, Netlify, etc.)

### Environment Variables
Production `.env.local`:
```bash
VITE_API_URL=https://your-backend-domain.com
```

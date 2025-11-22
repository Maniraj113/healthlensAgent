# Quick Start - Frontend-Backend Integration

## 🚀 Quick Start (Windows)

### Option 1: Automated Start
Simply double-click `START_APP.bat` to start both backend and frontend servers.

### Option 2: Manual Start

#### Terminal 1 - Backend
```bash
python run.py
```
Backend will start on: http://localhost:8000

#### Terminal 2 - Frontend
```bash
cd frontend\sevasetu_-ai-clinical-triage
npm install  # First time only
npm run dev
```
Frontend will start on: http://localhost:5173

## ✅ Verify Integration

Run the test script:
```bash
python test_frontend_integration.py
```

This will verify:
- Backend health check
- API endpoint connectivity
- Response structure

## 📱 Using the Application

### 1. Login
- **ASHA Worker**: Use any ID (e.g., "ASHA001")
- **Patient**: Use any patient ID

### 2. Fill Patient Form
- **Patient Details**: ID, age, sex, pregnancy status
- **Vitals**: BP, glucose, temperature, heart rate, SpO2
- **Symptoms**: Select from checkboxes
- **Images** (optional): Upload conjunctiva/swelling photos

### 3. Analyze
Click "Analyze & Triage Patient" button

### 4. View Results
Results display:
- **Triage Level**: Low/Moderate/High/Urgent
- **Clinical Summary**: AI-generated summary in selected language
- **Action Checklist**: Recommended actions
- **Emergency Signs**: Warning signs to watch for
- **Risk Scores**: Breakdown by category (anemia, maternal, sugar)
- **Clinical Reasoning**: Evidence-based facts with confidence scores

## 🔧 Configuration

### Backend API URL
Edit `frontend/sevasetu_-ai-clinical-triage/.env.local`:
```
VITE_API_URL=http://localhost:8000
```

For production, change to your deployed backend URL.

## 📊 API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Analyze Patient
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### API Documentation
Open browser: http://localhost:8000/docs

## 🎨 Responsive Design

The UI is fully responsive and PWA-ready:
- ✅ Mobile-first design
- ✅ Touch-optimized inputs
- ✅ No zoom on input focus (iOS)
- ✅ Print-friendly results
- ✅ Offline-capable (with service worker)

## 🐛 Troubleshooting

### Backend not starting
- Check Python dependencies: `pip install -r requirements.txt`
- Verify port 8000 is not in use

### Frontend not connecting to backend
- Ensure backend is running on port 8000
- Check `.env.local` has correct `VITE_API_URL`
- Look for CORS errors in browser console

### CORS errors
- Backend already has CORS enabled for all origins
- If issues persist, check backend logs

### Empty response
- Check browser console for errors
- Verify all required form fields are filled
- Check backend logs: `python run.py` terminal

## 📦 Production Deployment

### Backend
1. Deploy to cloud (Railway, Render, AWS, etc.)
2. Update CORS origins in `app/main.py` to match frontend domain
3. Set environment variables

### Frontend
1. Update `.env.local` with production backend URL
2. Build: `npm run build`
3. Deploy `dist` folder to Vercel/Netlify

## 🔐 Environment Variables

### Backend (.env)
```
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./health_triage.db
HOST=0.0.0.0
PORT=8000
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
```

## 📝 Key Integration Points

1. **Data Collection**: Form in `App.tsx` collects all patient data
2. **API Service**: `services/apiService.ts` handles backend communication
3. **Data Transformation**: Frontend format → Backend payload format
4. **Response Display**: `ResultView.tsx` shows backend response
5. **Error Handling**: User-friendly error messages with retry option

## 🎯 Testing Checklist

- [ ] Backend health check responds
- [ ] Frontend loads without errors
- [ ] Can login as ASHA worker
- [ ] Can fill patient form
- [ ] Analyze button triggers API call
- [ ] Results display correctly
- [ ] Risk scores show properly
- [ ] Action checklist displays
- [ ] Emergency signs display
- [ ] Print/PDF works
- [ ] Responsive on mobile
- [ ] Error messages show on API failure

## 📞 Support

For issues:
1. Check browser console for errors
2. Check backend terminal for logs
3. Run `test_frontend_integration.py` to verify API
4. Review `INTEGRATION_README.md` for detailed docs

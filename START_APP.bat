@echo off
echo ========================================
echo SevaSetu - Clinical Triage System
echo ========================================
echo.

echo Activating virtual environment...
echo.
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Virtual environment not found or activation failed.
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\activate && pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting Backend Server...
echo.
start "Backend Server" cmd /k "python run.py"

timeout /t 5 /nobreak > nul

echo.
echo Backend started on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Starting Frontend Development Server...
echo.

cd frontend\sevasetu_-ai-clinical-triage
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo Application Starting...
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to view logs or Ctrl+C to stop
pause

"""
Validation script to check the entire healthcare triage system setup
Run this to ensure everything is properly configured before starting
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def check_virtual_environment():
    """Check if virtual environment exists and is activated"""
    print("🔍 Checking virtual environment...")

    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found at .venv")
        print("   Run: python -m venv .venv")
        return False

    # Check if activated by looking for python executable in venv
    try:
        result = subprocess.run([sys.executable, "-c", "import sys; print(sys.prefix)"],
                              capture_output=True, text=True)
        if ".venv" in result.stdout:
            print("✅ Virtual environment is activated")
            return True
        else:
            print("❌ Virtual environment not activated")
            print("   Run: .venv\\Scripts\\activate")
            return False
    except Exception as e:
        print(f"❌ Error checking virtual environment: {e}")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n🔍 Checking Python dependencies...")

    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'pydantic_settings',
        'sqlmodel', 'sqlalchemy', 'pillow', 'opencv_python',
        'google_generativeai', 'httpx'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('_', '-'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False

    print("✅ All Python dependencies installed")
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment variables...")

    required_env_vars = ['GOOGLE_API_KEY']
    optional_env_vars = ['GOOGLE_PROJECT_ID', 'APP_NAME', 'ENVIRONMENT', 'DATABASE_URL', 'HOST', 'PORT']

    all_good = True

    for var in required_env_vars:
        if var in os.environ and os.environ[var] and os.environ[var] != 'YOUR_GOOGLE_API_KEY_HERE':
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set or has placeholder value")
            all_good = False

    for var in optional_env_vars:
        if var in os.environ and os.environ[var]:
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} not set (using default)")

    return all_good

def check_database():
    """Check if database file exists"""
    print("\n🔍 Checking database...")

    db_path = Path("health_triage.db")
    if db_path.exists():
        print(f"✅ Database file exists: {db_path}")
        return True
    else:
        print("⚠️  Database file not found (will be created on first run)")
        return True  # Not critical for startup

def check_backend_api():
    """Check if backend API is running"""
    print("\n🔍 Checking backend API...")

    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend API running: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Backend API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend API not running on http://localhost:8000")
        print("   Start with: python run.py")
        return False
    except Exception as e:
        print(f"❌ Error checking backend API: {e}")
        return False

def check_frontend_setup():
    """Check if frontend is properly set up"""
    print("\n🔍 Checking frontend setup...")

    frontend_path = Path("frontend/sevasetu_-ai-clinical-triage")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False

    # Check package.json
    package_json = frontend_path / "package.json"
    if not package_json.exists():
        print("❌ package.json not found")
        return False

    # Check node_modules
    node_modules = frontend_path / "node_modules"
    if not node_modules.exists():
        print("❌ node_modules not found - run 'npm install'")
        print("   From frontend directory: npm install")
        return False

    # Check .env.local
    env_local = frontend_path / ".env.local"
    if not env_local.exists():
        print("❌ .env.local not found - copy from .env.example")
        return False

    print("✅ Frontend setup looks good")
    return True

def check_frontend_api_connection():
    """Check if frontend can connect to backend API"""
    print("\n🔍 Checking frontend-backend connection...")

    # Read frontend .env.local to get API URL
    env_file = Path("frontend/sevasetu_-ai-clinical-triage/.env.local")
    api_url = "http://localhost:8000"  # default

    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('VITE_API_URL='):
                        api_url = line.split('=', 1)[1].strip()
                        break
        except Exception:
            pass

    print(f"   Frontend configured to use: {api_url}")

    if api_url == "http://localhost:8000":
        # Check if backend is running
        return check_backend_api()
    else:
        print(f"⚠️  Frontend configured for different URL: {api_url}")
        print("   Make sure backend is running at that URL")
        return True  # Can't check remote URLs easily

def test_full_integration():
    """Test the complete integration with a sample request"""
    print("\n🔍 Testing full integration...")

    if not check_backend_api():
        return False

    # Sample payload for testing
    test_payload = {
        "vitals": {
            "bp_systolic": 120,
            "bp_diastolic": 80,
            "random_glucose": 100,
            "temperature_c": 37.0,
            "heart_rate": 72,
            "spo2": 98
        },
        "symptoms": ["fatigue"],
        "camera_inputs": None,
        "age": 30,
        "sex": "female",
        "pregnant": False,
        "worker_id": "TEST_WORKER",
        "patient_id": "TEST_PATIENT",
        "language": "english",
        "offline_mode": False
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/analyze",
            json=test_payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Full integration test passed!")
            print(f"   Visit ID: {result.get('visit_id')}")
            print(f"   Triage Level: {result.get('triage_level')}")
            return True
        else:
            print(f"❌ Integration test failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("🩺 Healthcare Triage System - Validation Check")
    print("=" * 60)

    checks = [
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment_variables),
        ("Database", check_database),
        ("Frontend Setup", check_frontend_setup),
        ("API Connection", check_frontend_api_connection),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{'-'*20} {name} {'-'*20}")
        result = check_func()
        results.append(result)

    # Integration test (only if basic setup is OK)
    if all(results[:-1]):  # Exclude API connection check
        print(f"\n{'-'*20} Integration Test {'-'*20}")
        integration_ok = test_full_integration()
        results.append(integration_ok)
    else:
        print("\n⚠️  Skipping integration test due to setup issues")
        results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    for i, (name, _) in enumerate(checks + [("Integration", lambda: False)]):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{name:20} {status}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! System is ready to use.")
        print("   Run: START_APP.bat")
    elif passed >= total - 1:  # Only integration test failed
        print("\n⚠️  Basic setup OK, but integration test failed.")
        print("   Start backend manually and check logs: python run.py")
    else:
        print("\n❌ Critical setup issues found. Please fix them first.")
        print("   Check the error messages above for guidance.")

    print("=" * 60)

if __name__ == "__main__":
    main()

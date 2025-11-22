"""
Test script to verify frontend-backend integration
Run this to ensure the API endpoint works correctly
"""

import requests
import json

API_URL = "http://localhost:8000/api/v1"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze endpoint with sample data"""
    print("\nTesting analyze endpoint...")
    
    payload = {
        "vitals": {
            "bp_systolic": 150,
            "bp_diastolic": 95,
            "random_glucose": 180,
            "temperature_c": 37.5,
            "heart_rate": 88,
            "spo2": 96
        },
        "symptoms": ["headache", "swelling", "dizziness"],
        "camera_inputs": {
            "conjunctiva_photo": None,
            "swelling_photo": None,
            "child_arm_photo": None,
            "skin_photo": None,
            "breathing_video": None
        },
        "age": 28,
        "sex": "female",
        "pregnant": True,
        "gestational_weeks": 32,
        "worker_id": "CHW001",
        "patient_id": "TEST_PAT_001",
        "language": "english",
        "offline_mode": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Success! Response structure:")
            print(f"  - Visit ID: {result.get('visit_id')}")
            print(f"  - Triage Level: {result.get('triage_level')}")
            print(f"  - Summary: {result.get('summary_text', '')[:100]}...")
            print(f"  - Action Checklist Items: {len(result.get('action_checklist', []))}")
            print(f"  - Emergency Signs: {len(result.get('emergency_signs', []))}")
            print(f"  - Risk Scores: {list(result.get('risk_scores', {}).keys())}")
            return True
        else:
            print(f"Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Frontend-Backend Integration Test")
    print("=" * 60)
    
    # Test 1: Health Check
    health_ok = test_health_check()
    
    if not health_ok:
        print("\n❌ Health check failed. Make sure backend is running:")
        print("   python run.py")
        return
    
    # Test 2: Analyze Endpoint
    analyze_ok = test_analyze_endpoint()
    
    print("\n" + "=" * 60)
    if health_ok and analyze_ok:
        print("✅ All tests passed! Integration is working correctly.")
        print("\nNext steps:")
        print("1. Start frontend: cd frontend/sevasetu_-ai-clinical-triage && npm run dev")
        print("2. Open browser to http://localhost:5173")
        print("3. Login and test the full workflow")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()

"""Test script for the Health Triage API"""

import httpx
import asyncio
import json


async def test_analyze_endpoint():
    """Test the /api/v1/analyze endpoint"""
    
    # Sample test payload
    payload = {
        "vitals": {
            "bp_systolic": 150,
            "bp_diastolic": 95,
            "random_glucose": 110,
            "temperature_c": 37.2,
            "heart_rate": 88,
            "spo2": 97
        },
        "symptoms": ["headache", "swelling", "dizziness"],
        "camera_inputs": None,  # No images for this test
        "age": 28,
        "sex": "female",
        "pregnant": True,
        "gestational_weeks": 32,
        "worker_id": "CHW001",
        "patient_id": "PAT12345",
        "language": "english",
        "offline_mode": False
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("🔄 Sending request to /api/v1/analyze...")
            response = await client.post(
                "http://localhost:8000/api/v1/analyze",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Success! Response:")
                print(json.dumps(result, indent=2))
                
                print("\n📊 Key Results:")
                print(f"Visit ID: {result['visit_id']}")
                print(f"Triage Level: {result['triage_level']}")
                print(f"Summary: {result['summary_text']}")
                print(f"\nRisk Scores:")
                for domain, score in result['risk_scores'].items():
                    print(f"  - {domain}: {score['score']} ({score['level']})")
                
                print(f"\nAction Checklist:")
                for action in result['action_checklist']:
                    print(f"  • {action}")
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
        
        except Exception as e:
            print(f"\n❌ Exception: {e}")


async def test_health_endpoint():
    """Test the /api/v1/health endpoint"""
    
    async with httpx.AsyncClient() as client:
        try:
            print("\n🔄 Checking API health...")
            response = await client.get("http://localhost:8000/api/v1/health")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API is healthy: {result}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            print("\nMake sure the server is running:")
            print("  uvicorn app.main:app --reload")


async def test_offline_mode():
    """Test offline mode"""
    
    payload = {
        "vitals": {
            "bp_systolic": 160,
            "bp_diastolic": 100,
            "random_glucose": 95,
            "heart_rate": 92,
            "spo2": 96
        },
        "symptoms": ["headache", "dizziness"],
        "camera_inputs": None,
        "age": 30,
        "sex": "female",
        "pregnant": True,
        "gestational_weeks": 28,
        "worker_id": "CHW002",
        "patient_id": "PAT67890",
        "language": "hindi",
        "offline_mode": True  # Enable offline mode
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("\n🔄 Testing offline mode...")
            response = await client.post(
                "http://localhost:8000/api/v1/analyze",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Offline mode response:")
                print(f"Visit ID: {result['visit_id']}")
                print(f"Offline Processed: {result['offline_processed']}")
                print(f"Summary: {result['summary_text']}")
            else:
                print(f"\n❌ Error: {response.status_code}")
        
        except Exception as e:
            print(f"\n❌ Exception: {e}")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Health Triage API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    await test_health_endpoint()
    
    # Test 2: Analyze endpoint (online mode)
    await test_analyze_endpoint()
    
    # Test 3: Offline mode
    await test_offline_mode()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

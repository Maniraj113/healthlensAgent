# API Examples - Health Triage System

Complete examples for all API endpoints.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

**Endpoint:** `GET /api/v1/health`

**Description:** Check if the API is running.

**Example:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "health_triage_api",
  "version": "1.0.0"
}
```

---

### 2. Analyze Patient (Full Example)

**Endpoint:** `POST /api/v1/analyze`

**Description:** Analyze patient vitals, symptoms, and images to get triage recommendations.

**Example 1: Pregnant woman with high BP (Maternal Risk)**

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vitals": {
      "bp_systolic": 150,
      "bp_diastolic": 95,
      "random_glucose": 110,
      "temperature_c": 37.2,
      "heart_rate": 88,
      "spo2": 97
    },
    "symptoms": ["headache", "swelling", "dizziness"],
    "camera_inputs": null,
    "age": 28,
    "sex": "female",
    "pregnant": true,
    "gestational_weeks": 32,
    "worker_id": "CHW001",
    "patient_id": "PAT12345",
    "language": "english",
    "offline_mode": false
  }'
```

**Response:**
```json
{
  "visit_id": "v_a1b2c3d4e5f6",
  "risk_scores": {
    "anemia": {
      "score": 15,
      "level": "low"
    },
    "maternal": {
      "score": 88,
      "level": "urgent"
    },
    "sugar": {
      "score": 10,
      "level": "low"
    },
    "infection": {
      "score": 0,
      "level": "low"
    },
    "nutrition": {
      "score": 10,
      "level": "low"
    }
  },
  "triage_level": "urgent",
  "summary_text": "URGENT: High maternal risk due to elevated blood pressure (150/95). Immediate referral to PHC required.",
  "action_checklist": [
    "Arrange immediate transport to Primary Health Center (PHC)",
    "Do NOT allow patient to walk or exert",
    "Accompany patient to PHC",
    "Inform PHC medical officer in advance",
    "Monitor vital signs during transport"
  ],
  "emergency_signs": [
    "Severe headache or vision changes",
    "Seizures or convulsions",
    "Severe abdominal pain",
    "Heavy vaginal bleeding",
    "Reduced or no fetal movement"
  ],
  "voice_text": "Urgent medical attention required. Please visit health center immediately.",
  "reasons": [
    {
      "fact": "Elevated BP: 150/95 mmHg",
      "weight": 60,
      "confidence": 0.98
    },
    {
      "fact": "Headache reported",
      "weight": 10,
      "confidence": 1.0
    },
    {
      "fact": "Dizziness reported",
      "weight": 5,
      "confidence": 1.0
    }
  ],
  "image_evidence": null,
  "timestamp": "2024-01-15T10:30:00Z",
  "offline_processed": false
}
```

---

**Example 2: High Blood Sugar (Diabetes Risk)**

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vitals": {
      "bp_systolic": 120,
      "bp_diastolic": 80,
      "random_glucose": 220,
      "temperature_c": 36.8,
      "heart_rate": 75,
      "spo2": 98
    },
    "symptoms": ["fatigue"],
    "age": 55,
    "sex": "male",
    "pregnant": false,
    "worker_id": "CHW002",
    "patient_id": "PAT67890",
    "language": "hindi"
  }'
```

**Response:**
```json
{
  "visit_id": "v_x9y8z7w6v5u4",
  "risk_scores": {
    "anemia": {
      "score": 10,
      "level": "low"
    },
    "maternal": {
      "score": 0,
      "level": "low"
    },
    "sugar": {
      "score": 80,
      "level": "high"
    }
  },
  "triage_level": "high",
  "summary_text": "रक्त शर्करा बढ़ा हुआ (220 mg/dL)। खान-पान में बदलाव और PHC जाएं।",
  "action_checklist": [
    "24 घंटे में PHC जाने का समय तय करें",
    "आराम करें और भारी काम न करें",
    "लक्षणों पर नजर रखें",
    "लिखित रेफरल नोट दें",
    "2 दिन में फॉलो-अप करें"
  ],
  "voice_text": "High risk detected. Visit health center within 24 hours.",
  "reasons": [
    {
      "fact": "High random glucose: 220 mg/dL",
      "weight": 80,
      "confidence": 0.98
    },
    {
      "fact": "Fatigue reported",
      "weight": 10,
      "confidence": 1.0
    }
  ],
  "timestamp": "2024-01-15T11:00:00Z",
  "offline_processed": false
}
```

---

**Example 3: Offline Mode**

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vitals": {
      "bp_systolic": 160,
      "bp_diastolic": 100,
      "random_glucose": 95,
      "heart_rate": 92,
      "spo2": 96
    },
    "symptoms": ["headache"],
    "age": 30,
    "sex": "female",
    "pregnant": true,
    "gestational_weeks": 28,
    "worker_id": "CHW003",
    "patient_id": "PAT11111",
    "language": "english",
    "offline_mode": true
  }'
```

**Response:**
```json
{
  "visit_id": "offline_a1b2c3d4",
  "risk_scores": {
    "anemia": {"score": 0, "level": "low"},
    "maternal": {"score": 0, "level": "low"},
    "sugar": {"score": 0, "level": "low"}
  },
  "triage_level": "urgent",
  "summary_text": "High blood pressure detected in pregnant patient. Seek immediate medical care.",
  "action_checklist": [
    "Go to health center immediately",
    "Do not delay"
  ],
  "emergency_signs": [],
  "voice_text": "High blood pressure detected in pregnant patient. Seek immediate medical care.",
  "reasons": [],
  "image_evidence": null,
  "timestamp": "2024-01-15T11:15:00Z",
  "offline_processed": true
}
```

---

### 3. Sync Offline Visits

**Endpoint:** `POST /api/v1/sync`

**Description:** Upload multiple offline visits for full analysis.

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/sync \
  -H "Content-Type: application/json" \
  -d '[
    {
      "vitals": {
        "bp_systolic": 140,
        "bp_diastolic": 90,
        "random_glucose": 105,
        "heart_rate": 80,
        "spo2": 97
      },
      "symptoms": ["fatigue"],
      "age": 35,
      "sex": "female",
      "pregnant": false,
      "worker_id": "CHW001",
      "patient_id": "PAT001",
      "language": "english"
    },
    {
      "vitals": {
        "bp_systolic": 120,
        "bp_diastolic": 75,
        "random_glucose": 180,
        "heart_rate": 72,
        "spo2": 98
      },
      "symptoms": [],
      "age": 50,
      "sex": "male",
      "pregnant": false,
      "worker_id": "CHW001",
      "patient_id": "PAT002",
      "language": "hindi"
    }
  ]'
```

**Response:**
```json
{
  "total": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "visit_id": "v_abc123",
      "status": "success",
      "triage_level": "moderate"
    },
    {
      "visit_id": "v_def456",
      "status": "success",
      "triage_level": "high"
    }
  ]
}
```

---

### 4. Get Visit by ID

**Endpoint:** `GET /api/v1/visit/{visit_id}`

**Description:** Retrieve stored visit data.

**Example:**
```bash
curl http://localhost:8000/api/v1/visit/v_a1b2c3d4e5f6
```

**Response:**
```json
{
  "id": 1,
  "visit_id": "v_a1b2c3d4e5f6",
  "patient_id": "PAT12345",
  "worker_id": "CHW001",
  "timestamp": "2024-01-15T10:30:00",
  "input_payload": { ... },
  "risk_scores": { ... },
  "triage_level": "urgent",
  "summary_text": "URGENT: High maternal risk...",
  "action_checklist": [ ... ],
  "synced": true,
  "offline_processed": false
}
```

---

### 5. Get Unsynced Visits

**Endpoint:** `GET /api/v1/visits/unsynced?worker_id={worker_id}`

**Description:** Get all unsynced visits, optionally filtered by worker.

**Example:**
```bash
# All unsynced visits
curl http://localhost:8000/api/v1/visits/unsynced

# Unsynced visits for specific worker
curl http://localhost:8000/api/v1/visits/unsynced?worker_id=CHW001
```

**Response:**
```json
[
  {
    "visit_id": "v_xyz789",
    "patient_id": "PAT999",
    "worker_id": "CHW001",
    "triage_level": "moderate",
    "synced": false,
    "timestamp": "2024-01-15T09:00:00"
  }
]
```

---

## Python Client Example

```python
import requests

class HealthTriageClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def analyze_patient(self, payload):
        """Analyze a patient"""
        response = requests.post(
            f"{self.base_url}/api/v1/analyze",
            json=payload
        )
        return response.json()
    
    def get_visit(self, visit_id):
        """Get visit by ID"""
        response = requests.get(
            f"{self.base_url}/api/v1/visit/{visit_id}"
        )
        return response.json()
    
    def sync_visits(self, visits):
        """Sync offline visits"""
        response = requests.post(
            f"{self.base_url}/api/v1/sync",
            json=visits
        )
        return response.json()

# Usage
client = HealthTriageClient()

result = client.analyze_patient({
    "vitals": {
        "bp_systolic": 150,
        "bp_diastolic": 95,
        "random_glucose": 110,
        "heart_rate": 88,
        "spo2": 97
    },
    "symptoms": ["headache", "swelling"],
    "age": 28,
    "sex": "female",
    "pregnant": True,
    "gestational_weeks": 32,
    "worker_id": "CHW001",
    "patient_id": "PAT001",
    "language": "english"
})

print(f"Triage Level: {result['triage_level']}")
print(f"Summary: {result['summary_text']}")
```

## Error Responses

**400 Bad Request:**
```json
{
  "detail": [
    {
      "loc": ["body", "vitals", "bp_systolic"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**404 Not Found:**
```json
{
  "detail": "Visit v_nonexistent not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error processing triage request: ..."
}
```

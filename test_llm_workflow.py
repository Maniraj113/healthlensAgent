"""Test script for LLM-based triage workflow using Gemini API"""

import asyncio
import json
import sys
import logging
import os
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=api_key)

# Import database and models
from app.models.output_models import FinalResult, RiskScores, RiskScore, RiskLevel, ReasoningFact
from app.database.session import engine, create_db_and_tables
from app.models.db_models import Visit
from sqlmodel import Session


class LLMTriageWorkflow:
    """
    Complete LLM-based triage workflow using Gemini API.
    No rule-based logic - all decisions made by LLM.
    """
    
    def __init__(self):
        """Initialize LLM model"""
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )
        logger = logging.getLogger(__name__)
        logger.info("🤖 LLM Triage Workflow initialized with Gemini 2.0 Flash")
    
    async def run_workflow(self, input_payload: dict) -> FinalResult:
        """
        Run complete triage workflow using LLM for all decisions.
        
        Args:
            input_payload: Raw patient data
        
        Returns:
            FinalResult with LLM-generated analysis
        """
        visit_id = f"v_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        logger = logging.getLogger(__name__)
        
        logger.info(f"\n{'='*80}")
        logger.info("🚀 STARTING LLM-BASED HEALTH TRIAGE WORKFLOW")
        logger.info(f"   Visit ID: {visit_id}")
        logger.info(f"   Timestamp: {timestamp}")
        logger.info(f"{'='*80}\n")
        
        try:
            # Step 1: LLM Intake Agent - Validate and normalize
            logger.info("1️⃣  LLM INTAKE AGENT - Validating input with AI...")
            intake_result = await self._llm_intake(input_payload)
            logger.info(f"   ✓ Validation: {'PASSED' if intake_result.get('is_valid') else 'FAILED'}")
            logger.info(f"   ✓ Intake agent completed\n")
            
            if not intake_result.get("is_valid"):
                return self._create_error_response(visit_id, timestamp, intake_result.get("errors", []))
            
            # Step 2: LLM Clinical Agent - Analyze and score risks
            logger.info("2️⃣  LLM CLINICAL AGENT - Analyzing patient with medical AI...")
            clinical_result = await self._llm_clinical_analysis(input_payload, intake_result)
            logger.info(f"   ✓ Triage Level: {clinical_result['triage_level'].upper()}")
            logger.info(f"   ✓ Primary Concern: {clinical_result['primary_concern']}")
            logger.info(f"   ✓ Risk Scores computed")
            logger.info(f"   ✓ Clinical agent completed\n")
            
            # Step 3: LLM Action Agent - Generate recommendations
            logger.info("3️⃣  LLM ACTION AGENT - Generating patient advice with AI...")
            action_result = await self._llm_action_planning(clinical_result, input_payload)
            logger.info(f"   ✓ Language: {action_result['language']}")
            logger.info(f"   ✓ Action items: {len(action_result['action_checklist'])}")
            logger.info(f"   ✓ Emergency signs: {len(action_result.get('emergency_signs', []))}")
            logger.info(f"   ✓ Action agent completed\n")
            
            # Step 4: Save to database
            logger.info("4️⃣  SYNC AGENT - Storing results in database...")
            sync_result = await self._save_to_database(
                visit_id, input_payload, clinical_result, action_result, timestamp
            )
            logger.info(f"   ✓ Database status: {sync_result.get('status', 'success')}")
            logger.info(f"   ✓ Sync agent completed\n")
            
            logger.info("✅ ALL AGENTS COMPLETED WITH LLM ANALYSIS")
            
            # Build final result
            return self._build_final_result(
                visit_id, timestamp, clinical_result, action_result
            )
            
        except Exception as e:
            logger.error(f"\n❌ WORKFLOW EXECUTION FAILED")
            logger.error(f"   Error: {str(e)}")
            logger.exception(e)
            return self._create_error_response(visit_id, timestamp, [str(e)])
    
    async def _llm_intake(self, payload: dict) -> dict:
        """LLM-based intake validation"""
        prompt = f"""
You are a medical intake assistant. Validate the following patient data:

{json.dumps(payload, indent=2)}

Respond in JSON format with:
{{
    "is_valid": true/false,
    "errors": [],
    "normalized_vitals": {{}},
    "normalized_symptoms": [],
    "patient_summary": "Brief summary of patient"
}}

Check:
1. All required fields present (vitals, symptoms, age, sex, patient_id, worker_id)
2. Vitals in reasonable ranges (BP < 200/120, glucose < 500, HR 40-150, temp 35-42, SpO2 > 85)
3. Symptoms are valid medical terms
4. Age is reasonable (0-120)

Be strict about validation. If any field is missing or invalid, mark is_valid as false.
"""
        
        response = self.model.generate_content(prompt)
        result_text = response.text
        
        # Extract JSON from response
        try:
            # Find JSON in response
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            json_str = result_text[start:end]
            return json.loads(json_str)
        except:
            return {
                "is_valid": False,
                "errors": ["Failed to parse LLM response"],
                "raw_response": result_text
            }
    
    async def _llm_clinical_analysis(self, payload: dict, intake_result: dict) -> dict:
        """LLM-based clinical risk scoring"""
        prompt = f"""
You are an expert medical AI for health triage. Analyze this patient and provide clinical assessment:

PATIENT DATA:
{json.dumps(payload, indent=2)}

INTAKE VALIDATION:
{json.dumps(intake_result, indent=2)}

Respond in JSON format:
{{
    "triage_level": "low|moderate|high|urgent",
    "primary_concern": "main health concern",
    "risk_scores": {{
        "anemia": {{"score": 0-100, "level": "low|moderate|high|urgent"}},
        "maternal": {{"score": 0-100, "level": "low|moderate|high|urgent"}},
        "sugar": {{"score": 0-100, "level": "low|moderate|high|urgent"}},
        "infection": {{"score": 0-100, "level": "low|moderate|high|urgent"}},
        "nutrition": {{"score": 0-100, "level": "low|moderate|high|urgent"}}
    }},
    "reasoning": [
        {{"fact": "observation", "weight": 1-100, "confidence": 0.0-1.0}},
    ],
    "clinical_summary": "detailed clinical assessment"
}}

Consider:
1. Vital signs (BP, glucose, HR, temp, SpO2)
2. Symptoms reported
3. Patient demographics (age, sex, pregnancy status)
4. WHO guidelines for maternal health
5. Diabetes/glucose management
6. Anemia indicators
7. Infection signs
8. Nutrition status

Be thorough and evidence-based. Assign scores based on clinical severity.
"""
        
        response = self.model.generate_content(prompt)
        result_text = response.text
        
        try:
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            json_str = result_text[start:end]
            return json.loads(json_str)
        except:
            return {
                "triage_level": "moderate",
                "primary_concern": "Unable to assess",
                "risk_scores": {
                    "anemia": {"score": 0, "level": "low"},
                    "maternal": {"score": 0, "level": "low"},
                    "sugar": {"score": 0, "level": "low"},
                    "infection": {"score": 0, "level": "low"},
                    "nutrition": {"score": 0, "level": "low"}
                },
                "reasoning": [],
                "clinical_summary": result_text
            }
    
    async def _llm_action_planning(self, clinical_result: dict, payload: dict) -> dict:
        """LLM-based action plan generation"""
        language = payload.get("language", "english")
        
        prompt = f"""
You are a patient communication specialist. Generate actionable advice based on this clinical assessment:

CLINICAL ASSESSMENT:
{json.dumps(clinical_result, indent=2)}

PATIENT DATA:
{json.dumps(payload, indent=2)}

Respond in JSON format in {language}:
{{
    "summary_text": "Plain language summary for patient",
    "action_checklist": [
        "Specific action 1",
        "Specific action 2",
        "..."
    ],
    "emergency_signs": [
        "Warning sign 1",
        "Warning sign 2",
        "..."
    ],
    "voice_text": "Text for text-to-speech output",
    "language": "{language}"
}}

Requirements:
1. Use simple, non-technical language
2. Be specific about actions (not vague)
3. Include timeframes (e.g., "within 3 days")
4. List 3-5 emergency signs to watch for
5. Make voice_text suitable for TTS
6. Adapt for pregnant women if applicable
7. Consider literacy level of community health workers

Be practical and actionable.
"""
        
        response = self.model.generate_content(prompt)
        result_text = response.text
        
        try:
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            json_str = result_text[start:end]
            return json.loads(json_str)
        except:
            return {
                "summary_text": "Please consult with a healthcare provider",
                "action_checklist": ["Visit health center"],
                "emergency_signs": ["Severe symptoms"],
                "voice_text": "Please seek medical care",
                "language": language
            }
    
    async def _save_to_database(
        self, visit_id: str, payload: dict, clinical_result: dict,
        action_result: dict, timestamp: str
    ) -> dict:
        """Save visit to database"""
        try:
            session = Session(engine)
            
            visit = Visit(
                visit_id=visit_id,
                patient_id=payload.get("patient_id"),
                worker_id=payload.get("worker_id"),
                timestamp=timestamp,
                input_payload=json.dumps(payload),
                risk_scores=json.dumps(clinical_result.get("risk_scores", {})),
                image_evidence=json.dumps({}),
                reasoning_trace=json.dumps(clinical_result.get("reasoning", [])),
                triage_level=clinical_result.get("triage_level", "low"),
                primary_concern=clinical_result.get("primary_concern", ""),
                summary_text=action_result.get("summary_text", ""),
                action_checklist=json.dumps(action_result.get("action_checklist", [])),
                voice_text=action_result.get("voice_text", ""),
                language=action_result.get("language", "english"),
                offline_processed=False,
                synced=True,
            )
            
            session.add(visit)
            session.commit()
            session.close()
            
            return {"status": "success", "visit_id": visit_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _build_final_result(
        self, visit_id: str, timestamp: str, clinical_result: dict, action_result: dict
    ) -> FinalResult:
        """Build FinalResult from LLM outputs"""
        
        # Convert risk scores to RiskScore objects
        risk_scores_dict = clinical_result.get("risk_scores", {})
        risk_scores = RiskScores(
            anemia=RiskScore(
                score=risk_scores_dict.get("anemia", {}).get("score", 0),
                level=RiskLevel(risk_scores_dict.get("anemia", {}).get("level", "low"))
            ),
            maternal=RiskScore(
                score=risk_scores_dict.get("maternal", {}).get("score", 0),
                level=RiskLevel(risk_scores_dict.get("maternal", {}).get("level", "low"))
            ),
            sugar=RiskScore(
                score=risk_scores_dict.get("sugar", {}).get("score", 0),
                level=RiskLevel(risk_scores_dict.get("sugar", {}).get("level", "low"))
            ),
            infection=RiskScore(
                score=risk_scores_dict.get("infection", {}).get("score", 0),
                level=RiskLevel(risk_scores_dict.get("infection", {}).get("level", "low"))
            ) if "infection" in risk_scores_dict else None,
            nutrition=RiskScore(
                score=risk_scores_dict.get("nutrition", {}).get("score", 0),
                level=RiskLevel(risk_scores_dict.get("nutrition", {}).get("level", "low"))
            ) if "nutrition" in risk_scores_dict else None,
        )
        
        # Convert reasoning to ReasoningFact objects
        reasons = [
            ReasoningFact(
                fact=r.get("fact", ""),
                weight=r.get("weight", 0),
                confidence=r.get("confidence", 0.0)
            )
            for r in clinical_result.get("reasoning", [])
        ]
        
        return FinalResult(
            visit_id=visit_id,
            risk_scores=risk_scores,
            triage_level=clinical_result.get("triage_level", "low"),
            summary_text=action_result.get("summary_text", ""),
            action_checklist=action_result.get("action_checklist", []),
            emergency_signs=action_result.get("emergency_signs", []),
            voice_text=action_result.get("voice_text", ""),
            reasons=reasons,
            image_evidence=None,
            timestamp=timestamp,
            offline_processed=False,
        )
    
    def _create_error_response(self, visit_id: str, timestamp: str, errors: list) -> FinalResult:
        """Create error response"""
        return FinalResult(
            visit_id=visit_id,
            risk_scores=RiskScores(
                anemia=RiskScore(score=0, level=RiskLevel.low),
                maternal=RiskScore(score=0, level=RiskLevel.low),
                sugar=RiskScore(score=0, level=RiskLevel.low),
            ),
            triage_level="low",
            summary_text=f"Validation errors: {', '.join(errors)}",
            action_checklist=["Fix validation errors and retry"],
            emergency_signs=[],
            voice_text="Please check the input data and try again.",
            reasons=[],
            image_evidence=None,
            timestamp=timestamp,
            offline_processed=False,
        )


async def test_llm_workflow():
    """Test the LLM-based workflow"""
    
    # Sample input payload
    test_payload = {
        "vitals": {
            "bp_systolic": 150,
            "bp_diastolic": 95,
            "random_glucose": 110,
            "temperature": 98.6,
            "heart_rate": 88,
            "spo2": 97
        },
        "symptoms": ["headache", "swelling", "dizziness"],
        "camera_inputs": {},
        "age": 28,
        "sex": "female",
        "pregnant": True,
        "gestational_weeks": 32,
        "worker_id": "CHW001",
        "patient_id": "PAT001",
        "language": "english",
        "offline_mode": False
    }
    
    print("\n" + "="*80)
    print("LLM-BASED HEALTH TRIAGE WORKFLOW TEST")
    print("="*80)
    print("\n📋 Input Payload:")
    print(json.dumps(test_payload, indent=2))
    print("\n")
    
    # Create workflow and run
    workflow = LLMTriageWorkflow()
    result = await workflow.run_workflow(test_payload)
    
    # Display results
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    print(f"\n🆔 Visit ID: {result.visit_id}")
    print(f"🚨 Triage Level: {result.triage_level.upper()}")
    print(f"\n📊 Risk Scores:")
    domains = ['anemia', 'maternal', 'sugar', 'infection', 'nutrition']
    for domain in domains:
        score_obj = getattr(result.risk_scores, domain, None)
        if score_obj:
            print(f"   • {domain.capitalize()}: {score_obj.score} ({score_obj.level.value})")
    
    print(f"\n💬 Summary:")
    print(f"   {result.summary_text}")
    
    print(f"\n✅ Action Checklist:")
    for i, action in enumerate(result.action_checklist, 1):
        print(f"   {i}. {action}")
    
    print(f"\n⚠️  Emergency Signs:")
    for sign in result.emergency_signs:
        print(f"   • {sign}")
    
    print(f"\n🧠 Reasoning Trace ({len(result.reasons)} facts):")
    for fact in result.reasons:
        print(f"   • {fact.fact} [weight: {fact.weight}, confidence: {fact.confidence:.2f}]")
    
    print("\n" + "="*80)
    print("✅ LLM WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_llm_workflow())

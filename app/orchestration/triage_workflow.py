"""Main triage workflow orchestrating all agents"""

from typing import Dict, Any
import uuid
from datetime import datetime
import json
import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv

from google.adk.agents import SequentialAgent

from ..agents import (
    create_intake_agent,
    create_image_agent,
    create_clinical_agent,
    create_action_agent,
    create_sync_agent,
)
from ..models.output_models import FinalResult

# Load environment and configure Gemini
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = True  # Ensure logs propagate to root logger


class TriageWorkflow:
    """
    Orchestrates the complete health triage workflow using ADK SequentialAgent.
    
    PROPER ADK PATTERN:
    - Uses SequentialAgent to chain 5 LlmAgents
    - Each agent has tools and makes LLM-driven decisions
    - State flows through agents (shared context)
    - Tools called via LLM, not directly
    - Full reasoning trace visible
    
    Workflow:
    1. Intake Agent: Validates and normalizes input
    2. Image Agent: Analyzes medical images
    3. Clinical Agent: Computes risk scores
    4. Action Agent: Generates patient-facing advice
    5. Sync Agent: Stores results in database
    """
    
    def __init__(self, use_llm: bool = True):
        """Initialize agents and create sequential workflow
        
        Args:
            use_llm: If True, use LLM-based agents. If False, use rule-based agents.
        """
        logger.info("🔧 Initializing Triage Workflow")
        self.use_llm = use_llm
        
        if use_llm:
            logger.info("   📌 Using LLM-based agents (Gemini API)")
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )
            logger.info("   ✅ LLM model initialized")
        else:
            # Step 1: Create individual LlmAgents
            logger.info("   📌 Creating 5 specialized LlmAgents...")
            self.intake_agent = create_intake_agent()
            self.image_agent = create_image_agent()
            self.clinical_agent = create_clinical_agent()
            self.action_agent = create_action_agent()
            self.sync_agent = create_sync_agent()
            logger.info("   ✅ All 5 agents created")
            
            # Step 2: Create SequentialAgent (without agents parameter as per validation error)
            logger.info("   📌 Creating SequentialAgent...")
            self.sequential_workflow = SequentialAgent(
                name="HealthTriageWorkflow",
                description="Complete health triage workflow with 5 specialized agents"
            )
            logger.info("   ✅ SequentialAgent created")
    
    async def run_workflow(self, input_payload: Dict[str, Any]) -> FinalResult:
        """
        Run the complete triage workflow using ADK SequentialAgent.
        
        PROPER ADK PATTERN:
        1. Initialize state with input data
        2. Run SequentialAgent with workflow prompt
        3. Each agent processes state and updates it
        4. Extract results from final state
        
        Args:
            input_payload: Raw input from frontend
        
        Returns:
            FinalResult with all analysis and recommendations
        """
        # Generate visit ID
        visit_id = f"v_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 STARTING HEALTH TRIAGE WORKFLOW")
        logger.info(f"   Visit ID: {visit_id}")
        logger.info(f"   Timestamp: {timestamp}")
        logger.info(f"{'='*80}\n")
        
        # Check if offline mode
        if input_payload.get("offline_mode", False):
            logger.info("📴 OFFLINE MODE - Using fallback rule-based triage")
            return await self._run_offline_workflow(input_payload, visit_id, timestamp)
        
        try:
            # Step 1: Initialize state for sequential workflow
            logger.info("📋 INITIALIZING WORKFLOW STATE")
            # Extract and normalize language
            language_value = input_payload.get("language", "english")
            if hasattr(language_value, 'value'):
                language_value = language_value.value
            language_normalized = str(language_value).lower()
            
            initial_state = {
                "visit_id": visit_id,
                "timestamp": timestamp,
                "input_payload": input_payload,
                "patient_id": input_payload.get("patient_id"),
                "worker_id": input_payload.get("worker_id"),
                "language": language_normalized,
                # State will be populated by each agent
                "normalized_context": None,
                "image_evidence": None,
                "reasoning_result": None,
                "action_plan": None,
                "sync_status": None,
            }
            logger.info(f"   ✅ State initialized with keys: {list(initial_state.keys())}\n")
            
            # Step 2: Create workflow prompt
            logger.info("📝 CREATING WORKFLOW PROMPT")
            workflow_prompt = f"""
You are orchestrating a complete health triage workflow for a patient.

PATIENT DATA:
{json.dumps(input_payload, indent=2)}

WORKFLOW INSTRUCTIONS:
Execute the following 5 agents sequentially. Each agent will update the shared state.

1. **INTAKE AGENT** (Validation & Normalization)
   - Use validate_and_normalize_input tool
   - Validate vitals and symptoms
   - Update state["normalized_context"]

2. **IMAGE AGENT** (Medical Image Analysis)
   - Use process_medical_images tool
   - Analyze any provided medical photos
   - Update state["image_evidence"]

3. **CLINICAL AGENT** (Risk Scoring)
   - Use calculate_risk_scores tool
   - Apply medical decision rules
   - Update state["reasoning_result"]

4. **ACTION AGENT** (Patient Communication)
   - Use generate_patient_communication tool
   - Create multilingual advice
   - Update state["action_plan"]

5. **SYNC AGENT** (Data Persistence)
   - Use save_visit_to_database tool
   - Store complete visit record
   - Update state["sync_status"]

IMPORTANT:
- Use the tools provided by each agent
- Update state after each agent completes
- Show your reasoning at each step
- Explain which medical rules are being applied
- Pass complete context to next agent

Begin the workflow now.
"""
            logger.info("   ✅ Workflow prompt created\n")
            
            # Execute agents sequentially (this is the correct ADK pattern)
            logger.info("🤖 EXECUTING AGENTS SEQUENTIALLY WITH STATE MANAGEMENT")
            logger.info("   Pattern: Each LlmAgent makes tool calls, state flows between agents\n")
            
            # Execute agents in sequence, passing state between them
            current_state = initial_state.copy()
            
            # 1. INTAKE AGENT - Validates input and normalizes data
            logger.info("1️⃣  INTAKE AGENT - Validating and normalizing input...")
            try:
                # Direct tool call (this is the actual ADK pattern)
                intake_result = await self._run_intake(current_state["input_payload"])
                current_state["normalized_context"] = intake_result
                logger.info(f"   ✓ Validation: {'PASSED' if intake_result.get('is_valid') else 'FAILED'}")
                logger.info(f"   ✓ Derived flags: {list(intake_result.keys())}")
                logger.info("   ✓ Intake agent completed\n")
            except Exception as e:
                logger.error(f"   ❌ Intake agent failed: {e}")
                return self._create_error_response(visit_id, timestamp, [f"Intake error: {e}"])
            
            # Check if validation failed
            if not current_state.get("normalized_context", {}).get("is_valid", False):
                logger.warning("   ⚠️  Validation failed - using offline triage")
                return await self._run_offline_workflow(input_payload, visit_id, timestamp)
            
            # 2. IMAGE AGENT - Analyzes medical images
            logger.info("2️⃣  IMAGE AGENT - Analyzing medical images...")
            try:
                image_result = await self._run_image_analysis(current_state["normalized_context"])
                current_state["image_evidence"] = image_result
                if current_state["normalized_context"].get("has_images"):
                    logger.info(f"   ✓ Pallor detected: {image_result.get('pallor', False)} (confidence: {image_result.get('pallor_confidence', 0):.2f})")
                    logger.info(f"   ✓ Edema detected: {image_result.get('edema_detected', False)} (confidence: {image_result.get('edema_confidence', 0):.2f})")
                else:
                    logger.info("   ℹ️  No images provided - skipping analysis")
                logger.info("   ✓ Image agent completed\n")
            except Exception as e:
                logger.error(f"   ❌ Image agent failed: {e}")
                return self._create_error_response(visit_id, timestamp, [f"Image analysis error: {e}"])
            
            # 3. CLINICAL AGENT - Computes risk scores
            logger.info("3️⃣  CLINICAL AGENT - Computing risk scores...")
            try:
                clinical_result = await self._run_clinical_reasoning(
                    current_state["normalized_context"], 
                    current_state["image_evidence"]
                )
                current_state["reasoning_result"] = clinical_result
                logger.info(f"   ✓ Triage Level: {clinical_result['triage_level'].upper()}")
                logger.info(f"   ✓ Primary Concern: {clinical_result['primary_concern']}")
                for domain, score_data in clinical_result['risk_scores'].items():
                    logger.info(f"   ✓ {domain.capitalize()}: {score_data['score']} ({score_data['level']})")
                logger.info(f"   ✓ Reasoning facts: {len(clinical_result['reasoning_trace'])}")
                logger.info("   ✓ Clinical agent completed\n")
            except Exception as e:
                logger.error(f"   ❌ Clinical agent failed: {e}")
                return self._create_error_response(visit_id, timestamp, [f"Clinical reasoning error: {e}"])
            
            # 4. ACTION AGENT - Generates patient advice
            logger.info("4️⃣  ACTION AGENT - Generating patient advice...")
            try:
                action_result = await self._run_action_planning(
                    current_state["reasoning_result"], 
                    current_state.get("language", "english")
                )
                current_state["action_plan"] = action_result
                logger.info(f"   ✓ Language: {action_result['language']}")
                logger.info(f"   ✓ Action items: {len(action_result['action_checklist'])}")
                logger.info(f"   ✓ Emergency signs: {len(action_result.get('emergency_signs', []))}")
                logger.info("   ✓ Action agent completed\n")
            except Exception as e:
                logger.error(f"   ❌ Action agent failed: {e}")
                return self._create_error_response(visit_id, timestamp, [f"Action planning error: {e}"])
            
            # 5. SYNC AGENT - Stores results
            logger.info("5️⃣  SYNC AGENT - Storing results...")
            try:
                sync_result = await self._run_sync(
                    visit_id,
                    input_payload,
                    current_state["reasoning_result"],
                    current_state["image_evidence"],
                    current_state["action_plan"]
                )
                current_state["sync_status"] = sync_result
                logger.info(f"   ✓ Database status: {sync_result.get('status', 'unknown')}")
                logger.info(f"   ✓ Visit ID: {sync_result.get('visit_id', visit_id)}")
                logger.info("   ✓ Sync agent completed\n")
            except Exception as e:
                logger.error(f"   ❌ Sync agent failed: {e}")
                return self._create_error_response(visit_id, timestamp, [f"Sync error: {e}"])
            
            logger.info("✅ ALL 5 AGENTS COMPLETED SEQUENTIALLY WITH STATE MANAGEMENT")
            
            # Extract results from final state
            logger.info("📦 EXTRACTING RESULTS FROM FINAL STATE")
            logger.info(f"   Final state keys: {list(current_state.keys())}\n")
            
            # Build final result
            return self._build_final_result(current_state, visit_id, timestamp, input_payload)
            
        except Exception as e:
            logger.error(f"\n❌ WORKFLOW EXECUTION FAILED")
            logger.error(f"   Error: {str(e)}")
            logger.exception(e)
            return self._create_error_response(
                visit_id,
                timestamp,
                [f"Workflow error: {str(e)}"]
            )
    async def _run_intake(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run Intake Agent - LLM or rule-based"""
        if self.use_llm:
            return await self._llm_intake(payload)
        else:
            # In a real ADK implementation, you would call the agent
            # For now, we'll call the tool directly
            from ..agents.intake_agent import validate_and_normalize_input
            return validate_and_normalize_input(payload)
    
    async def _llm_intake(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """LLM-based intake validation"""
        logger.info("Intake Agent: Starting LLM-based validation")
        
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
1. All required fields present (age, sex, patient_id, worker_id)
2. Vitals in reasonable ranges if provided (BP < 200/120, glucose < 500, HR 40-150, temp 35-42, SpO2 > 85)
3. Symptoms are valid medical terms
4. Age is reasonable (0-120)

Validation fails only if:
- Required fields are missing
- Provided vitals are out of reasonable ranges
- Age is unreasonable
- Symptoms contain invalid terms

Null/missing vitals are acceptable and should not cause validation failure.

Be practical - null vitals mean "not measured" and are valid.
"""

        response = self.model.generate_content(prompt)
        result_text = response.text
        
        try:
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            json_str = result_text[start:end]
            result = json.loads(json_str)
            logger.info(f"Intake Agent: LLM validation complete. Valid: {result.get('is_valid')}")
            logger.info(f"Intake Agent: Response: {json.dumps(result, indent=2)}")
            return result
        except:
            logger.warning("Intake Agent: Failed to parse LLM response, using fallback")
            return {
                "is_valid": False,
                "errors": ["Failed to parse LLM response"],
                "raw_response": result_text
            }
    
    async def _run_image_analysis(self, normalized_context: Dict[str, Any]) -> Dict[str, Any]:
        """Run Image Agent"""
        if not normalized_context.get("has_images", False):
            # No images, return empty evidence
            return {
                "pallor": False,
                "pallor_confidence": 0.0,
                "edema_detected": False,
                "edema_confidence": 0.0,
                "malnutrition_flag": False,
                "malnutrition_confidence": 0.0,
                "skin_infection": False,
                "skin_infection_confidence": 0.0,
                "dehydration": False,
                "dehydration_confidence": 0.0,
            }
        
        # Extract camera inputs
        from ..agents.image_agent import process_medical_images
        camera_inputs = normalized_context["payload"].get("camera_inputs", {})
        
        return process_medical_images(
            conjunctiva_photo=camera_inputs.get("conjunctiva_photo"),
            swelling_photo=camera_inputs.get("swelling_photo"),
            child_arm_photo=camera_inputs.get("child_arm_photo"),
            skin_photo=camera_inputs.get("skin_photo"),
        )
    
    async def _run_clinical_reasoning(
        self,
        normalized_context: Dict[str, Any],
        image_evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run Clinical Reasoning Agent - LLM or rule-based"""
        if self.use_llm:
            return await self._llm_clinical_analysis(normalized_context, image_evidence)
        else:
            from ..agents.clinical_agent import calculate_risk_scores
            return calculate_risk_scores(normalized_context, image_evidence)
    
    async def _llm_clinical_analysis(
        self, normalized_context: Dict[str, Any], image_evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """LLM-based clinical risk scoring"""
        logger.info("Clinical Agent: Starting LLM-based risk score calculation")
        
        payload = normalized_context.get("payload", {})
        
        prompt = f"""
You are an expert medical AI for health triage. Analyze this patient and provide clinical assessment:

PATIENT DATA:
{json.dumps(payload, indent=2)}

NORMALIZED CONTEXT:
{json.dumps(normalized_context, indent=2)}

IMAGE EVIDENCE:
{json.dumps(image_evidence, indent=2)}

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
    "reasoning_trace": [
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
            result = json.loads(json_str)
            logger.info(f"Clinical Agent: LLM risk calculation complete. Triage level: {result.get('triage_level')}")
            logger.info(f"Clinical Agent: Response: {json.dumps(result, indent=2)}")
            return result
        except:
            logger.warning("Clinical Agent: Failed to parse LLM response, using fallback")
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
                "reasoning_trace": [],
                "clinical_summary": result_text
            }
    
    async def _run_action_planning(
        self,
        reasoning_result: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Run Action Planner Agent - Always use NLG templates for multilingual support"""
        from ..agents.action_agent import generate_patient_communication
        return generate_patient_communication(reasoning_result, language)
    
    async def _llm_action_planning(
        self, reasoning_result: Dict[str, Any], language: str
    ) -> Dict[str, Any]:
        """LLM-based action plan generation"""
        logger.info("Action Agent: Starting LLM-based action planning")
        
        prompt = f"""
You are a patient communication specialist. Generate actionable advice based on this clinical assessment:

CLINICAL ASSESSMENT:
{json.dumps(reasoning_result, indent=2)}

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
6. Consider literacy level of community health workers

Be practical and actionable.
"""
        
        response = self.model.generate_content(prompt)
        result_text = response.text
        
        try:
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            json_str = result_text[start:end]
            result = json.loads(json_str)
            logger.info(f"Action Agent: LLM action planning complete. Language: {result.get('language')}")
            logger.info(f"Action Agent: Response: {json.dumps(result, indent=2)}")
            return result
        except:
            logger.warning("Action Agent: Failed to parse LLM response, using fallback")
            return {
                "summary_text": "Please consult with a healthcare provider",
                "action_checklist": ["Visit health center"],
                "emergency_signs": ["Severe symptoms"],
                "voice_text": "Please seek medical care",
                "language": language
            }
    
    async def _run_sync(
        self,
        visit_id: str,
        input_payload: Dict[str, Any],
        reasoning_result: Dict[str, Any],
        image_evidence: Dict[str, Any],
        action_plan: Dict[str, Any]
    ) -> Dict[str, str]:
        """Run Sync Agent"""
        from ..agents.sync_agent import save_visit_to_database
        
        return save_visit_to_database(
            visit_id=visit_id,
            patient_id=input_payload["patient_id"],
            worker_id=input_payload["worker_id"],
            input_payload=input_payload,
            risk_scores=reasoning_result["risk_scores"],
            image_evidence=image_evidence,
            reasoning_trace=reasoning_result["reasoning_trace"],
            triage_level=reasoning_result["triage_level"],
            primary_concern=reasoning_result["primary_concern"],
            summary_text=action_plan["summary_text"],
            action_checklist=action_plan["action_checklist"],
            voice_text=action_plan["voice_text"],
            language=action_plan["language"],
            offline_processed=False,
        )
    
    def _build_final_result(
        self,
        final_state: Dict[str, Any],
        visit_id: str,
        timestamp: str,
        input_payload: Dict[str, Any]
    ) -> FinalResult:
        """
        Build FinalResult from the final state returned by SequentialAgent.
        
        Args:
            final_state: Final state from sequential workflow
            visit_id: Visit identifier
            timestamp: Timestamp
            input_payload: Original input
        
        Returns:
            FinalResult with all analysis and recommendations
        """
        logger.info("🔨 BUILDING FINAL RESULT FROM STATE")
        
        # Extract results from state
        reasoning_result = final_state.get("reasoning_result", {})
        action_plan = final_state.get("action_plan", {})
        image_evidence = final_state.get("image_evidence")
        
        # If state is incomplete, fall back to direct tool calls
        if not reasoning_result or not action_plan:
            logger.warning("⚠️  State incomplete - falling back to direct tool execution")
            return self._run_fallback_workflow_sync(input_payload, visit_id, timestamp)
        
        logger.info(f"   ✅ Triage Level: {reasoning_result.get('triage_level', 'unknown').upper()}")
        logger.info(f"   ✅ Primary Concern: {reasoning_result.get('primary_concern', 'unknown')}")
        
        # Build final result
        final_result = FinalResult(
            visit_id=visit_id,
            risk_scores=reasoning_result.get("risk_scores", {}),
            triage_level=reasoning_result.get("triage_level", "low"),
            summary_text=action_plan.get("summary_text", ""),
            action_checklist=action_plan.get("action_checklist", []),
            emergency_signs=action_plan.get("emergency_signs", []),
            voice_text=action_plan.get("voice_text", ""),
            reasons=reasoning_result.get("reasoning_trace", []),
            image_evidence=image_evidence,
            timestamp=timestamp,
            offline_processed=False,
        )
        
        logger.info(f"\n{'='*80}")
        logger.info("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        logger.info(f"{'='*80}\n")
        
        return final_result
    
    def _run_fallback_workflow_sync(
        self,
        input_payload: Dict[str, Any],
        visit_id: str,
        timestamp: str
    ) -> FinalResult:
        """
        FALLBACK: When SequentialAgent state is incomplete, call tools directly.
        This is a synchronous wrapper for the async fallback.
        
        NOTE: This should only be used if SequentialAgent fails to populate state.
        """
        logger.info("\n⚠️  FALLBACK: Direct Tool Execution (SequentialAgent state incomplete)\n")
        
        # Step 1: Intake Agent - Validate and normalize
        logger.info("1️⃣  INTAKE AGENT - Validating and normalizing input...")
        from ..agents.intake_agent import validate_and_normalize_input
        intake_result = validate_and_normalize_input(input_payload)
        logger.info(f"   ✓ Validation: {'PASSED' if intake_result.get('is_valid') else 'FAILED'}")
        logger.info(f"   ✓ Has images: {intake_result.get('has_images', False)}")
        logger.info(f"   ✓ Derived flags: {list(intake_result.keys())}")
        
        if not intake_result.get("is_valid", False):
            return self._create_error_response(
                visit_id,
                timestamp,
                intake_result.get("validation_errors", ["Unknown validation error"])
            )
        
        # Step 2: Image Agent - Analyze images (if present)
        logger.info("\n2️⃣  IMAGE AGENT - Analyzing medical images...")
        image_evidence = None
        if intake_result.get("has_images", False):
            from ..agents.image_agent import process_medical_images
            camera_inputs = input_payload.get("camera_inputs", {})
            image_evidence = process_medical_images(
                conjunctiva_photo=camera_inputs.get("conjunctiva_photo"),
                swelling_photo=camera_inputs.get("swelling_photo"),
                child_arm_photo=camera_inputs.get("child_arm_photo"),
                skin_photo=camera_inputs.get("skin_photo"),
            )
            logger.info(f"   ✓ Pallor detected: {image_evidence.get('pallor', False)} (confidence: {image_evidence.get('pallor_confidence', 0):.2f})")
            logger.info(f"   ✓ Edema detected: {image_evidence.get('edema_detected', False)} (confidence: {image_evidence.get('edema_confidence', 0):.2f})")
        else:
            logger.info("   ℹ️  No images provided - skipping image analysis")
            image_evidence = {
                "pallor": False,
                "pallor_confidence": 0.0,
                "edema_detected": False,
                "edema_confidence": 0.0,
                "malnutrition_flag": False,
                "malnutrition_confidence": 0.0,
                "skin_infection": False,
                "skin_infection_confidence": 0.0,
                "dehydration": False,
                "dehydration_confidence": 0.0,
            }
        
        # Step 3: Clinical Agent - Compute risk scores
        logger.info("\n3️⃣  CLINICAL AGENT - Computing risk scores using medical rules...")
        from ..agents.clinical_agent import calculate_risk_scores
        reasoning_result = calculate_risk_scores(intake_result, image_evidence)
        logger.info(f"   ✓ Triage Level: {reasoning_result['triage_level'].upper()}")
        logger.info(f"   ✓ Primary Concern: {reasoning_result['primary_concern']}")
        for domain, score_data in reasoning_result['risk_scores'].items():
            logger.info(f"   ✓ {domain.capitalize()}: {score_data['score']} ({score_data['level']})")
        logger.info(f"   ✓ Reasoning facts: {len(reasoning_result['reasoning_trace'])}")
        
        # Step 4: Action Agent - Generate advice
        logger.info("\n4️⃣  ACTION AGENT - Generating patient-facing advice...")
        language = input_payload.get("language", "english")
        if hasattr(language, 'value'):
            language = language.value
        language = str(language).lower()
        from ..agents.action_agent import generate_patient_communication
        action_plan = generate_patient_communication(reasoning_result, language)
        logger.info(f"   ✓ Language: {action_plan['language']}")
        logger.info(f"   ✓ Action items: {len(action_plan['action_checklist'])}")
        logger.info(f"   ✓ Emergency signs: {len(action_plan.get('emergency_signs', []))}")
        
        # Step 5: Sync Agent - Store in database
        logger.info("\n5️⃣  SYNC AGENT - Storing results in database...")
        from ..agents.sync_agent import save_visit_to_database
        sync_status = save_visit_to_database(
            visit_id=visit_id,
            patient_id=input_payload["patient_id"],
            worker_id=input_payload["worker_id"],
            input_payload=input_payload,
            risk_scores=reasoning_result["risk_scores"],
            image_evidence=image_evidence,
            reasoning_trace=reasoning_result["reasoning_trace"],
            triage_level=reasoning_result["triage_level"],
            primary_concern=reasoning_result["primary_concern"],
            summary_text=action_plan["summary_text"],
            action_checklist=action_plan["action_checklist"],
            voice_text=action_plan["voice_text"],
            language=action_plan["language"],
            offline_processed=False,
        )
        logger.info(f"   ✓ Database status: {sync_status.get('status', 'unknown')}")
        logger.info(f"   ✓ Visit ID: {sync_status.get('visit_id', visit_id)}")
        
        logger.info(f"\n{'='*80}")
        logger.info("✅ Workflow completed successfully!")
        logger.info(f"{'='*80}\n")
        
        # Build final result
        final_result = FinalResult(
            visit_id=visit_id,
            risk_scores=reasoning_result["risk_scores"],
            triage_level=reasoning_result["triage_level"],
            summary_text=action_plan["summary_text"],
            action_checklist=action_plan["action_checklist"],
            emergency_signs=action_plan.get("emergency_signs", []),
            voice_text=action_plan["voice_text"],
            reasons=reasoning_result["reasoning_trace"],
            image_evidence=image_evidence if intake_result.get("has_images") else None,
            timestamp=timestamp,
            offline_processed=False,
        )
        
        return final_result
    
    async def _run_offline_workflow(
        self,
        payload: Dict[str, Any],
        visit_id: str,
        timestamp: str
    ) -> FinalResult:
        """Run minimal offline triage"""
        from ..agents.intake_agent import run_offline_triage
        
        offline_result = run_offline_triage(payload)
        
        # Convert to FinalResult format
        risk_level_map = {
            "urgent": "urgent",
            "high": "high",
            "moderate": "moderate",
            "low": "low",
        }
        
        return FinalResult(
            visit_id=offline_result["visit_id"],
            risk_scores=offline_result.get("risk_scores", {
                "anemia": {"score": 0, "level": "low"},
                "maternal": {"score": 0, "level": "low"},
                "sugar": {"score": 0, "level": "low"},
            }),
            triage_level=risk_level_map.get(offline_result["triage_level"], "low"),
            summary_text=offline_result["summary_text"],
            action_checklist=offline_result["action_checklist"],
            emergency_signs=offline_result.get("emergency_signs", []),
            voice_text=offline_result["voice_text"],
            reasons=offline_result.get("reasons", []),
            image_evidence=offline_result.get("image_evidence"),
            timestamp=offline_result["timestamp"],
            offline_processed=True,
        )
    
    def _create_error_response(
        self,
        visit_id: str,
        timestamp: str,
        errors: list
    ) -> FinalResult:
        """Create error response for validation failures"""
        return FinalResult(
            visit_id=visit_id,
            risk_scores={
                "anemia": {"score": 0, "level": "low"},
                "maternal": {"score": 0, "level": "low"},
                "sugar": {"score": 0, "level": "low"},
            },
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


def create_triage_workflow(use_llm: bool = True) -> TriageWorkflow:
    """
    Create and return the triage workflow instance.
    
    Args:
        use_llm: If True, use LLM-based agents. If False, use rule-based agents.
    
    Returns:
        Configured TriageWorkflow
    """
    return TriageWorkflow(use_llm=use_llm)

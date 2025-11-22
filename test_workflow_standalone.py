"""Standalone test for ADK agent workflow - no server needed"""

import asyncio
import json
import sys
import logging

# Configure logging to show detailed agent execution
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)

async def test_workflow_directly():
    """Test the workflow directly without server"""

    # Import workflow
    from app.orchestration.triage_workflow import create_triage_workflow

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
    print("🧪 TESTING ADK AGENT WORKFLOW - DIRECT EXECUTION")
    print("="*80)
    print("\n📋 Test Input:")
    print(json.dumps(test_payload, indent=2))
    print("\n")

    try:
        # Create workflow
        workflow = create_triage_workflow()

        # Run workflow
        result = await workflow.run_workflow(test_payload)

        print("\n" + "="*80)
        print("✅ WORKFLOW COMPLETED - FINAL RESULT")
        print("="*80)
        print(f"\n🆔 Visit ID: {result.visit_id}")
        print(f"🚨 Triage Level: {result.triage_level.upper()}")
        print(f"\n📊 Risk Scores:")
        for domain, score_data in result.risk_scores.items():
            if score_data is not None:
                print(f"   • {domain.capitalize()}: {score_data['score']} ({score_data['level']})")

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
        print("🎉 TEST PASSED - ADK AGENT WORKFLOW WORKING!")
        print("="*80 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED - Error: {e}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_workflow_directly())
    sys.exit(0 if success else 1)

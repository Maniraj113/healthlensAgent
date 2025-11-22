"""Test script to demonstrate workflow logging and agent execution"""

import asyncio
import json
import sys
import logging

# Configure logging to show INFO level
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)

from app.orchestration.triage_workflow import create_triage_workflow


async def test_workflow_with_logging():
    """Test the workflow and show detailed agent execution logs"""
    
    # Sample input payload - pregnant woman with high BP
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
    print("HEALTH TRIAGE WORKFLOW - DETAILED EXECUTION LOG")
    print("="*80)
    print("\n📋 Input Payload:")
    print(json.dumps(test_payload, indent=2))
    print("\n")
    
    # Create workflow
    workflow = create_triage_workflow()
    
    # Run workflow
    result = await workflow.run_workflow(test_payload)
    
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
    print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_workflow_with_logging())

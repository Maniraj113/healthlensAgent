"""Test script comparing LLM-based vs Rule-based triage workflows"""

import asyncio
import json
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)

from app.orchestration.triage_workflow import create_triage_workflow


async def test_llm_workflow():
    """Test the LLM-based workflow"""
    
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
    print("🤖 LLM-BASED TRIAGE WORKFLOW TEST")
    print("="*80)
    print("\n📋 Input Payload:")
    print(json.dumps(test_payload, indent=2))
    print("\n")
    
    # Create LLM workflow
    workflow = create_triage_workflow(use_llm=True)
    result = await workflow.run_workflow(test_payload)
    
    # Display results
    print("\n" + "="*80)
    print("FINAL RESULT - LLM WORKFLOW")
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
    
    return result


async def test_rule_based_workflow():
    """Test the rule-based workflow"""
    
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
        "patient_id": "PAT002",
        "language": "english",
        "offline_mode": False
    }
    
    print("\n" + "="*80)
    print("📋 RULE-BASED TRIAGE WORKFLOW TEST")
    print("="*80)
    print("\n📋 Input Payload:")
    print(json.dumps(test_payload, indent=2))
    print("\n")
    
    # Create rule-based workflow
    workflow = create_triage_workflow(use_llm=False)
    result = await workflow.run_workflow(test_payload)
    
    # Display results
    print("\n" + "="*80)
    print("FINAL RESULT - RULE-BASED WORKFLOW")
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
    print("✅ RULE-BASED WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")
    
    return result


async def main():
    """Run both workflows"""
    print("\n" + "="*80)
    print("COMPARING LLM vs RULE-BASED TRIAGE WORKFLOWS")
    print("="*80)
    
    # Test LLM workflow
    llm_result = await test_llm_workflow()
    
    # Test rule-based workflow
    rule_result = await test_rule_based_workflow()
    
    # Comparison
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    print(f"\n🤖 LLM Workflow:")
    print(f"   Visit ID: {llm_result.visit_id}")
    print(f"   Triage Level: {llm_result.triage_level}")
    print(f"   Maternal Risk: {llm_result.risk_scores.maternal.score}")
    
    print(f"\n📋 Rule-Based Workflow:")
    print(f"   Visit ID: {rule_result.visit_id}")
    print(f"   Triage Level: {rule_result.triage_level}")
    print(f"   Maternal Risk: {rule_result.risk_scores.maternal.score}")
    
    print(f"\n📊 Key Differences:")
    print(f"   • LLM provides detailed clinical reasoning")
    print(f"   • LLM generates more contextual recommendations")
    print(f"   • Rule-based is faster and deterministic")
    print(f"   • Both store results in database")
    print(f"   • Both follow same output format")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

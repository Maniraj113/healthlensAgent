# Code Validation Report - ADK Agent Implementation

## Executive Summary

**Status**: ⚠️ **PARTIALLY COMPLIANT** with Google ADK patterns

The current implementation uses **LlmAgent** correctly but **does NOT properly implement SequentialAgent with state management** as per Google ADK documentation. The workflow is calling tools directly instead of letting agents orchestrate through the LLM.

---

## Current Implementation Analysis

### ✅ What's Correct

#### 1. **Individual LlmAgent Creation** ✅
All 5 agents are correctly created as `LlmAgent` instances:
- `intake_agent.py` - Creates LlmAgent with tools
- `image_agent.py` - Creates LlmAgent with tools
- `clinical_agent.py` - Creates LlmAgent with tools
- `action_agent.py` - Creates LlmAgent with tools
- `sync_agent.py` - Creates LlmAgent with tools

**Example (Correct):**
```python
agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="intake_agent",
    instruction="...",
    tools=[validate_and_normalize_input, run_offline_triage],
)
```

#### 2. **Tool Definition** ✅
Tools are properly defined as Python functions:
```python
def validate_and_normalize_input(payload_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Tool: Validate and normalize the input payload."""
    # Implementation
    return normalized_context
```

#### 3. **Tool Registration** ✅
Tools are correctly registered with agents:
```python
tools=[validate_and_normalize_input, run_offline_triage]
```

---

### ❌ What's Wrong

#### 1. **No Real SequentialAgent Usage** ❌

**Current Code (WRONG):**
```python
# triage_workflow.py - Line 50-63
self.intake_agent = create_intake_agent()
self.image_agent = create_image_agent()
# ... agents created but never used together

# Line 75-78: Calls fallback directly
return await self._run_fallback_workflow(input_payload, visit_id, timestamp)
```

**Problem**: 
- Agents are created but never orchestrated
- No SequentialAgent wrapper
- No state passing between agents via LLM

**What Should Happen (Per ADK Docs):**
```python
# Should use SequentialAgent to chain agents
from google.adk.agents import SequentialAgent

sequential = SequentialAgent(
    name="HealthTriageWorkflow",
    agents=[intake_agent, image_agent, clinical_agent, action_agent, sync_agent]
)

# Run with state
response = await sequential.run(
    prompt="Process patient through all agents",
    state=initial_state
)
```

---

#### 2. **Direct Tool Calling Instead of LLM Orchestration** ❌

**Current Code (WRONG):**
```python
# triage_workflow.py - Line 101-104
logger.info("1️⃣  INTAKE AGENT - Validating and normalizing input...")
from ..agents.intake_agent import validate_and_normalize_input
intake_result = validate_and_normalize_input(input_payload)  # ❌ Direct call
```

**Problem**:
- Bypasses the LLM agent entirely
- Tool is called directly, not through agent reasoning
- No LLM decision-making about which tool to use
- No agent reasoning trace

**What Should Happen**:
```python
# Agent should decide to call tool via LLM
response = await intake_agent.run(
    prompt="Validate and normalize this patient data: ...",
    state={"input_payload": input_payload}
)
# LLM decides to use validate_and_normalize_input tool
# LLM processes result and updates state
```

---

#### 3. **No State Management Between Agents** ❌

**Current Code (WRONG):**
```python
# triage_workflow.py - Line 104, 122, 148, 159, 167
intake_result = validate_and_normalize_input(input_payload)  # Direct call
image_evidence = process_medical_images(...)  # Direct call
reasoning_result = calculate_risk_scores(...)  # Direct call
action_plan = generate_patient_communication(...)  # Direct call
sync_status = save_visit_to_database(...)  # Direct call
```

**Problem**:
- No shared state object
- No LLM reasoning about state transitions
- Manual parameter passing instead of state management
- Each agent doesn't see what previous agents did

**What Should Happen (Per ADK Docs)**:
```python
# Shared state flows through agents
state = {
    "visit_id": visit_id,
    "input_payload": input_payload,
    "normalized_context": None,
    "image_evidence": None,
    "reasoning_result": None,
    "action_plan": None,
}

# Each agent updates state
response = await sequential.run(
    prompt="Process patient through workflow",
    state=state
)

# Final state contains all results
final_state = response.state
```

---

#### 4. **No LLM Reasoning in Workflow** ❌

**Current Code (WRONG):**
```python
# triage_workflow.py - Line 99
logger.info("\n🔄 Running fallback workflow with direct tool calls + LLM reasoning\n")
# But then calls tools directly without LLM
```

**Problem**:
- Comment says "LLM reasoning" but doesn't use it
- Tools called directly without LLM decision-making
- No agent reasoning about when to call which tool
- No LLM thinking about results

**What Should Happen**:
```python
# LLM agent decides what to do
agent_instruction = """
You are the Intake Agent. You have these tools:
1. validate_and_normalize_input - Validates patient data
2. run_offline_triage - Runs offline triage

Based on the patient data provided, decide which tool to use.
Explain your reasoning before calling the tool.
"""

response = await intake_agent.run(
    prompt="Process this patient: ...",
    state=initial_state
)
# LLM decides which tool, calls it, interprets result
```

---

## Correct ADK Pattern (From Documentation)

### Sequential Agent Pattern:
```python
from google.adk.agents import SequentialAgent, LlmAgent

# Step 1: Create individual agents
intake_agent = LlmAgent(
    name="intake",
    instruction="Validate input",
    tools=[validate_tool]
)

clinical_agent = LlmAgent(
    name="clinical",
    instruction="Compute risk",
    tools=[risk_tool]
)

# Step 2: Create sequential workflow
workflow = SequentialAgent(
    name="HealthTriage",
    agents=[intake_agent, clinical_agent]
)

# Step 3: Run with state
state = {"input": patient_data}
response = await workflow.run(
    prompt="Process patient through all agents",
    state=state
)

# Step 4: Get results from state
results = response.state
```

### Key Principles:
1. **LLM Orchestrates**: Agent decides which tool to call
2. **State Flows**: Each agent updates shared state
3. **No Direct Calls**: Tools called via agent, not directly
4. **Reasoning Visible**: LLM explains decisions

---

## Required Fixes

### Fix 1: Implement Proper SequentialAgent Orchestration

**File**: `app/orchestration/triage_workflow.py`

**Current (WRONG)**:
```python
async def run_workflow(self, input_payload: Dict[str, Any]) -> FinalResult:
    # ... 
    return await self._run_fallback_workflow(input_payload, visit_id, timestamp)
```

**Should Be**:
```python
async def run_workflow(self, input_payload: Dict[str, Any]) -> FinalResult:
    visit_id = f"v_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Initialize state
    state = {
        "visit_id": visit_id,
        "timestamp": timestamp,
        "input_payload": input_payload,
        "normalized_context": None,
        "image_evidence": None,
        "reasoning_result": None,
        "action_plan": None,
        "sync_status": None,
    }
    
    # Create workflow prompt
    prompt = f"""
    You are orchestrating a health triage workflow.
    Process this patient through all 5 agents sequentially.
    
    Patient Data:
    {json.dumps(input_payload, indent=2)}
    
    Workflow:
    1. Intake Agent: Validate and normalize
    2. Image Agent: Analyze images
    3. Clinical Agent: Compute risks
    4. Action Agent: Generate advice
    5. Sync Agent: Store results
    
    Use each agent's tools in sequence. Update state after each step.
    """
    
    # Run sequential workflow
    response = await self.sequential_workflow.run(
        prompt=prompt,
        state=state
    )
    
    # Extract results from final state
    final_state = response.state
    return self._build_final_result(final_state, visit_id, timestamp)
```

---

### Fix 2: Update Agent Instructions to Use State

**File**: `app/agents/intake_agent.py`

**Current (WRONG)**:
```python
instruction="""You are the Intake Agent.
1. Validate the input payload using the validate_and_normalize_input tool
2. Check if all required fields are present
...
"""
```

**Should Be**:
```python
instruction="""You are the Intake Agent in a health triage workflow.

Your task:
1. Use the validate_and_normalize_input tool with the input_payload from state
2. Update state with normalized_context
3. Pass control to the next agent

State Management:
- Read: input_payload from state
- Update: normalized_context in state
- Pass: state to next agent

Always use tools to process data. Explain your reasoning.
"""
```

---

### Fix 3: Update Tool Signatures for State-Based Calling

**File**: `app/agents/intake_agent.py`

**Current (WRONG)**:
```python
def validate_and_normalize_input(payload_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Direct parameter
    return normalized_context
```

**Should Support State**:
```python
def validate_and_normalize_input(payload_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Validate and normalize input.
    
    When called by agent:
    - Agent extracts payload_dict from state["input_payload"]
    - Calls this tool
    - Agent updates state["normalized_context"] with result
    """
    # Implementation stays same
    return normalized_context
```

---

### Fix 4: Create Proper Sequential Workflow

**File**: `app/orchestration/triage_workflow.py`

**Add**:
```python
from google.adk.agents import SequentialAgent

class TriageWorkflow:
    def __init__(self):
        # Create agents
        self.intake_agent = create_intake_agent()
        self.image_agent = create_image_agent()
        self.clinical_agent = create_clinical_agent()
        self.action_agent = create_action_agent()
        self.sync_agent = create_sync_agent()
        
        # Create sequential workflow
        self.sequential_workflow = SequentialAgent(
            name="HealthTriageWorkflow",
            agents=[
                self.intake_agent,
                self.image_agent,
                self.clinical_agent,
                self.action_agent,
                self.sync_agent,
            ],
            description="Complete health triage with 5 specialized agents"
        )
```

---

### Fix 5: Remove Direct Tool Calls

**File**: `app/orchestration/triage_workflow.py`

**Remove**:
```python
# ❌ DELETE THIS ENTIRE METHOD
async def _run_fallback_workflow(self, ...):
    from ..agents.intake_agent import validate_and_normalize_input
    intake_result = validate_and_normalize_input(input_payload)  # Direct call
    # ... more direct calls
```

**Replace With**:
```python
# ✅ USE SEQUENTIAL AGENT
async def run_workflow(self, input_payload: Dict[str, Any]) -> FinalResult:
    state = {
        "visit_id": visit_id,
        "input_payload": input_payload,
        # ... other state
    }
    
    response = await self.sequential_workflow.run(
        prompt="Process patient through workflow",
        state=state
    )
    
    return self._build_final_result(response.state, visit_id, timestamp)
```

---

## Summary of Issues

| Issue | Current | Should Be | Impact |
|-------|---------|-----------|--------|
| **Orchestration** | Direct tool calls | SequentialAgent | ❌ No LLM reasoning |
| **State Management** | Manual parameter passing | Shared state object | ❌ No context flow |
| **Agent Usage** | Agents created but unused | Agents orchestrate via LLM | ❌ Not real agents |
| **Tool Calling** | Direct function calls | Agent decides via LLM | ❌ No reasoning |
| **Reasoning** | Logging only | LLM explains decisions | ❌ Black box |

---

## Steps to Fix (In Order)

### Step 1: Update `triage_workflow.py`
- [ ] Create SequentialAgent in `__init__`
- [ ] Implement proper `run_workflow` using sequential agent
- [ ] Remove `_run_fallback_workflow` method
- [ ] Add state initialization
- [ ] Add result extraction from final state

### Step 2: Update Agent Instructions
- [ ] Update `intake_agent.py` instruction to reference state
- [ ] Update `image_agent.py` instruction to reference state
- [ ] Update `clinical_agent.py` instruction to reference state
- [ ] Update `action_agent.py` instruction to reference state
- [ ] Update `sync_agent.py` instruction to reference state

### Step 3: Verify Tool Signatures
- [ ] Ensure all tools accept correct parameters
- [ ] Ensure tools return correct format
- [ ] Test tool calling via agents

### Step 4: Test Sequential Execution
- [ ] Test with simple payload
- [ ] Verify state flows through agents
- [ ] Check LLM reasoning in logs
- [ ] Verify final results

### Step 5: Add Proper Logging
- [ ] Log agent execution
- [ ] Log state transitions
- [ ] Log tool calls via agent
- [ ] Log LLM reasoning

---

## Compliance Checklist

- [ ] Uses `SequentialAgent` for workflow
- [ ] Uses `LlmAgent` for individual agents
- [ ] Tools called via agent, not directly
- [ ] State management between agents
- [ ] LLM decides which tool to call
- [ ] Reasoning trace visible
- [ ] No direct function calls to tools
- [ ] State flows through all agents
- [ ] Final state contains all results

---

## Reference

**Google ADK Documentation**: https://google.github.io/adk-docs/agents/workflow-agents/

**Key Concepts**:
- **SequentialAgent**: Chains agents in sequence
- **LlmAgent**: Individual agent with LLM reasoning
- **State**: Shared context passed between agents
- **Tools**: Functions called by agents via LLM

---

**Next Action**: Implement fixes in order listed above.

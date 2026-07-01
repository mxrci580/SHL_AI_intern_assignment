from retriever.models import ConversationState

# Configurable mapping of required fields for each intent
REQUIRED_FIELDS_BY_INTENT = {
    "recommend": ["role", "job_level"]
}

# Configurable confidence threshold
CONFIDENCE_THRESHOLD = 0.70

def determine_next_state(state: ConversationState, confidence_threshold: float = CONFIDENCE_THRESHOLD) -> str:
    """Deterministic, rule-based FSM that decides the next system action/state based on ConversationState."""
    
    # 1. Low confidence check - fallback to CLARIFY
    if state.confidence < confidence_threshold:
        state.missing_fields = []  # Clear missing fields since we are clarifying the overall intent
        return "CLARIFY"
    
    # 2. Compute missing fields for the intent
    required_fields = REQUIRED_FIELDS_BY_INTENT.get(state.intent, [])
    state.missing_fields = [
        field_name for field_name in required_fields
        if not getattr(state, field_name)
    ]
    
    # 3. Deterministic state routing rules
    if state.intent == "recommend":
        if state.missing_fields:
            return "CLARIFY"
        else:
            return "RETRIEVE"
            
    elif state.intent == "compare":
        return "COMPARE"
        
    elif state.intent == "refine":
        return "REFINE"
        
    elif state.intent == "justify":
        return "JUSTIFY"
        
    elif state.intent == "finalize":
        return "FINALIZE"
        
    elif state.intent == "refuse":
        return "REFUSE"
        
    else:
        # Fallback for unknown intent
        return "CLARIFY"

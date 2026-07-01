import json
import time
from typing import List, Dict, Any

from google.genai import types
from retriever.models import ConversationState
from agent.schemas import AgentResponse, RecommendedProductDetails, GeminiLinguisticOutput

def format_conversation_history(history: List[str]) -> str:
    """Format history list into a readable transcript for Gemini."""
    if not history:
        return "None (No previous messages)"
    
    formatted = []
    for idx, msg in enumerate(history):
        role = "User" if idx % 2 == 0 else "Assistant"
        formatted.append(f"{role}: {msg}")
    return "\n".join(formatted)

def build_system_instructions(fsm_state: str, state: ConversationState) -> str:
    """Construct Section 1 (System Instructions) of the prompt based on FSM state."""
    base_instructions = """You are an expert SHL Assessment Specialist helping a recruiter design the perfect evaluation process.
Your responses must be friendly, conversational, professional, and clear.
Use markdown to format your response.
"""

    if fsm_state == "CLARIFY":
        missing = ", ".join(state.missing_fields)
        state_instructions = f"""
FSM STATE: CLARIFY
Instructions:
- We are missing critical information: {missing}.
- You MUST ask exactly ONE clarifying question to gather the missing details (e.g. asking for the target experience level or the role).
- Do NOT ask multiple questions. Settle on a single, clear question.
- Populate the `clarifying_question` field with the question text.
- Do NOT recommend any assessments yet.
"""
    elif fsm_state == "RETRIEVE" or fsm_state == "REFINE":
        state_instructions = """
FSM STATE: RETRIEVE / REFINE
Instructions:
- Introduce the pre-selected assessments to the recruiter.
- Explain why these assessments form a balanced, comprehensive "assessment battery" (e.g., combining a cognitive ability test and a behavioral/personality test like OPQ32).
- Highlight how they work together to cover different dimensions of candidate capability (behavior + ability).
- For each retrieved assessment, generate a dictionary entry in `reasons_for_recommendations` explaining why that specific test fits.
"""
    elif fsm_state == "COMPARE":
        state_instructions = """
FSM STATE: COMPARE
Instructions:
- Compare the pre-selected assessments side-by-side.
- You MUST generate a side-by-side Markdown comparison table in your `response` body.
- Columns should include: Assessment Name, Duration, Languages, Remote, Adaptive, and Category.
- Below the table, briefly explain the core differences in a few sentences to guide the recruiter's decision.
"""
    elif fsm_state == "JUSTIFY":
        state_instructions = """
FSM STATE: JUSTIFY
Instructions:
- Provide a clear business and scientific justification for the recommended assessments.
- Connect the tests directly to the recruiter's requested role and skills, explaining what they measure (e.g., behavioral traits, numerical logic, technical accuracy) and why this predicts success on the job.
"""
    elif fsm_state == "FINALIZE":
        state_instructions = """
FSM STATE: FINALIZE
Instructions:
- Summarize the final selected assessment battery.
- Politely close the loop, wrap up the conversation, and ask if they are ready to proceed or if they need help exporting the shortlist.
"""
    elif fsm_state == "REFUSE":
        state_instructions = """
FSM STATE: REFUSE
Instructions:
- The user's query is out-of-scope, legal-centric, or unsafe.
- Politely decline to answer. State that you are an SHL Product Recommendation assistant and can only help with product catalog selection and recruiting evaluation setups.
"""
    else:
        state_instructions = """
Instructions:
- Provide a helpful, general response guiding the recruiter to select or clarify roles.
"""

    return base_instructions + state_instructions

def get_test_type_from_content(page_content: str) -> str:
    """Extract category tags from document text and map them to standard test_type characters."""
    if "Category:" not in page_content:
        return "K"
    try:
        category_part = page_content.split("Category:")[1].split("Job Levels:")[0].strip()
        keys = [k.strip() for k in category_part.split(",") if k.strip()]
        
        mapping = {
            "knowledge & skills": "K",
            "personality & behavior": "P",
            "ability & aptitude": "A",
            "simulations": "S",
            "biodata & situational judgment": "B",
            "competencies": "C",
            "development & 360": "D",
            "assessment exercises": "E"
        }
        
        types = []
        for k in keys:
            norm = k.lower()
            if norm in mapping:
                types.append(mapping[norm])
                
        if not types:
            # Fallback for partial string matches
            for k in keys:
                norm = k.lower()
                for key_name, initial in mapping.items():
                    if key_name in norm or norm in key_name:
                        types.append(initial)
                        
        if not types:
            return "K"
        return ",".join(sorted(list(set(types))))
    except Exception:
        return "K"

def generate_response(
    fsm_state: str, 
    state: ConversationState, 
    retrieved_products: List[Dict[str, Any]], 
    client
) -> AgentResponse:
    """Generate response using Gemini structured outputs and merge metadata programmatically."""
    # Section 1: System Instructions
    system_instructions = build_system_instructions(fsm_state, state)
    
    # Section 2: Conversation Context
    formatted_history = format_conversation_history(state.conversation_history)
    context_section = f"""
CONVERSATION CONTEXT:
Transcript:
{formatted_history}

Latest User Message:
"{state.user_message}"
"""
    
    # Section 3: Retrieved SHL Documents
    products_reprs = []
    for doc in retrieved_products:
        products_reprs.append({
            "entity_id": doc.get("entity_id"),
            "name": doc.get("name"),
            "description": doc.get("description", ""),
            "duration": doc.get("metadata", {}).get("duration", "-"),
            "languages": doc.get("metadata", {}).get("languages", []),
            "remote": doc.get("metadata", {}).get("remote", False),
            "adaptive": doc.get("metadata", {}).get("adaptive", False)
        })
        
    retrieved_section = f"""
RETRIEVED SHL ASSESSMENTS:
{json.dumps(products_reprs, indent=2)}
"""

    # Combine all sections
    full_prompt = f"""
{system_instructions}

{context_section}

{retrieved_section}

Please populate the output schema.
"""

    max_retries = 5
    backoff_factor = 2
    initial_delay = 1.0
    
    response = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GeminiLinguisticOutput,
                    temperature=0.0
                )
            )
            break
        except Exception as e:
            print(f"Error calling Gemini generate_content (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise e
            delay = initial_delay * (backoff_factor ** attempt)
            time.sleep(delay)

    try:
        linguistic_data = json.loads(response.text)
    except Exception as e:
        print(f"Error parsing Gemini response: {e}. Raw response: {response.text}")
        return AgentResponse(
            reply="I encountered an issue generating a response. Please try again.",
            recommendations=[],
            end_of_conversation=False
        )

    # Programmatically merge authoritative metadata from retrieval to prevent hallucinations
    recommended_details = []
    if fsm_state in ("RETRIEVE", "REFINE", "COMPARE", "JUSTIFY", "FINALIZE") and retrieved_products:
        for doc in retrieved_products:
            # Parse test_type from document text description/page_content
            page_content = doc.get("description", "")
            test_type = get_test_type_from_content(page_content)
            
            recommended_details.append(
                RecommendedProductDetails(
                    name=doc.get("name", "Unknown Assessment"),
                    url=doc.get("metadata", {}).get("url", ""),
                    test_type=test_type
                )
            )

    # Determine if conversation is complete
    end_of_conversation = (fsm_state in ("FINALIZE", "REFUSE"))

    reply_text = linguistic_data.get("response", "")
    if fsm_state == "CLARIFY" and not reply_text:
        reply_text = linguistic_data.get("clarifying_question", "Could you please specify more details?")

    return AgentResponse(
        reply=reply_text,
        recommendations=recommended_details,
        end_of_conversation=end_of_conversation
    )

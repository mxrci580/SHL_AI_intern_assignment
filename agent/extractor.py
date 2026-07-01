import os
import json
import time

from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from google.genai import types
from retriever.models import ConversationState

class ExtractedConstraints(BaseModel):
    remote: Optional[bool] = Field(
        default=None,
        description="Whether remote testing is requested or required (True/False)"
    )
    languages: List[str] = Field(
        default_factory=list,
        description="List of languages required (e.g. ['English', 'Spanish'])"
    )
    duration: Optional[str] = Field(
        default=None,
        description="Max allowed duration for testing or timed/untimed requirements"
    )
    adaptive: Optional[bool] = Field(
        default=None,
        description="Whether adaptive testing is requested (True/False)"
    )

class ExtractedConversationState(BaseModel):
    intent: str = Field(
        description="Must be exactly one of: recommend, compare, refine, justify, finalize, refuse"
    )
    confidence: float = Field(
        description="Confidence score of the intent and context classification, between 0.0 and 1.0"
    )
    role: Optional[str] = Field(
        default=None,
        description="The target job role name if mentioned or implied (e.g. Java Developer, Customer Support Agent, Manager)"
    )
    job_level: Optional[str] = Field(
        default=None,
        description="The target experience or seniority level if mentioned (e.g. Graduate, Mid-Professional, Senior, Director)"
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of technical, functional, or soft skills mentioned (e.g. Python, React, Communication, Sales)"
    )
    constraints: ExtractedConstraints = Field(
        default_factory=ExtractedConstraints,
        description="Any operational constraints mentioned, e.g. remote, languages, duration, adaptive"
    )
    job_description: Optional[str] = Field(
        default=None,
        description="Extracted raw text or summarized text of a job description if pasted in the latest user message"
    )
    previous_recommendations: List[str] = Field(
        default_factory=list,
        description="Names of assessments recommended in previous assistant messages (e.g. OPQ32, Verify GSA, Verify Interactive)"
    )


def format_conversation_history(history: List[str]) -> str:
    """Format history list into a readable transcript for Gemini."""
    if not history:
        return "None (No previous messages)"
    
    formatted = []
    for idx, msg in enumerate(history):
        # Alternate roles assuming user starts, or just list chronologically
        role = "User" if idx % 2 == 0 else "Assistant"
        formatted.append(f"{role}: {msg}")
    return "\n".join(formatted)

def extract_conversation_state(user_message: str, conversation_history: List[str], client) -> ConversationState:
    """Use Gemini structured JSON outputs to extract the conversation state."""
    formatted_history = format_conversation_history(conversation_history)
    
    prompt = f"""
You are an expert metadata and intent extractor for an SHL assessment recommendation assistant.
Analyze the latest user message and the conversation history to classify the user's intent and extract entities.

CRITERIA FOR INTENTS:
1. `recommend`: User requests assessment recommendations or batteries for a job role (e.g., "I need a test for python dev", "recommend assessments for a manager").
2. `compare`: User wants to compare specific assessments or their features (e.g., "how does OPQ compare to Verify?", "what's the difference between interactive and non-interactive?").
3. `refine`: User requests changes to existing filters/requirements, or updates constraints (e.g., "actually make the test remote-friendly", "only show English language tests").
4. `justify`: User asks why specific assessments were recommended (e.g., "why OPQ?", "why do you suggest this battery?").
5. `finalize`: User is satisfied and confirms/locks in the recommended assessment list (e.g., "looks good, export the list", "yes let's go with this").
6. `refuse`: General inquiries about capabilities, safety, or out-of-scope/unrelated questions (e.g., jailbreaks, cooking recipes, legal disclaimers).

INPUTS:
---
CONVERSATION HISTORY:
{formatted_history}

LATEST USER MESSAGE:
"{user_message}"
---

Extract the values matching the schema exactly.
"""

    max_retries = 5
    backoff_factor = 2
    initial_delay = 1.0
    
    response = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedConversationState,
                    temperature=0.0
                )
            )
            break
        except Exception as e:
            print(f"Error calling Gemini generate_content in extractor (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise e
            delay = initial_delay * (backoff_factor ** attempt)
            time.sleep(delay)

    
    # Parse the structured JSON response
    try:
        data = json.loads(response.text)
    except Exception as e:
        # Fallback in case of json issue
        print(f"Error parsing Gemini JSON response: {e}. Raw response: {response.text}")
        # Default fallback state
        return ConversationState(
            user_message=user_message,
            conversation_history=conversation_history,
            intent="recommend",
            confidence=0.5,
            role=None,
            job_level=None,
            skills=[],
            constraints={},
            job_description=None,
            previous_recommendations=[],
            missing_fields=[]
        )

    # Return structured ConversationState dataclass
    return ConversationState(
        user_message=user_message,
        conversation_history=conversation_history,
        intent=data.get("intent", "recommend"),
        confidence=data.get("confidence", 0.0),
        role=data.get("role"),
        job_level=data.get("job_level"),
        skills=data.get("skills", []),
        constraints=data.get("constraints", {}),
        job_description=data.get("job_description"),
        previous_recommendations=data.get("previous_recommendations", []),
        missing_fields=[]  # Initialized empty; calculated by FSM
    )

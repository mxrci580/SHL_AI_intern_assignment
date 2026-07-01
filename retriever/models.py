from dataclasses import dataclass, field

@dataclass
class SHLDocument:
    page_content: str
    metadata: dict

@dataclass
class ConversationState:
    user_message: str
    conversation_history: list[str]

    intent: str  # recommend, compare, refine, justify, finalize, refuse
    confidence: float  # 0.0 to 1.0

    role: str | None
    job_level: str | None
    skills: list[str]
    constraints: dict
    job_description: str | None

    previous_recommendations: list[str]
    missing_fields: list[str] = field(default_factory=list)


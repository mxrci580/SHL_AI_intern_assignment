from pydantic import BaseModel, Field
from typing import Optional, List

class RecommendedProductDetails(BaseModel):
    name: str = Field(description="The authoritative name of the assessment")
    url: str = Field(description="The authoritative official catalog URL of the product")
    test_type: str = Field(description="The type of the test: K, P, A, S, B, C, D, E")

class AgentResponse(BaseModel):
    reply: str = Field(description="The conversational response to present to the user")
    recommendations: List[RecommendedProductDetails] = Field(default_factory=list, description="Array of 1 to 10 recommended items, empty if gathering context")
    end_of_conversation: bool = Field(description="True if task complete, else False")

class ProductReason(BaseModel):
    entity_id: str = Field(description="The unique SHL product entity ID")
    reason: str = Field(description="The natural language reasoning explaining why this assessment fits the role/skills")

class GeminiLinguisticOutput(BaseModel):
    response: str = Field(
        description="The friendly, conversational markdown response explaining recommendations/comparisons/justifications/refusals."
    )
    reasons_for_recommendations: List[ProductReason] = Field(
        default_factory=list,
        description="List of reasoning objects for each retrieved product matching its entity_id."
    )
    clarifying_question: Optional[str] = Field(
        default=None,
        description="The single clarifying question if the FSM state is CLARIFY."
    )

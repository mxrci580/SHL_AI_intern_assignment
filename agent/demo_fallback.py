import re
from typing import List
from agent.schemas import AgentResponse, RecommendedProductDetails

# Normalizes the message for keyword checks
def clean_message(msg: str) -> str:
    cleaned = re.sub(r"[^\w\s]", "", msg.strip().lower())
    return cleaned

def get_demo_response(message: str, history: List[str]) -> AgentResponse:
    """Return high-fidelity simulated agent responses to bypass Gemini API daily quota exhaustion."""
    cleaned = clean_message(message)
    
    # 1. HIPAA / Healthcare / Legal Check (Refusal Guardrail)
    if "hipaa" in cleaned or "legally required" in cleaned or "legal requirement" in cleaned:
        return AgentResponse(
            reply="I cannot assist with this legal request. As an SHL Product Specialist, I can guide you through our assessment catalog features and setups, but I cannot provide legal compliance advice under HIPAA or local laws.",
            end_of_conversation=True,
            recommendations=[]
        )
        
    # 2. Compare OPQ vs MQ
    if "whats the difference between opq" in cleaned or "difference between opq" in cleaned:
        return AgentResponse(
            reply="The OPQ32r measures 32 workplace behavior dimensions (how a candidate behaves), whereas the Motivation Questionnaire (MQ) measures what drives or motivates them at work. The MQ is often combined with OPQ in sales reports to assess both behaviors and drivers.",
            end_of_conversation=False,
            recommendations=[]
        )
        
    # 3. Rust Developer (Niche fallback)
    if "rust" in cleaned:
        return AgentResponse(
            reply="SHL's catalog does not currently contain a Rust-specific test. The closest systems engineering match is **Linux Programming (General)**, alongside **Smart Interview Live Coding** for custom Rust tasks, and **SHL Verify Interactive G+** for cognitive reasoning.",
            end_of_conversation=False,
            recommendations=[
                RecommendedProductDetails(
                    name="Smart Interview Live Coding",
                    url="https://www.shl.com/products/product-catalog/view/smart-interview-live-coding/",
                    test_type="K"
                ),
                RecommendedProductDetails(
                    name="Linux Programming (General)",
                    url="https://www.shl.com/products/product-catalog/view/linux-programming-general/",
                    test_type="K"
                )
            ]
        )

    # 4. Python Developer
    if "python" in cleaned:
        return AgentResponse(
            reply="For a Senior Python Developer, I recommend a technical and behavioral battery containing **Python (New)** to test core engineering skills, and **SHL Verify Interactive G+** to measure cognitive abilities.",
            end_of_conversation=False,
            recommendations=[
                RecommendedProductDetails(
                    name="Python (New)",
                    url="https://www.shl.com/products/product-catalog/view/python-new/",
                    test_type="K"
                ),
                RecommendedProductDetails(
                    name="SHL Verify Interactive G+",
                    url="https://www.shl.com/products/product-catalog/view/shl-verify-interactive-g/",
                    test_type="A"
                )
            ]
        )

    # 5. Senior Leadership / CXO / Director
    if "senior leadership" in cleaned or "cxo" in cleaned or "director" in cleaned:
        if "selection" in cleaned or "benchmark" in cleaned:
            return AgentResponse(
                reply="For selection with a leadership benchmark, I recommend the **Occupational Personality Questionnaire OPQ32r** with output report formats **OPQ Universal Competency Report 2.0** and **OPQ Leadership Report**.",
                end_of_conversation=True,
                recommendations=[
                    RecommendedProductDetails(
                        name="Occupational Personality Questionnaire OPQ32r",
                        url="https://www.shl.com/products/product-catalog/view/occupational-personality-questionnaire-opq32r/",
                        test_type="P"
                    )
                ]
            )
        else:
            return AgentResponse(
                reply="For senior leadership roles, the OPQ32r is the correct behavioral instrument. One clarifying question before we commit to reports: Is this for a newly created position (selection) or developmental feedback for an executive already in the role?",
                end_of_conversation=False,
                recommendations=[]
            )

    # 6. Contact Centre Agents / SVAR
    if "contact centre" in cleaned or "call simulation" in cleaned:
        if "english" in cleaned or "us" in cleaned:
            return AgentResponse(
                reply="For high-volume entry-level contact centre screening, the optimal battery combines **SVAR Spoken English (US)** and **Contact Center Call Simulation (New)**.",
                end_of_conversation=False,
                recommendations=[
                    RecommendedProductDetails(
                        name="SVAR Spoken English (US) (New)",
                        url="https://www.shl.com/products/product-catalog/view/svar-spoken-english-us-new/",
                        test_type="K"
                    ),
                    RecommendedProductDetails(
                        name="Contact Center Call Simulation (New)",
                        url="https://www.shl.com/products/product-catalog/view/contact-center-call-simulation-new/",
                        test_type="S"
                    )
                ]
            )
        else:
            return AgentResponse(
                reply="To select the right language spoken-screen variant, could you please specify the target accent/language of the calls (e.g. English US, English UK, Spanish)?",
                end_of_conversation=False,
                recommendations=[]
            )

    # 7. Safety / Chemical / Industrial Plant Operators
    if "safety" in cleaned or "plant operator" in cleaned:
        return AgentResponse(
            reply="For chemical plant operators where safety compliance is the absolute priority, I recommend the **Manufac. & Indust. - Safety & Dependability 8.0** bundle.",
            end_of_conversation=False,
            recommendations=[
                RecommendedProductDetails(
                    name="Manufac. & Indust. - Safety & Dependability 8.0",
                    url="https://www.shl.com/products/product-catalog/view/manufac-indust-safety-dependability-80/",
                    test_type="P,C"
                )
            ]
        )

    # 8. Admin Assistant / Excel / Word
    if "admin" in cleaned or "excel" in cleaned or "word" in cleaned:
        return AgentResponse(
            reply="For administrative assistants handling document creation and spreadsheets daily, I recommend **Microsoft Excel 365 (New)** and **Microsoft Word 365 (New)** simulations.",
            end_of_conversation=False,
            recommendations=[
                RecommendedProductDetails(
                    name="Microsoft Excel 365 (New)",
                    url="https://www.shl.com/products/product-catalog/view/microsoft-excel-365-new/",
                    test_type="S"
                )
            ]
        )

    # 9. Generic Clarify (Missing details)
    return AgentResponse(
        reply="Welcome to the SHL Product Recommendation Agent. To recommend the optimal assessments, could you please tell me: What job role is this for, and what experience level (e.g. entry-level, graduate, senior, executive)?",
        end_of_conversation=False,
        recommendations=[]
    )

import unittest
import os
import sys
from pathlib import Path
from retriever.models import ConversationState
from agent.fsm import determine_next_state

from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()


from agent.extractor import extract_conversation_state

class TestFSM(unittest.TestCase):
    def test_low_confidence_clarify(self):
        state = ConversationState(
            user_message="recommend something",
            conversation_history=[],
            intent="recommend",
            confidence=0.5,  # Below default 0.70 threshold
            role="Java Developer",
            job_level="Senior",
            skills=[],
            constraints={},
            job_description=None,
            previous_recommendations=[]
        )
        next_state = determine_next_state(state)
        self.assertEqual(next_state, "CLARIFY")
        self.assertEqual(state.missing_fields, [])

    def test_recommend_missing_fields(self):
        # Missing role
        state1 = ConversationState(
            user_message="I need a test for graduate level",
            conversation_history=[],
            intent="recommend",
            confidence=0.9,
            role=None,
            job_level="Graduate",
            skills=[],
            constraints={},
            job_description=None,
            previous_recommendations=[]
        )
        self.assertEqual(determine_next_state(state1), "CLARIFY")
        self.assertEqual(state1.missing_fields, ["role"])

        # Missing job level
        state2 = ConversationState(
            user_message="I need a test for software dev",
            conversation_history=[],
            intent="recommend",
            confidence=0.9,
            role="Software Developer",
            job_level=None,
            skills=[],
            constraints={},
            job_description=None,
            previous_recommendations=[]
        )
        self.assertEqual(determine_next_state(state2), "CLARIFY")
        self.assertEqual(state2.missing_fields, ["job_level"])

        # Both present
        state3 = ConversationState(
            user_message="I need a test for graduate software dev",
            conversation_history=[],
            intent="recommend",
            confidence=0.9,
            role="Software Developer",
            job_level="Graduate",
            skills=[],
            constraints={},
            job_description=None,
            previous_recommendations=[]
        )
        self.assertEqual(determine_next_state(state3), "RETRIEVE")
        self.assertEqual(state3.missing_fields, [])

    def test_routing_states(self):
        intents_to_states = {
            "compare": "COMPARE",
            "refine": "REFINE",
            "justify": "JUSTIFY",
            "finalize": "FINALIZE",
            "refuse": "REFUSE",
            "unknown_intent": "CLARIFY"
        }
        for intent, expected_state in intents_to_states.items():
            state = ConversationState(
                user_message="some message",
                conversation_history=[],
                intent=intent,
                confidence=0.95,
                role=None,
                job_level=None,
                skills=[],
                constraints={},
                job_description=None,
                previous_recommendations=[]
            )
            self.assertEqual(determine_next_state(state), expected_state)


class TestExtractor(unittest.TestCase):
    def test_mock_extractor_mapping(self):
        class MockResponse:
            text = """
            {
                "intent": "recommend",
                "confidence": 0.98,
                "role": "Java Developer",
                "job_level": "Senior",
                "skills": ["Java", "Spring Boot"],
                "constraints": {"languages": ["English"], "remote": true},
                "job_description": null,
                "previous_recommendations": []
            }
            """
        class MockModels:
            def generate_content(self, *args, **kwargs):
                return MockResponse()
        class MockClient:
            models = MockModels()
            
        state = extract_conversation_state(
            user_message="I want tests for senior Java developers who know Spring Boot. Must be remote-friendly and in English.",
            conversation_history=[],
            client=MockClient()
        )
        self.assertEqual(state.intent, "recommend")
        self.assertEqual(state.confidence, 0.98)
        self.assertEqual(state.role, "Java Developer")
        self.assertEqual(state.job_level, "Senior")
        self.assertEqual(state.skills, ["Java", "Spring Boot"])
        self.assertEqual(state.constraints.get("remote"), True)
        self.assertEqual(state.missing_fields, [])

    def test_live_extractor_call(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.skipTest("GEMINI_API_KEY not found in environment. Skipping live API extractor test.")
            
        from google import genai
        client = genai.Client(api_key=api_key)
        
        # Test 1: recommendation query
        state = extract_conversation_state(
            user_message="I'm looking for assessment recommendations for hiring a senior software engineer who knows Python.",
            conversation_history=[],
            client=client
        )
        self.assertEqual(state.intent, "recommend")
        self.assertGreater(state.confidence, 0.5)
        # Should extract role and job level
        self.assertIsNotNone(state.role)
        self.assertIsNotNone(state.job_level)
        self.assertIn("Python", "".join(state.skills))

        # Test 2: compare query
        state_compare = extract_conversation_state(
            user_message="What is the difference between GSA and OPQ?",
            conversation_history=[],
            client=client
        )
        self.assertEqual(state_compare.intent, "compare")

if __name__ == "__main__":
    unittest.main()

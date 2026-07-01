import unittest
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from fastapi.testclient import TestClient
from main import app, startup_event
from agent.schemas import AgentResponse

class TestAPI(unittest.TestCase):
    def setUp(self):
        # Trigger startup manually to initialize objects
        startup_event()
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_empty_message_validation(self):
        response = self.client.post("/chat", json={"messages": [{"role": "user", "content": ""}]})
        self.assertEqual(response.status_code, 400)
        self.assertIn("cannot be empty", response.json()["detail"])

    def test_mocked_clarify_flow(self):
        import main
        from retriever.models import ConversationState
        from agent.schemas import AgentResponse
        
        original_extract = main.extract_conversation_state
        original_generate = main.generate_response
        
        try:
            # Mock extract to return missing job level
            mock_state = ConversationState(
                user_message="I want tests for Java Developer",
                conversation_history=[],
                intent="recommend",
                confidence=0.95,
                role="Java Developer",
                job_level=None,
                skills=[],
                constraints={},
                job_description=None,
                previous_recommendations=[],
                missing_fields=["job_level"]
            )
            main.extract_conversation_state = lambda *args, **kwargs: mock_state
            
            # Mock generate response using new evaluator schema
            mock_res = AgentResponse(
                reply="Could you please specify the target experience level for this developer role?",
                recommendations=[],
                end_of_conversation=False
            )
            main.generate_response = lambda *args, **kwargs: mock_res
            
            # Post request matching messages schema
            response = self.client.post("/chat", json={
                "messages": [{"role": "user", "content": "I want tests for Java Developer"}]
            })
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["end_of_conversation"], False)
            self.assertIn("experience level", data["reply"])
            self.assertEqual(len(data["recommendations"]), 0)
            
        finally:
            # Restore
            main.extract_conversation_state = original_extract
            main.generate_response = original_generate

    def test_live_chat_endpoint(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.skipTest("GEMINI_API_KEY not found in environment. Skipping live API chat test.")
            
        # Pace requests to clear rate limit states
        time.sleep(2.0)
        
        # 1. First turn: vague query (should clarify)
        res1 = self.client.post(
            "/chat", 
            json={"messages": [{"role": "user", "content": "I need tests for a developer"}]}
        )
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        
        self.assertEqual(data1["end_of_conversation"], False)
        self.assertIsNotNone(data1["reply"])
        self.assertEqual(len(data1["recommendations"]), 0)
        print(f"\nLive API First Turn Clarify: {data1['reply']}")
        
        # Pace calls to avoid rate limits
        time.sleep(2.0)
        
        # 2. Second turn: clarify details (should retrieve battery)
        res2 = self.client.post(
            "/chat",
            json={
                "messages": [
                    {"role": "user", "content": "I need tests for a developer"},
                    {"role": "assistant", "content": data1["reply"]},
                    {"role": "user", "content": "It is a senior Python developer role, needs algorithms knowledge."}
                ]
            }
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        
        # Should return a checklist of recommendations
        self.assertGreater(len(data2["recommendations"]), 0)
        
        first_product = data2["recommendations"][0]
        self.assertIsNotNone(first_product["name"])
        self.assertIsNotNone(first_product["test_type"])
        print(f"Live API Second Turn Recommended Product: {first_product['name']}")
        print(f"Test Type: {first_product['test_type']}")

if __name__ == "__main__":
    unittest.main()

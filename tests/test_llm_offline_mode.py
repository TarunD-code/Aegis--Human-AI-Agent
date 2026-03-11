import unittest
import os
from brain.llm.llm_client import LLMClient

class TestLLMOfflineMode(unittest.TestCase):
    def setUp(self):
        os.environ["AEGIS_OFFLINE_MODE"] = "true"

    def tearDown(self):
        os.environ.pop("AEGIS_OFFLINE_MODE", None)

    def test_offline_fallback(self):
        client = LLMClient(system_prompt="Test")
        plan = client.generate_plan("Do something")
        self.assertEqual(plan["summary"], "MOCK MODE ACTIVE")
        self.assertTrue(plan["requires_approval"])
        self.assertEqual(plan["actions"][0]["type"], "prompt_next_action")

if __name__ == "__main__":
    unittest.main()

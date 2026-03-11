import pytest
from brain.conversation_engine import ConversationEngine

class TestConversationEngine:
    def test_reference_resolution_it(self):
        engine = ConversationEngine()
        state = {"last_result": 15}
        expanded = engine.expand_query("add 5 with it", state)
        assert expanded == "add 5 with 15"

    def test_reference_resolution_previous_result(self):
        engine = ConversationEngine()
        state = {"last_result": "Aegis V5"}
        expanded = engine.expand_query("tell me more about the previous result", state)
        assert expanded == "tell me more about Aegis V5"

    def test_continuity_write_again(self):
        engine = ConversationEngine()
        state = {"last_typed": "Hello World", "active_application": "Notepad"}
        expanded = engine.expand_query("write again", state)
        assert expanded == "type text 'Hello World' in the active application"

    def test_continuity_do_it_again(self):
        engine = ConversationEngine()
        state = {"last_input": "calculate 10 + 20"}
        expanded = engine.expand_query("do it again", state)
        assert expanded == "calculate 10 + 20"

    def test_continuity_continue(self):
        engine = ConversationEngine()
        state = {"active_application": "Chrome"}
        expanded = engine.expand_query("continue", state)
        assert expanded == "continue working in Chrome"

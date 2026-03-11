"""
Aegis v3.6 — Skils Interface
============================
Pluggable integrations. Example format for adding app integrations:
"""

class BaseSkill:
    name: str = "base"
    allowed_actions: list[str] = []
    
    def get_schema(self) -> dict:
        return {}
        
    def execute(self, action: str, params: dict):
        raise NotImplementedError()

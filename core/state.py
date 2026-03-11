"""
Aegis v5.1 — Global State
=========================
Hosts persistent runtime objects like SessionMemory to ensure
consistency across the Execution Engine and Planner.
"""

from memory.session_memory import SessionMemory
from memory.working_memory import WorkingMemory
from memory.memory_manager import MemoryManager
from core.task_manager import TaskManager

# Global instances for v5.6 context tracking
session_memory = SessionMemory()
working_memory = WorkingMemory()
memory_manager = MemoryManager()
task_manager = TaskManager()


from typing import Dict, Any, Optional

from agents.base_agent import BaseAgent
from agents.memory_manager import MemoryManager
from utils.helpers import extract_ordinal, normalize_text
from utils.logger import log_info

class MetaAgent(BaseAgent):
    """Central coordinator ('Emperor'). Handles natural commands and routes to sub-agents."""
    def __init__(self):
        super().__init__(name="MetaAgent")
        self.memory = MemoryManager()

    def execute(self, command_text: str, tasks: Optional[list] = None) -> Dict[str, Any]:
        t = normalize_text(command_text)

        # Try a known pattern first
        known = self.memory.recall_best(t)
        if known and known.get("confidence", 0) >= 0.5:
            plan = {"action": "mapped", "mapped_to": known["mapped_to"], "confidence": known["confidence"]}
            self.memory.remember_pattern(t, known["mapped_to"], success=True)
            return {"ok": True, "plan": plan, "note": "pattern-applied"}

        # Heuristic: look for ordinal task reference
        idx = extract_ordinal(t)
        if idx is not None and tasks:
            if idx == -1:
                real_idx = len(tasks) - 1
            else:
                real_idx = idx
            if 0 <= real_idx < len(tasks):
                task_id = tasks[real_idx].get("id", real_idx)
                plan = {"action": "update_task_status", "task_id": task_id, "new_status": "Done"}
                self.memory.remember_pattern(t, f"update_task_status:{task_id}:Done", success=True)
                return {"ok": True, "plan": plan, "note": "heuristic-ordinal"}

        # Fallback: ask LLM to draft plan (mocked if no API key)
        sys = "Ты планировщик. Верни JSON-план действий без лишних слов."
        llm = self.run(command_text, system_prompt=sys).content
        self.memory.remember_pattern(t, "llm_plan", success=False)
        return {"ok": True, "plan": {"llm": llm}, "note": "fallback-llm"}
    # test sync


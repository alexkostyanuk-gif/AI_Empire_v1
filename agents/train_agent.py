
import asyncio
from typing import Optional

from agents.base_agent import BaseAgent
from agents.memory_manager import MemoryManager
from config import TRAIN_INTERVAL_SEC, CONFIDENCE_DECAY
from utils.logger import log_info

class TrainAgent(BaseAgent):
    def __init__(self, name: str = "TrainAgent"):
        super().__init__(name=name)

    async def run_background_training(self, interval: Optional[int] = None):
        interval = interval or TRAIN_INTERVAL_SEC
        mem = MemoryManager()
        while True:
            await self.train_once(mem)
            await asyncio.sleep(interval)

    async def train_once(self, mem: MemoryManager):
        log_info("[TRAIN] Updating experience: decay + metrics")
        for p in mem.data.get("patterns", []):
            p["confidence"] = max(0.0, p.get("confidence", 0.5) * CONFIDENCE_DECAY)
        mem.update_stats(adaptivity=0.55)
        mem.save()
        log_info("[TRAIN] Done")

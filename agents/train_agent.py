import asyncio
import logging
from agents.base_agent import BaseAgent
from agents.memory_manager import MemoryManager

class TrainAgent(BaseAgent):
    def __init__(self):
        super().__init__("TrainAgent")
        self.memory_manager = MemoryManager()  # ✅ менеджер памяти
        self.logger.info("[TrainAgent] initialized successfully.")

    async def run_background_training(self):
        """Асинхронный цикл периодического обучения."""
        while True:
            self.logger.info("[TRAIN] Updating experience: decay + metrics")
            self.run_cycle()
            await asyncio.sleep(10)

    def run_cycle(self):
        """Запускает один цикл обучения."""
        self.logger.info("[TRAIN] Starting training cycle...")
        try:
            memory = self.memory_manager.load()

            # Фиктивное обновление уверенности в паттернах
            if "patterns" in memory and isinstance(memory["patterns"], list):
                for pattern in memory["patterns"]:
                    pattern["confidence"] = max(
                        0.1, pattern.get("confidence", 1.0) * 0.98
                    )

            self.memory_manager.save(memory)
            self.logger.info("[TRAIN] Training cycle completed successfully.")
            return {"ok": True, "patterns": len(memory.get("patterns", []))}
        except Exception as e:
            self.logger.exception(f"[TRAIN] Failed during training cycle: {e}")
            return {"error": str(e)}

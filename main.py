
import asyncio
from agents.meta_agent import MetaAgent
from agents.train_agent import TrainAgent
from export_report import export_progress
from utils.logger import log_info

# Demo in-memory tasks list (No Notion yet)
TASKS = [
    {"id": "task-001", "title": "Сделать интеграцию Telegram"},
    {"id": "task-002", "title": "Добавить поддержку Notion"},
    {"id": "task-003", "title": "Сделать отчётность"},
]

async def main():
    meta = MetaAgent()
    trainer = TrainAgent()

    # Launch background training
    asyncio.create_task(trainer.run_background_training(interval=10))  # short for demo

    # Example: natural command with ordinal
    cmd = "поменяй во второй задаче статус на сделано"
    result = meta.execute(cmd, tasks=TASKS)
    log_info(f"Execute result: {result}")

    # Export progress
    export_progress()

if __name__ == "__main__":
    asyncio.run(main())

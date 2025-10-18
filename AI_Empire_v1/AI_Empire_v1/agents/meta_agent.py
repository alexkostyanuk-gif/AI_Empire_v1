import logging
from agents.base_agent import BaseAgent
from agents.notion_agent import NotionAgent
from agents.train_agent import TrainAgent
from config import settings

class MetaAgent(BaseAgent):
    def __init__(self):
        super().__init__("MetaAgent")
        self.logger.info("[MetaAgent] initialized successfully.")

        # Регистрируем подагентов
        self.notion = NotionAgent(settings.NOTION_TOKEN, settings.NOTION_DATABASE_ID)
        self.train = TrainAgent()

        # Таблица команд
        self.commands = {
            "notion.list_tasks": self.notion.list_tasks,
            "notion.set_status": self.notion.set_status,
            "notion.update_property": self.notion.update_task_field,
            "train.run": self.train.run_cycle,
        }

    # Универсальный метод выполнения команды
    def execute(self, command: str, **kwargs):
        """
        Выполняет заданную команду и возвращает результат.
        Например:
            execute("notion.list_tasks")
            execute("notion.set_status", page_id="xxx", new_status="Done")
        """
        self.logger.info(f"[MetaAgent] Executing command: {command} | args={kwargs}")
        if command not in self.commands:
            self.logger.warning(f"[MetaAgent] Unknown command: {command}")
            return {"error": f"Unknown command: {command}"}

        try:
            func = self.commands[command]
            result = func(**kwargs)
            self.logger.info(f"[MetaAgent] Command '{command}' executed successfully.")
            return result
        except Exception as e:
            self.logger.exception(f"[MetaAgent] Error executing '{command}': {e}")
            return {"error": str(e)}


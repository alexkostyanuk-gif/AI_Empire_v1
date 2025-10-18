# agents/base_agent.py
import logging
from typing import Optional


class BaseAgent:
    """
    Базовый агент. Не инициализирует логирование сам (это делает main.py),
    чтобы не дублировать хендлеры. Даёт self.logger всем наследникам.
    """

    def __init__(self, name: str, model: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.model = model  # пока не используется
        # никаких обращений к OPENAI_API_KEY здесь не делаем, чтобы не было лишних логов
        self.logger.info(f"[{self.name}] initialized successfully.")


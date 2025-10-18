# config.py
# ======================================
# Конфигурация проекта AI_Empire_v1
# ======================================

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# --- Загружаем .env ---
load_dotenv()

# --- Глобальные константы (legacy & defaults) ---
DEFAULT_MODEL = "gpt-5"
MAX_TOKENS = 4000
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MEMORY_FILE = "storage/memory.json"
TRAIN_INTERVAL_SEC = 30        # интервал между циклами TrainAgent
CONFIDENCE_DECAY = 0.98        # коэффициент затухания обучения

# --- Основные настройки проекта ---
@dataclass(frozen=True)
class Settings:
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")
    NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")
    ENV: str = os.getenv("ENV", "dev")

    def validate(self):
        """Проверяет наличие критичных переменных"""
        missing = []
        for name in ("NOTION_TOKEN", "NOTION_DATABASE_ID"):
            if not getattr(self, name):
                missing.append(name)
        if missing:
            raise RuntimeError(
                f"❌ Missing required environment variables: {', '.join(missing)}"
            )


# --- Глобальный экземпляр ---
settings = Settings()
PROGRESS_REPORT = "storage/progress_report.json"


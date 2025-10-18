# config.py
# ============================
# Конфигурация проекта AI_Empire_v1
# Загружает переменные из .env
# и предоставляет доступ через объект settings
# ============================

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()


@dataclass(frozen=True)
class Settings:
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")
    NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")
    ENV: str = os.getenv("ENV", "dev")

    def validate(self):
        """Проверка, что важные переменные заданы"""
        missing = []
        for name in ("NOTION_TOKEN", "NOTION_DATABASE_ID"):
            if not getattr(self, name):
                missing.append(name)
        if missing:
            raise RuntimeError(
                f"❌ Missing required environment variables: {', '.join(missing)}"
            )


# Глобальный объект конфигурации
settings = Settings()

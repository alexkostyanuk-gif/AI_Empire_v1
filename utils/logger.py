# utils/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level: int = logging.INFO, log_dir: str = "logs") -> None:
    """
    Настраивает логирование для всего проекта:
    - консоль + файл (с ротацией);
    - единый формат сообщений.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Удаляем старые хендлеры (если logger уже конфигурировался)
    root = logging.getLogger()
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)

    root.setLevel(level)

    # Консоль
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    # Файл
    file_handler = RotatingFileHandler(
        Path(log_dir) / "ai_empire.log",
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    # Добавляем
    root.addHandler(console)
    root.addHandler(file_handler)

    logging.info("✅ Logging initialized")

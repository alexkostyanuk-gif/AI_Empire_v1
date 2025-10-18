# agents/memory_manager.py
import json
from pathlib import Path
from typing import Any, Dict


class MemoryManager:
    """
    Простой файловый менеджер памяти.
    Хранит данные в storage/memory.json и пишет атомарно (tmp -> replace).
    """

    def __init__(self, path: str = "storage/memory.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Читает память с диска или создаёт дефолтную структуру."""
        if not self.path.exists():
            default = {
                "patterns": [],
                "stats": {"trained_cycles": 0, "last_update": None},
            }
            self._atomic_write(default)
            return default
        return json.loads(self.path.read_text(encoding="utf-8"))

    # Публичные фасады
    def load(self) -> Dict[str, Any]:
        """Публичная обёртка над _load(): возвращает текущее состояние памяти."""
        # перечитываем с диска, чтобы видеть изменения из других процессов
        self.data = self._load()
        return self.data

    def save(self, data: Dict[str, Any]) -> None:
        """Сохраняет данные памяти на диск атомарно."""
        self.data = data
        self._atomic_write(self.data)

    # Вспомогательное
    def _atomic_write(self, data: Dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)

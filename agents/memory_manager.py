
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from config import MEMORY_FILE
from utils.logger import log_info

class MemoryManager:
    def __init__(self, path: Path = MEMORY_FILE):
        self.path = Path(path)
        self.data = self._load()
        log_info(f"Memory loaded: patterns={len(self.data.get('patterns', []))}")

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            self.path.write_text(json.dumps({
                "patterns": [],
                "stats": {"accuracy":0.0, "adaptivity":0.0, "reliability":0.0, "total_experience":0.0}
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ===== Patterns (lightweight 'weights of experience') =====
    def remember_pattern(self, input_text: str, mapped_to: str, success: bool = True) -> None:
        patterns: List[Dict[str, Any]] = self.data.setdefault("patterns", [])
        now = datetime.utcnow().isoformat() + "Z"
        for p in patterns:
            if p["input"] == input_text:
                p["usage_count"] = p.get("usage_count", 0) + 1
                p["confidence"] = max(0.0, min(1.0, p.get("confidence", 0.5) + (0.05 if success else -0.1)))
                p["last_used"] = now
                self.save()
                return
        patterns.append({
            "input": input_text,
            "mapped_to": mapped_to,
            "confidence": 0.6 if success else 0.4,
            "usage_count": 1,
            "last_used": now
        })
        self.save()

    def recall_best(self, input_text: str) -> Optional[Dict[str, Any]]:
        for p in self.data.get("patterns", []):
            if p["input"] == input_text:
                return p
        return None

    # ===== Stats (agent 'IQ' style metrics) =====
    def update_stats(self, accuracy: Optional[float] = None, adaptivity: Optional[float] = None, reliability: Optional[float] = None):
        stats = self.data.setdefault("stats", {"accuracy":0.0, "adaptivity":0.0, "reliability":0.0, "total_experience":0.0})
        if accuracy is not None:
            stats["accuracy"] = (stats["accuracy"] + max(0.0, min(1.0, accuracy))) / 2
        if adaptivity is not None:
            stats["adaptivity"] = (stats["adaptivity"] + max(0.0, min(1.0, adaptivity))) / 2
        if reliability is not None:
            stats["reliability"] = (stats["reliability"] + max(0.0, min(1.0, reliability))) / 2
        stats["total_experience"] = stats.get("total_experience", 0.0) + 1.0
        self.save()

    def all(self) -> Dict[str, Any]:
        return self.data

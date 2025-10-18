
import os
from pathlib import Path

# === Core settings ===
PROJECT_NAME = "AI_Empire_v1"

# Model & LLM
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-5")  # Patched to GPT-5 by default
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()  # optional; if empty, MockLLM is used

# Paths
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
MEMORY_FILE = STORAGE_DIR / "memory.json"
DB_FILE = STORAGE_DIR / "db.json"
PROGRESS_REPORT = STORAGE_DIR / "progress_report.json"

# Training / background
TRAIN_INTERVAL_SEC = int(os.getenv("TRAIN_INTERVAL_SEC", "1800"))  # 30 minutes
CONFIDENCE_DECAY = float(os.getenv("CONFIDENCE_DECAY", "0.99"))   # 1% decay per cycle

# Safety flags
STRICT_MODE = os.getenv("STRICT_MODE", "true").lower() in ("1","true","yes")

# Ensure storage exists at import time
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize default storage files if absent
if not MEMORY_FILE.exists():
    MEMORY_FILE.write_text('{        "patterns": [],        "stats": {            "accuracy": 0.0,            "adaptivity": 0.0,            "reliability": 0.0,            "total_experience": 0.0        }    }', encoding="utf-8")

if not DB_FILE.exists():
    DB_FILE.write_text('{"sessions": []}', encoding="utf-8")

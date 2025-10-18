# audit_repo.py
from __future__ import annotations
import importlib, json, os, sys, traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT = {"structure": {}, "imports": {}, "env": {}, "notion_ping": {}}

# ---- 1. Проверка структуры
expected = {
    "agents/base_agent.py": True,
    "agents/meta_agent.py": True,
    "agents/notion_agent.py": True,
    "agents/train_agent.py": True,
    "utils/logger.py": True,
    "utils/helpers.py": True,
    "config.py": True,
    "main.py": True,
    "requirements.txt": True,
    "test_notion.py": True,  # мы его добавляли
}

for rel, must in expected.items():
    REPORT["structure"][rel] = (PROJECT_ROOT / rel).exists()

# ---- 2. Проверка импортов/символов
def try_import(mod_name: str, attr: str | None = None):
    try:
        mod = importlib.import_module(mod_name)
        if attr:
            getattr(mod, attr)  # AttributeError если нет
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": repr(e), "trace": traceback.format_exc()}

REPORT["imports"]["utils.logger.setup_logging"] = try_import("utils.logger", "setup_logging")
REPORT["imports"]["config.settings"] = try_import("config", "settings")
REPORT["imports"]["agents.base_agent.BaseAgent"] = try_import("agents.base_agent", "BaseAgent")
REPORT["imports"]["agents.meta_agent.MetaAgent"] = try_import("agents.meta_agent", "MetaAgent")
REPORT["imports"]["agents.notion_agent.NotionAgent"] = try_import("agents.notion_agent", "NotionAgent")
REPORT["imports"]["agents.train_agent"] = try_import("agents.train_agent")

# ---- 3. Проверка env
REPORT["env"]["NOTION_TOKEN"] = bool(os.getenv("NOTION_TOKEN"))
REPORT["env"]["NOTION_DATABASE_ID"] = bool(os.getenv("NOTION_DATABASE_ID"))

# ---- 4. (опц.) Пинг Notion схемы — без модификаций
def notion_ping():
    try:
        if not (REPORT["env"]["NOTION_TOKEN"] and REPORT["env"]["NOTION_DATABASE_ID"]):
            return {"ok": False, "error": "Missing NOTION_TOKEN or NOTION_DATABASE_ID"}
        from agents.notion_agent import NotionAgent
        from config import settings
        agent = NotionAgent(settings.NOTION_TOKEN, settings.NOTION_DATABASE_ID)
        # доступна ли схема и есть ли status/select/multi_select поля
        types = agent.field_types
        summary = {
            "field_types": types,
            "has_status": any(t == "status" for t in types.values()),
            "has_select": any(t == "select" for t in types.values()),
            "has_multi_select": any(t == "multi_select" for t in types.values()),
        }
        return {"ok": True, "summary": summary}
    except Exception as e:
        return {"ok": False, "error": repr(e), "trace": traceback.format_exc()}

# Можно выключить если не хочешь сетевых вызовов
DO_NOTION_PING = True
REPORT["notion_ping"] = notion_ping() if DO_NOTION_PING else {"ok": None}

# ---- 5. Вывод отчёта
print(json.dumps(REPORT, ensure_ascii=False, indent=2))


import json
from datetime import datetime
from config import MEMORY_FILE, PROGRESS_REPORT
from utils.logger import log_info

def export_progress(memory_path=MEMORY_FILE, report_path=PROGRESS_REPORT):
    data = json.loads(open(memory_path, "r", encoding="utf-8").read())
    summary = {
        "date": datetime.utcnow().isoformat() + "Z",
        "stats": data.get("stats", {}),
        "patterns_learned": len(data.get("patterns", []))
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    log_info(f"Progress report written: {report_path}")

if __name__ == "__main__":
    export_progress()


from datetime import datetime

def ts():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "Z"

def log_info(msg):
    print(f"[INFO] {ts()} | {msg}")

def log_warn(msg):
    print(f"[WARN] {ts()} | {msg}")

def log_error(msg):
    print(f"[ERROR]{ts()} | {msg}")

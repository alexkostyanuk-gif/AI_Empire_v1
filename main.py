import os
import asyncio
from pathlib import Path
from utils.logger import setup_logging
from agents.meta_agent import MetaAgent
from export_report import export_progress

# === Автоматическая смена директории ===
# (чтобы storage/* и config.py всегда находились корректно)
os.chdir(Path(__file__).resolve().parent)

# === Основная точка входа ===
async def main():
    setup_logging()
    print("\n⚡ AI-Empire Booting Up...\n")

    # Инициализация MetaAgent (он создаёт всех остальных)
    meta = MetaAgent()

    # === Демонстрация: получаем задачи из Notion ===
    print("📋 Список задач из базы Notion:")
    tasks = meta.execute("notion.list_tasks")

    if isinstance(tasks, list) and tasks:
        for i, t in enumerate(tasks, 1):
            print(f"  {i}. {t['title']} — {t['status']}")
    elif isinstance(tasks, dict) and "error" in tasks:
        print("⚠️ Ошибка при получении задач:", tasks["error"])
    else:
        print("Нет задач или база пуста.")

    # === Запускаем цикл обучения ===
    print("\n🧠 Запуск обучающего цикла TrainAgent...")
    train_result = meta.execute("train.run")
    print("✅ Результат обучения:", train_result)

    # === Экспорт прогресса ===
    print("\n📦 Экспорт отчёта прогресса...")
    export_progress()
    print("📑 Прогресс успешно экспортирован в storage/progress_report.json")

    print("\n✅ Империя запущена успешно.\n")

# === Запуск программы ===
if __name__ == "__main__":
    asyncio.run(main())

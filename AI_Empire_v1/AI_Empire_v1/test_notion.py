# test_notion.py
from utils.logger import setup_logging
from config import settings
from agents.notion_agent import NotionAgent


def main():
    setup_logging()
    settings.validate()

    agent = NotionAgent(settings.NOTION_TOKEN, settings.NOTION_DATABASE_ID)

    print("=== LIST (up to 5) ===")
    tasks = agent.list_tasks(limit=5)
    for i, t in enumerate(tasks, 1):
        print(i, t)

    if not tasks:
        print("No tasks found in database.")
        return

    page_id = tasks[0]["id"]

    print("\n=== READ STATUS ===")
    before = agent.get_task_status(page_id)
    print("Status (before):", before)

    # Попробуем перевести в 'In progress' (или любой существующий у тебя статус)
    try_status = "In progress"

    try:
        print(f"\n=== SET STATUS → {try_status} ===")
        agent.set_task_status(page_id, try_status)
        after = agent.get_task_status(page_id)
        print("Status (after):", after)
    except Exception as e:
        print("Failed to set status:", e)

    print("\n=== UPDATE PROPERTY (example: 'Status' or 'Tags') ===")
    # пример для multi_select, если в базе есть поле 'Tags'
    try:
        agent.update_property(page_id, "Tags", ["AI", "Empire"])
        print("Tags updated (if field exists).")
    except Exception as e:
        print("Property update error:", e)


if __name__ == "__main__":
    main()

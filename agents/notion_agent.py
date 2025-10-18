import time
import logging
from notion_client import Client
from agents.base_agent import BaseAgent

class NotionAgent(BaseAgent):
    def __init__(self, token, database_id):
        super().__init__("NotionAgent")

        # Инициализация Notion SDK
        self.notion = Client(auth=token)
        self.database_id = database_id
        self.field_types = {}

        self.logger.info("[NotionAgent] initialized successfully.")
        self.logger.info("[NotionAgent] Initializing and refreshing schema...")
        self.refresh_schema()

    # === === === === === === === === === === === === ===
    def refresh_schema(self):
        """Загружает структуру базы (поля и типы)."""
        try:
            self.logger.info("[NotionAgent] Fetching database schema...")
            db = self.notion.databases.retrieve(database_id=self.database_id)
            props = db.get("properties", {})
            self.field_types = {name: p["type"] for name, p in props.items()}
            self.logger.info("[NotionAgent] Schema loaded successfully.")
        except Exception as e:
            self.logger.exception(f"[NotionAgent] Failed to load database schema: {e}")

    # === === === === === === === === === === === === ===
    def list_tasks(self, limit: int = 5):
        """Возвращает последние задачи из Notion."""
        self.logger.info(f"[NotionAgent] Fetching last {limit} tasks from Notion...")
        try:
            response = self.notion.databases.query(
                database_id=self.database_id,
                page_size=limit,
                sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
            )

            tasks = []
            for page in response.get("results", []):
                props = page.get("properties", {})
                title = (
                    props.get("Task Name", {})
                    .get("title", [{}])[0]
                    .get("plain_text", "(no title)")
                )
                status = props.get("Status", {}).get("select", {}).get("name", "No status")
                tasks.append({"title": title, "status": status, "id": page["id"]})

            self.logger.info(f"[NotionAgent] Retrieved {len(tasks)} tasks successfully.")
            return tasks

        except Exception as e:
            self.logger.exception(f"[NotionAgent] Failed to list tasks: {e}")
            return {"error": str(e)}

    # === === === === === === === === === === === === ===
    def set_status(self, page_id: str, new_status: str):
        """Меняет статус задачи (поле select/status)."""
        self.logger.info(f"[NotionAgent] Updating status for {page_id} → {new_status}")
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={"Status": {"select": {"name": new_status}}},
            )
            self.logger.info(f"[NotionAgent] Status updated to '{new_status}' successfully.")
            return {"ok": True, "status": new_status}
        except Exception as e:
            self.logger.exception(f"[NotionAgent] Failed to update status: {e}")
            return {"error": str(e)}

    # === === === === === === === === === === === === ===
    def update_task_field(self, page_id: str, field_name: str, value: str):
        """Обновляет любое текстовое поле задачи (rich_text)."""
        self.logger.info(f"[NotionAgent] Updating field '{field_name}' for {page_id} → {value}")
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={field_name: {"rich_text": [{"text": {"content": value}}]}},
            )
            self.logger.info(f"[NotionAgent] Field '{field_name}' updated successfully.")
            return {"ok": True, "field": field_name, "value": value}
        except Exception as e:
            self.logger.exception(f"[NotionAgent] Failed to update field '{field_name}': {e}")
            return {"error": str(e)}

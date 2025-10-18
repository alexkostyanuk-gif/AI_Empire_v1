# notion_agent.py
# ==========================
# NotionAgent — агент для взаимодействия с базой Notion.
# Поддерживает автоматическое определение типов свойств:
# status, select, multi_select, title, rich_text и т.д.
# ==========================

import logging
from notion_client import Client
from agents.base_agent import BaseAgent

class NotionAgent(BaseAgent):
    """
    Агент для взаимодействия с Notion API.
    Поддерживает чтение и обновление страниц с автоопределением типов свойств.
    """

    def __init__(self, notion_token: str, database_id: str):
        super().__init__("NotionAgent")
        self.database_id = database_id
        self.notion = Client(auth=notion_token)
        self.field_types = {}

        # Загружаем схему базы при инициализации
        try:
            logging.info("[NotionAgent] Fetching database schema...")
            db_info = self.notion.databases.retrieve(database_id=self.database_id)
            for name, prop in db_info["properties"].items():
                self.field_types[name] = prop["type"]
            logging.info(f"[NotionAgent] Loaded field types: {self.field_types}")
        except Exception as e:
            logging.error(f"[NotionAgent] Failed to load database schema: {e}")

    # ------------------------------
    # Вспомогательные функции
    # ------------------------------

    def _build_property_payload(self, field_name: str, value):
        """
        Формирует корректную структуру properties для обновления страницы.
        """
        field_type = self.field_types.get(field_name, "rich_text")

        if field_type == "status":
            return {"status": {"name": value}}

        elif field_type == "select":
            return {"select": {"name": value}}

        elif field_type == "multi_select":
            # поддерживает как list[str], так и строку через запятую
            if isinstance(value, str):
                value = [v.strip() for v in value.split(",")]
            return {"multi_select": [{"name": v} for v in value]}

        elif field_type == "title":
            return {"title": [{"text": {"content": str(value)}}]}

        elif field_type == "rich_text":
            return {"rich_text": [{"text": {"content": str(value)}}]}

        else:
            logging.warning(f"[NotionAgent] Unsupported property type '{field_type}' for '{field_name}'")
            return {"rich_text": [{"text": {"content": str(value)}}]}

    def _extract_property_value(self, prop_obj: dict):
        """
        Извлекает значение свойства из объекта Notion property.
        """
        prop_type = prop_obj.get("type")

        try:
            if prop_type == "status":
                return prop_obj["status"]["name"] if prop_obj["status"] else None
            elif prop_type == "select":
                return prop_obj["select"]["name"] if prop_obj["select"] else None
            elif prop_type == "multi_select":
                return [t["name"] for t in prop_obj["multi_select"]]
            elif prop_type == "title":
                return "".join([t["plain_text"] for t in prop_obj["title"]])
            elif prop_type == "rich_text":
                return "".join([t["plain_text"] for t in prop_obj["rich_text"]])
            elif prop_type == "number":
                return prop_obj["number"]
            elif prop_type == "checkbox":
                return prop_obj["checkbox"]
            else:
                return None
        except Exception as e:
            logging.warning(f"[NotionAgent] Failed to extract value for {prop_type}: {e}")
            return None

    # ------------------------------
    # Основные методы
    # ------------------------------

    def list_tasks(self, limit: int = 20):
        """
        Возвращает список задач (страниц) из базы Notion.
        """
        try:
            query = self.notion.databases.query(
                **{
                    "database_id": self.database_id,
                    "page_size": limit
                }
            )
            results = []
            for page in query["results"]:
                item = {"id": page["id"]}
                for name, prop in page["properties"].items():
                    item[name] = self._extract_property_value(prop)
                results.append(item)
            return results
        except Exception as e:
            logging.error(f"[NotionAgent] Failed to list tasks: {e}")
            return []

    def update_property(self, page_id: str, field_name: str, value):
        """
        Обновляет указанное свойство страницы.
        Автоматически определяет тип и формирует корректную структуру.
        """
        try:
            data = self._build_property_payload(field_name, value)
            self.notion.pages.update(
                page_id=page_id,
                properties={field_name: data}
            )
            logging.info(f"[NotionAgent] Updated '{field_name}' → '{value}' ({self.field_types.get(field_name)})")
        except Exception as e:
            logging.error(f"[NotionAgent] Failed to update '{field_name}': {e}")

    def get_task_status(self, page_id: str):
        """
        Возвращает статус задачи по ID страницы.
        """
        try:
            page = self.notion.pages.retrieve(page_id=page_id)
            for name, prop in page["properties"].items():
                if self.field_types.get(name) == "status":
                    return self._extract_property_value(prop)
            return None
        except Exception as e:
            logging.error(f"[NotionAgent] Failed to get task status: {e}")
            return None

    def set_task_status(self, page_id: str, new_status: str):
        """
        Устанавливает новый статус задачи (ищет первое поле типа 'status').
        """
        try:
            status_field = next((name for name, t in self.field_types.items() if t == "status"), None)
            if not status_field:
                logging.warning("[NotionAgent] No status field found in database.")
                return
            self.update_property(page_id, status_field, new_status)
        except Exception as e:
            logging.error(f"[NotionAgent] Failed to set task status: {e}")

# ==========================
# Пример использования
# ==========================
if __name__ == "__main__":
    import os

    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

    if not NOTION_TOKEN or not DATABASE_ID:
        print("❌ Please set NOTION_TOKEN and NOTION_DATABASE_ID environment variables.")
    else:
        agent = NotionAgent(NOTION_TOKEN, DATABASE_ID)
        tasks = agent.list_tasks(limit=5)
        for t in tasks:
            print(t)

from agents.base_agent import BaseAgent
from notion_client import Client

class NotionAgent(BaseAgent):
    def __init__(self, token, database_id):
        # !!! Сначала вызываем базовый инициализатор !!!
        super().__init__("NotionAgent")

        # Теперь логгер уже есть
        from notion_client import Client
        self.notion = Client(auth=token)
        self.database_id = database_id
        self.field_types = {}

        # Теперь можно логировать
        self.logger.info("[NotionAgent] Initializing and refreshing schema...")
        self.refresh_schema()


    def refresh_schema(self):
        try:
            self.logger.info("[NotionAgent] Fetching database schema...")
            db_info = self.notion.databases.retrieve(self.database_id)
            self.field_types = {
                name: prop["type"] for name, prop in db_info["properties"].items()
            }
            self.logger.info("[NotionAgent] Schema loaded successfully.")
        except Exception as e:
            self.logger.exception("[NotionAgent] Failed to load database schema: %s", e)

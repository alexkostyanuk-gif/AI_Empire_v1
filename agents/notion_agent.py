# agents/notion_agent.py
# ============================================
# NotionAgent — работа с Notion Database:
# - Автоопределение типов свойств (status, select, multi_select, title, rich_text, number, checkbox)
# - Валидация значений для status (только существующие опции)
# - Ретраи на 429/5xx с экспоненциальной паузой
# - Пагинация при чтении задач
# - Обновление (refresh) схемы базы на лету
# ============================================

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Iterable

from notion_client import Client
from notion_client.helpers import is_full_block  # не обязателен, но полезен
from agents.base_agent import BaseAgent


class NotionAgent(BaseAgent):
    def __init__(self, notion_token: str, database_id: str):
        super().__init__("NotionAgent")
        self.database_id = database_id
        self.notion = Client(auth=notion_token)
        self.field_types: Dict[str, str] = {}
        self._status_options: Dict[str, set] = {}  # { "Status": {"Todo","In progress","Done"} }
        self.refresh_schema()

    # ---------- СХЕМА / МЕТАДАННЫЕ ----------

    def refresh_schema(self) -> None:
        """Загрузить схему базы и кэшировать типы свойств + опции статусов."""
        try:
            self.logger.info("[NotionAgent] Fetching database schema...")
            db = self.notion.databases.retrieve(database_id=self.database_id)
            props = db.get("properties", {})
            self.field_types.clear()
            self._status_options.clear()

            for name, prop in props.items():
                ptype = prop.get("type")
                self.field_types[name] = ptype
                if ptype == "status":
                    opts = prop.get("status", {}).get("options", []) or []
                    self._status_options[name] = {o.get("name") for o in opts if o.get("name")}
            self.logger.info("[NotionAgent] Loaded field types: %s", self.field_types)
            if self._status_options:
                self.logger.info("[NotionAgent] Status options: %s", self._status_options)
        except Exception as e:
            self.logger.exception("[NotionAgent] Failed to load database schema: %s", e)

    # ---------- ВСПОМОГАТЕЛЬНОЕ ----------

    def _retry(self, fn, *args, **kwargs):
        """Простой экспоненциальный ретрай для 429/5xx."""
        max_attempts = 5
        backoff = 0.8
        for attempt in range(1, max_attempts + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                msg = str(e).lower()
                retriable = any(code in msg for code in (" 429", " 500", " 502", " 503", " 504"))
                if attempt == max_attempts or not retriable:
                    self.logger.exception("[NotionAgent] Request failed (no more retries): %s", e)
                    raise
                sleep_sec = round(backoff, 2)
                self.logger.warning("[NotionAgent] Retrying after %ss (attempt %s/%s)...", sleep_sec, attempt, max_attempts)
                time.sleep(sleep_sec)
                backoff *= 1.8

    @staticmethod
    def _ensure_list(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        if isinstance(value, Iterable):
            return [str(v).strip() for v in value if str(v).strip()]
        return [str(value)]

    def _build_property_payload(self, field_name: str, value: Any) -> Dict[str, Any]:
        """Сформировать корректное свойство Notion в зависимости от типа."""
        field_type = self.field_types.get(field_name, "rich_text")

        if field_type == "status":
            # Валидация: имя статуса должно существовать среди опций
            allowed = self._status_options.get(field_name, set())
            if value not in allowed:
                raise ValueError(
                    f"Unsupported status '{value}' for field '{field_name}'. "
                    f"Allowed: {sorted(allowed)}"
                )
            return {"status": {"name": value}}

        if field_type == "select":
            return {"select": {"name": value}}

        if field_type == "multi_select":
            items = self._ensure_list(value)
            return {"multi_select": [{"name": v} for v in items]}

        if field_type == "title":
            return {"title": [{"text": {"content": str(value)}}]}

        if field_type == "rich_text":
            return {"rich_text": [{"text": {"content": str(value)}}]}

        if field_type == "number":
            try:
                number = float(value)
            except Exception:
                raise ValueError(f"Field '{field_name}' expects number, got: {value!r}")
            return {"number": number}

        if field_type == "checkbox":
            return {"checkbox": bool(value)}

        # Fallback — безопасный rich_text
        self.logger.warning("[NotionAgent] Unsupported property type '%s' for '%s'. Using rich_text.", field_type, field_name)
        return {"rich_text": [{"text": {"content": str(value)}}]}

    @staticmethod
    def _extract_property_value(prop_obj: dict) -> Any:
        """Достать значение свойства из объекта Notion."""
        ptype = prop_obj.get("type")
        try:
            if ptype == "status":
                return prop_obj["status"]["name"] if prop_obj.get("status") else None
            if ptype == "select":
                return prop_obj["select"]["name"] if prop_obj.get("select") else None
            if ptype == "multi_select":
                return [t["name"] for t in prop_obj.get("multi_select", [])]
            if ptype == "title":
                return "".join([t.get("plain_text", "") for t in prop_obj.get("title", [])])
            if ptype == "rich_text":
                return "".join([t.get("plain_text", "") for t in prop_obj.get("rich_text", [])])
            if ptype == "number":
                return prop_obj.get("number")
            if ptype == "checkbox":
                return prop_obj.get("checkbox")
            return None
        except Exception:
            return None

    # ---------- ОСНОВНЫЕ ОПЕРАЦИИ ----------

    def list_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Вернуть первые N задач с распакованными полями."""
        collected: List[Dict[str, Any]] = []
        next_cursor: Optional[str] = None

        while len(collected) < limit:
            page_size = min(100, limit - len(collected))
            resp = self._retry(
                self.notion.databases.query,
                **{
                    "database_id": self.database_id,
                    "page_size": page_size,
                    **({"start_cursor": next_cursor} if next_cursor else {}),
                }
            )
            for page in resp.get("results", []):
                item = {"id": page["id"]}
                for name, prop in page.get("properties", {}).items():
                    item[name] = self._extract_property_value(prop)
                collected.append(item)
                if len(collected) >= limit:
                    break
            if not resp.get("has_more"):
                break
            next_cursor = resp.get("next_cursor")

        return collected

    def update_property(self, page_id: str, field_name: str, value: Any) -> None:
        """Обновить одно свойство страницы (тип определяется автоматически)."""
        payload = self._build_property_payload(field_name, value)
        self._retry(
            self.notion.pages.update,
            page_id=page_id,
            properties={field_name: payload},
        )
        self.logger.info("[NotionAgent] Updated %s → %r (%s)", field_name, value, self.field_types.get(field_name))

    def get_task_status(self, page_id: str) -> Optional[str]:
        """Вернуть значение первого поля типа status на странице."""
        page = self._retry(self.notion.pages.retrieve, page_id=page_id)
        for name, prop in page.get("properties", {}).items():
            if self.field_types.get(name) == "status":
                return self._extract_property_value(prop)
        return None

    def set_task_status(self, page_id: str, new_status: str) -> None:
        """Установить статус (первое поле типа 'status')."""
        status_field = next((n for n, t in self.field_types.items() if t == "status"), None)
        if not status_field:
            self.logger.warning("[NotionAgent] No status field found in database.")
            return
        self.update_property(page_id, status_field, new_status)

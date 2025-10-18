# agents/meta_agent.py
from __future__ import annotations

import logging
from typing import Any, Dict, Callable

from agents.base_agent import BaseAgent


class MetaAgent(BaseAgent):
    """
    Координатор: регистрирует агентов и роутит команды.
    Поддерживаемые команды:
      - notion.list_tasks {limit}
      - notion.update_property {page_id, field, value}
      - notion.set_status {page_id, status}
    """

    def __init__(self):
        super().__init__("MetaAgent")
        self._agents: Dict[str, BaseAgent] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    # ---------- регистрация ----------

    def register(self, name: str, agent: BaseAgent) -> None:
        self._agents[name] = agent
        self.logger.info("[MetaAgent] Registered agent '%s' (%s)", name, agent.__class__.__name__)
        # Авто-регистрация notion-хендлеров
        if name == "notion":
            self._register_notion_handlers(agent)

    def _register_notion_handlers(self, notion_agent: BaseAgent) -> None:
        from agents.notion_agent import NotionAgent  # локальный импорт для типов
        assert isinstance(notion_agent, NotionAgent)

        self._handlers["notion.list_tasks"] = lambda p: notion_agent.list_tasks(limit=int(p.get("limit", 20)))
        self._handlers["notion.update_property"] = lambda p: notion_agent.update_property(
            page_id=p["page_id"], field_name=p["field"], value=p["value"]
        )
        self._handlers["notion.set_status"] = lambda p: notion_agent.set_task_status(
            page_id=p["page_id"], new_status=p["status"]
        )

    # ---------- API ----------

    def handle(self, *args, **kwargs):
        """Не используется напрямую — вызывай route()."""
        return None

    def route(self, command: str, payload: Dict[str, Any]) -> Any:
        handler = self._handlers.get(command)
        if not handler:
            raise ValueError(f"Unknown command: {command}")
        self.logger.info("[MetaAgent] → %s %s", command, {k: v for k, v in payload.items() if k != 'value'})
        return handler(payload)


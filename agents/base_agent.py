import uuid
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from config import DEFAULT_MODEL


from utils.logger import log_info, log_warn

# --- Новый клиент OpenAI SDK v1.x ---
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    _openai_available = client is not None
except Exception as e:
    log_warn(f"OpenAI SDK not available: {e}")
    client = None
    _openai_available = False


class MockLLM:
    """Фолбэк, если ключ отсутствует или сеть недоступна."""
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        user_msg = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), '')
        return f"[MOCK:{kwargs.get('model', 'gpt-5')}] {user_msg[:400]}"


@dataclass
class LLMResponse:
    content: str
    trace_id: str
    model: str


import logging
from utils.logger import setup_logging

class BaseAgent:
    def __init__(self, name: str):
        self.name = name

        # Настраиваем логгер для агента
        setup_logging()
        self.logger = logging.getLogger(name)
        self.logger.info(f"[{self.name}] initialized successfully.")

        # Другие твои атрибуты (если есть)
        self.memory = None
        self.model = None


    def run(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Выполняет обращение к GPT-5 и возвращает ответ."""
        trace_id = str(uuid.uuid4())[:8]
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        log_info(f"[{trace_id}] {self.name} → {self.model}")

        # --- Новый корректный вызов GPT-5 (без temperature) ---
        if _openai_available and client:
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_completion_tokens=MAX_TOKENS
                )
                content = response.choices[0].message.content
            except Exception as e:
                log_warn(f"[{trace_id}] OpenAI error: {e}; falling back to MockLLM")
                content = self._mock.chat(messages, model=self.model)
        else:
            content = self._mock.chat(messages, model=self.model)

        return LLMResponse(content=content, trace_id=trace_id, model=self.model)



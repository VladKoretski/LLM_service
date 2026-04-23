import logging
import httpx
import base64
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.core.logging import logger

GIGACHAT_TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
FALLBACK_RESPONSE = "Сервис временно недоступен. Пожалуйста, попробуйте позже."

class GigaChatClient:
    def __init__(self):
        self.client_id = settings.gigachat_client_id
        self.client_secret = settings.gigachat_client_secret
        self.scope = settings.gigachat_scope
        self.base_url = settings.gigachat_base_url
        self.model_name = settings.llm_model_name
        self._access_token: str | None = None
        self._timeout = httpx.Timeout(settings.llm_timeout)

    async def _get_token(self) -> str:
        """Получение/обновление токена OAuth2"""
        if self._access_token:
            return self._access_token
            
        auth_str = f"{self.client_id}:{self.client_secret}"
        credentials = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        
        async with httpx.AsyncClient(verify=False, timeout=self._timeout) as client:
            response = await client.post(
                GIGACHAT_TOKEN_URL,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {credentials}",
                    "RqUID": "00000000-0000-0000-0000-000000000000"
                },
                data={"scope": self.scope}
            )
            response.raise_for_status()
            data = response.json()
            self._access_token = data["access_token"]
            logger.info("✅ Токен GigaChat получен")
            return self._access_token

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_llm(self, text: str) -> str:
        """Вызов GigaChat API"""
        token = await self._get_token()
        
        async with httpx.AsyncClient(verify=False, timeout=self._timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": "Ты полезный ассистент. Кратко суммаризируй текст или дай четкий ответ."},
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

# Глобальный экземпляр
gigachat = GigaChatClient()

async def call_llm(text: str) -> str:
    logger.info("Вызов GigaChat модели: %s", settings.llm_model_name)
    try:
        return await gigachat.call_llm(text)
    except httpx.HTTPError as e:
        logger.error("HTTP ошибка GigaChat: %s", str(e))
        raise
    except Exception as e:
        logger.error("Неожиданная ошибка GigaChat: %s", str(e))
        raise
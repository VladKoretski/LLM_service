from app.services.cache import SimpleCache
from app.services.llm_client import call_llm, FALLBACK_RESPONSE
from app.core.logging import logger
from app.models.schemas import ProcessResponse

cache = SimpleCache()

async def process_text(text: str) -> ProcessResponse:
    logger.info("Начало обработки запроса")
    
    cached = cache.get(text)
    if cached:
        logger.info("Cache HIT для запроса")
        return ProcessResponse(result=cached, source="cache", metadata={"cached": True})

    logger.info("Cache MISS. Вызов LLM...")
    try:
        raw_result = await call_llm(text)
        cleaned_result = raw_result.replace("\n", " ").strip()
        if not cleaned_result:
            raise ValueError("LLM вернул пустой ответ")
        
        cache.set(text, cleaned_result)
        logger.info("Ответ LLM обработан и сохранен в кеш")
        return ProcessResponse(result=cleaned_result, source="llm", metadata={"cached": False})
    except Exception as e:
        logger.error("Ошибка вызова/обработки LLM, активирован fallback: %s", str(e))
        return ProcessResponse(result=FALLBACK_RESPONSE, source="fallback", metadata={"error": str(e)})

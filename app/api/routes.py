import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import TextInput, ProcessResponse
from app.services.processor import process_text

router = APIRouter()
logger = logging.getLogger("llm_service.api")

@router.post("/process", response_model=ProcessResponse)
async def process_endpoint(data: TextInput):
    logger.info("Получен запрос на /process")
    try:
        result = await process_text(data.text)
        logger.info("Запрос обработан. Источник: %s", result.source)
        return result
    except ValueError as ve:
        logger.warning("Ошибка валидации ответа: %s", str(ve))
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error("Внутренняя ошибка сервера: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
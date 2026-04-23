from fastapi import FastAPI
from app.api.routes import router
from app.core.logging import logger

app = FastAPI(title="End-to-End LLM Service", version="1.0.0")
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("✅ LLM сервис запущен")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 LLM сервис остановлен")
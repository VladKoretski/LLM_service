from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("✅ LLM сервис запущен")
    yield
    # Shutdown
    logger.info("🛑 LLM сервис остановлен")

app = FastAPI(title="End-to-End LLM Service", version="1.0.0", lifespan=lifespan)
app.include_router(router, prefix="/api/v1")

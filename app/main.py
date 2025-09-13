from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
app.include_router(router)

from fastapi import FastAPI
from app.core.config import settings
from app.core.lifespan import lifespan

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan
)

# app.include_router()

@app.get("/")
async def root():
    return {"message": "Hello World"}
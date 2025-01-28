from fastapi import FastAPI

from app.handlers import router
from app.settings import settings
from app.vectorizer import Vectorizer

print(f"Start load model: {settings.model_name}")
Vectorizer()
print("Model has been loaded")

app = FastAPI()
app.include_router(router, prefix="/api/v1")


@app.get("/ping", tags=["health"])
def health():
    return "pong"

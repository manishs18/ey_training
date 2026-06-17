from fastapi import FastAPI
from app.api.chat import router

app = FastAPI(
    title="GenAI RAG API"
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "healthy"}
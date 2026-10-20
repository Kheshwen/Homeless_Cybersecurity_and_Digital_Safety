from fastapi import FastAPI
from app.api import web

app = FastAPI(title="ScamGuard API")

app.include_router(web.router)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the server is running."""
    return {"status": "ok"}
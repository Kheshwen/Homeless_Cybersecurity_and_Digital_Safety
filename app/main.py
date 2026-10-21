from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import web, whatsapp, meta_whatsapp
from app.db.seed import run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_seed()  # creates tables and seeds mock data on first run
    yield


app = FastAPI(title="ScamGuard API", lifespan=lifespan)

app.include_router(web.router)
app.include_router(whatsapp.router)
app.include_router(meta_whatsapp.router)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the server is running."""
    return {"status": "ok"}

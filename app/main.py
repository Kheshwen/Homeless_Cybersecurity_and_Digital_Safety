import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import web, whatsapp, meta_whatsapp
from app.db.seed import run_seed

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs database migrations and seeds initial mock mules/phrases on startup
    run_seed()
    
    # Spin up Telegram bot in a background thread so it runs concurrently with FastAPI
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    
    yield

app = FastAPI(title="ScamGuard API", lifespan=lifespan)

# Register routers
app.include_router(web.router)
app.include_router(whatsapp.router)
app.include_router(meta_whatsapp.router)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the server is running."""
    return {"status": "ok"}
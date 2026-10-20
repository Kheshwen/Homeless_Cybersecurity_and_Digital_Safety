from fastapi import FastAPI

app = FastAPI(title="ScamGuard API")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the server is running."""
    return {"status": "ok"}
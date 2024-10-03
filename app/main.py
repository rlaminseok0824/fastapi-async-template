from contextlib import asynccontextmanager
import logging
import sys


from fastapi import FastAPI


from app.core.db import session_manager
from app.api.main import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if session_manager is not None:
        await session_manager.close()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
from dotenv import load_dotenv
load_dotenv()

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import contact, services, reviews, search
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "")
    if raw.strip():
        return [x.strip() for x in raw.split(",") if x.strip()]

    return [
        "https://lebedi.pages.dev",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8088",
        "http://127.0.0.1:8088",
    ]


app = FastAPI(
    title="Resort",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contact.router)
app.include_router(services.router)
app.include_router(reviews.router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(search.router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "Resort"}
 # python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

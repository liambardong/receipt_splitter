import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI

from database import Base, engine
from routers import people_router, users_router, receipts_router
from logging import configure, Logger

load_dotenv()
configure()

logger = Logger(__name__)

app = FastAPI(
    title="Receipt Splitter API",
    description="Split receipts and track who owes what.",
)

if os.getenv("ENV", "development") == "development":
    Base.metadata.create_all(bind=engine)

app.include_router(people_router)
app.include_router(users_router)
app.include_router(receipts_router)


@app.on_event("startup")
def startup():
    env = os.getenv("ENV", "development")
    logger.info("Application started", ENV=env)
    if env == "development":
        logger.info("Database tables created", mode="development")


@app.on_event("shutdown")
def shutdown():
    logger.info("Application shutdown")


@app.middleware("http")
async def log_requests(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} {response.status_code} {duration_ms}ms"
    )
    return response


@app.get("/")
def read_root():
    return {"status": "healthy"}

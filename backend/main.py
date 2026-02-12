import os

from fastapi import FastAPI

from database import Base, engine
from routers import people_router, users_router, receipts_router

app = FastAPI(
    title="Receipt Splitter API",
    description="Split receipts and track who owes what.",
)

if os.getenv("ENV", "development") == "development":
    Base.metadata.create_all(bind=engine)

app.include_router(people_router)
app.include_router(users_router)
app.include_router(receipts_router)


@app.get("/")
def read_root():
    return {"status": "healthy"}

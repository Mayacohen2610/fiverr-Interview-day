"""
FastAPI application with a /health endpoint that checks PostgreSQL connectivity.
Returns {"status": "up"} when the database is reachable, {"status": "down"} otherwise.
"""
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI()

DATABASE_URL = "postgresql://admin:admin123@localhost:5432/fiverr_db"


@app.get("/health")
def health():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "up"}
    except Exception:
        return {"status": "down"}

"""
FastAPI application entry point.
Includes router with health check and toy management endpoints.
"""
from fastapi import FastAPI

from app.routes import router

app = FastAPI()
app.include_router(router)

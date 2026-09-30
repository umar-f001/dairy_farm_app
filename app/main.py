from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine, get_db
from app.models.base import Base
from app.api.api_v1 import api_router

# ==========================================
# FastAPI Lifespan Handler (Table Creation)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        print("Creating tables if they don't exist...")
        # Yeh automatic hmare User model (aur baad mein baaki models) ki tables bana dega
        await conn.run_sync(Base.metadata.create_all)
        print("Tables ready!")
    yield
    # Application band hote waqt engine ko saaf karega
    await engine.dispose()

# FastAPI App initialization
app = FastAPI(title="Dairy Farm Automation API", version="1.0.0", lifespan=lifespan)

# CORS Middleware (Frontend connection ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Database Connection Health Check
@app.get("/health", description="Database connection check karne ke liye")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to connect to DataBase: {str(e)}")

app.include_router(api_router, prefix="/api/v1")

from fastapi import APIRouter, HTTPException, Depends, status, Query

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime, timedelta, timezone, date
import random
from typing import Optional

from app.schema.milk_tracking import MilkLogCreate, MilkLogResponse
from app.models.milk_tracking import Milking
from app.models.animal import Animal
from app.core.database import get_db

router = APIRouter(prefix="/milking", tags=["Milk Production"])

yield_amount = 0

@router.get("/milkYield", description="Randomly generate yield of milk")
async def milkYield():
    global yield_amount
    yield_amount = random.randint(5, 25)
    return {"yield_amount": yield_amount}

# ====================================
# 2. ACTUAL PRODUCTION LOG ENDPOINT
# ====================================

@router.post("/uploadMilkRec", response_model=MilkLogResponse, status_code=status.HTTP_201_CREATED)
async def record_milk(log_data: MilkLogCreate, db: AsyncSession = Depends(get_db)):
    global yield_amount

    # 1. Animal check karein
    query = select(Animal).where(Animal.tag_number == log_data.tag_number)
    result = await db.execute(query)
    animal = result.scalar_one_or_none()

    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The cow with tag {log_data.tag_number} not found."
        )
    
    current_date = datetime.now(timezone.utc).date()

    # Naya record banayein
    new_milk_rec = Milking(
        tag_number=animal.tag_number,
        date=current_date,
        shift=log_data.shift,
        yield_liters=yield_amount  # Global variable se value li
    )

    try:
        db.add(new_milk_rec)
        await db.commit()
        await db.refresh(new_milk_rec)
        
        # Data save hone ke baad global variable ko wapas 0 kar dein
        yield_amount = 0
        
        return new_milk_rec

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {str(e)}"
        )

# ====================================
# Get MilK Record
# ====================================

@router.get("/get_milk_record", response_model=list[MilkLogResponse])
async def get_milk_rec(
    tag_number: Optional[str] = Query(None), 
    number_of_days: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    # Base query banayein aur default sorting laga dein
    query = select(Milking).order_by(Milking.tag_number.desc(), Milking.created_at.desc())

    # Animal validation check
    if tag_number is not None:
        extra_query = select(Animal).where(Animal.tag_number == tag_number)
        responce = await db.execute(extra_query)
        animal = responce.scalar_one_or_none()

        if not animal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"The cow with tag {tag_number} not found."
            )
        
        query = query.where(Milking.tag_number == tag_number)

    # Date validation aur filter
    if number_of_days is not None:
        target_date = datetime.now(timezone.utc).date() - timedelta(days=number_of_days)
        query = query.where(Milking.created_at >= target_date)
        
    # Query execute karein
    result = await db.execute(query)
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No milk records found for the given criteria."
        )
    
    return records

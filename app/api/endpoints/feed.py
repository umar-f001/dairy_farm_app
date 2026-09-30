from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schema.feed import InventoryCreate, InventoryUpdate, InventoryResponse
from app.core.database import get_db
from app.models.feed import Inventory  # Apne model ka sahi import path lagayein

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ---- 1. POST: Create Inventory Log ----
@router.post("/log_inventory", response_model=InventoryResponse, status_code=201)
async def log_inventory(inventory_data: InventoryCreate, db: AsyncSession = Depends(get_db)):
    new_log = Inventory(**inventory_data.model_dump())
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log


# ---- 2. GET: List All Inventory Logs ----
@router.get("/list_logs", response_model=list[InventoryResponse])
async def list_logs(db: AsyncSession = Depends(get_db)):
    query = select(Inventory).order_by(Inventory.current_date.desc(), Inventory.id.desc())
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs


# ---- 3. PATCH: Update Inventory Log ----
@router.patch("/update_log/{log_id}", response_model=InventoryResponse)
async def update_log(log_id: int, inventory_data: InventoryUpdate, db: AsyncSession = Depends(get_db)):
    # ID ke zariye log dhoondhein
    query = select(Inventory).where(Inventory.id == log_id)
    result = await db.execute(query)
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail=f"Inventory log with ID {log_id} not found.")

    # Sirf bheja hua data nikal kar update karein
    update_data = inventory_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(log, key, value)

    await db.commit()
    await db.refresh(log)
    return log


# ---- 4. DELETE: Delete Inventory Log ----
@router.delete("/delete_log/{log_id}", status_code=200)
async def delete_log(log_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Inventory).where(Inventory.id == log_id)
    result = await db.execute(query)
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail=f"Inventory log with ID {log_id} not found.")

    await db.delete(log)
    await db.commit()
    return {"message": f"Inventory log with ID {log_id} has been successfully deleted."}

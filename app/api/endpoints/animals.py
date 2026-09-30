from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schema.animal import AnimalCreate, AnimalUpdate, AnimalResponse
from app.core.database import get_db
from app.models.animal import Animal

router = APIRouter(prefix="/animals", tags=["Animals"])

# ---- Regester Animals record----
@router.post("/register_animal", response_model=AnimalResponse, status_code=201)
async def register_animal(animal_data : AnimalCreate, db: AsyncSession = Depends(get_db)):
    query = select(Animal).where(Animal.tag_number == animal_data.tag_number)
    result = await db.execute(query)
    existing_animal = result.scalar_one_or_none()

    if existing_animal:
        raise HTTPException(400, detail=f"Animal with Tag Number '{animal_data.tag_number}' already exists.")
    
    new_animal = Animal(**animal_data.model_dump())
    db.add(new_animal)
    await db.commit()
    await db.refresh(new_animal)

    return new_animal


# ---- Update Animals record----
@router.patch("/update_animal/{tag_number}", response_model=AnimalResponse)
async def update_animal(tag_number: str, animal_data: AnimalUpdate, db: AsyncSession = Depends(get_db)):
    # 1. Pehle check karein animal database mein hai ya nahi
    query = select(Animal).where(Animal.tag_number == tag_number)
    result = await db.execute(query)
    animal = result.scalar_one_or_none()

    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal with Tag Number '{tag_number}' not found.")

    # 2. Jo data user ne bheja hai usko extract karein (sirf wahi data jo generate/bheja gaya ho)
    update_data = animal_data.model_dump(exclude_unset=True)

    # 3. Agar user tag_number badal raha hai, toh check karein naya tag pehle se kisi aur ka toh nahi?
    if "tag_number" in update_data and update_data["tag_number"] != tag_number:
        dup_query = select(Animal).where(Animal.tag_number == update_data["tag_number"])
        dup_result = await db.execute(dup_query)
        if dup_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"Tag Number '{update_data['tag_number']}' is already taken by another animal.")

    # 4. Animal ke attributes ko loop ke zariye update karein
    for key, value in update_data.items():
        setattr(animal, key, value)

    # 5. Database mein save karein
    await db.commit()
    await db.refresh(animal)

    return animal


# ---- GET: List All Animals ----
@router.get("/list_animals", response_model=list[AnimalResponse])
async def list_animals(db: AsyncSession = Depends(get_db)):
    query = select(Animal).order_by(Animal.id.desc())
    result = await db.execute(query)
    animals = result.scalars().all()

    return animals

# ---- Delete Animals Record ----
@router.delete("/delete_animal/{tag_number}", status_code=200)
async def delete_animal(tag_number: str, db: AsyncSession = Depends(get_db)):
    # 1. Animal ko tag_number ke zariye dhoondhein
    query = select(Animal).where(Animal.tag_number == tag_number)
    result = await db.execute(query)
    animal = result.scalar_one_or_none()

    # 2. Agar animal nahi milta toh error dein
    if not animal:
        raise HTTPException(
            status_code=404, 
            detail=f"Animal with Tag Number '{tag_number}' not found."
        )
    
    # 3. Animal ko delete karein (Cascade ki wajah se milking records khud delete ho jayein ge)
    await db.delete(animal)
    await db.commit()

    # 4. Success response bheinjein
    return {"message": f"Animal with Tag Number '{tag_number}' and all its milking records have been successfully deleted."}

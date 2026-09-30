from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime


class AnimalCreate(BaseModel):
    tag_number: str = Field(..., description="Unique tag number like A47", min_length=2, max_length=20)
    breed: str = Field(..., description="Breed of the cow/buffalo, e.g., Cholistani, Sahiwal")
    gender: str | None = Field(default="Female", description="Gender of the animal, e.g., Female, Male", max_length=20)
    date_of_birth: date | None = Field(default=None, description="Date of birth of the animal")
    status: str = Field(default="Active", description="Active, Pregnant, Sick, Dry")


class AnimalUpdate(BaseModel):
    tag_number: str | None = Field(default=None, description="New tag number if changing", min_length=2, max_length=20)
    breed: str | None = Field(default=None, description="Breed of the cow/buffalo")
    gender: str | None = Field(default=None, description="Gender of the animal")
    date_of_birth: date | None = Field(default=None, description="Date of birth")
    status: str | None = Field(default=None, description="Active, Pregnant, Sick, Dry")


class AnimalResponse(BaseModel):
    id: int
    tag_number: str
    breed: str
    gender: str | None
    date_of_birth: date | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field

class MilkLogCreate(BaseModel):
    tag_number : str = Field(..., description= "Tag Number of the cow")
    shift : str = Field(..., description="'Morning' or 'Evening'")


class MilkLogResponse(BaseModel):

    id : int
    tag_number : str
    date : date
    shift: str
    yield_liters: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
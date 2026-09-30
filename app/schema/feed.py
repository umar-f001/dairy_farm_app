from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime


# ---- 1. Inventory Create Schema ----
class InventoryCreate(BaseModel):
    quantity_kg: float = Field(..., description="Quantity of feed/item in kilograms", gt=0)
    supplier_name: str = Field(default="General Market", description="Name of the supplier", max_length=100)
    total_cost: float = Field(default=0.0, description="Total cost of the purchase", ge=0)
    current_date: date = Field(default_factory=date.today, description="Date of purchase/log")


# ---- 2. Inventory Update Schema ----
class InventoryUpdate(BaseModel):
    quantity_kg: float | None = Field(default=None, description="Updated quantity in kg", gt=0)
    supplier_name: str | None = Field(default=None, description="Updated supplier name", max_length=100)
    total_cost: float | None = Field(default=None, description="Updated total cost", ge=0)
    current_date: date | None = Field(default=None, description="Updated date")


# ---- 3. Inventory Response Schema ----
class InventoryResponse(BaseModel):
    id: int
    quantity_kg: float
    supplier_name: str
    total_cost: float
    current_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

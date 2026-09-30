import datetime

from app.models.base import Base

from sqlalchemy import String, DateTime, Date, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

class Inventory(Base):
    __tablename__ = "inventory_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(100), default="General Market", nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    current_date: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today, nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)

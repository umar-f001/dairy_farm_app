import datetime

from app.models.base import Base

from sqlalchemy import String, DateTime, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.milk_tracking import Milking

class Animal(Base):
    __tablename__ = "animals"

    id : Mapped[int] = mapped_column(primary_key=True)
    tag_number : Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    breed : Mapped[str] = mapped_column(String(50), nullable=False)
    gender : Mapped[str] = mapped_column(String(20), nullable=False)
    date_of_birth : Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status : Mapped[str] = mapped_column(String(30), default="Acive", nullable=False)
    created_at : Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    # created_at : Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    # created_at : Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    milking_records: Mapped[list["Milking"]] = relationship("Milking", back_populates="animal", cascade="all, delete-orphan")
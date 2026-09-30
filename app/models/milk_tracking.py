import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, Float, Date,ForeignKey

from app.models.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.animal import Animal

class Milking(Base):
    __tablename__ = "milk_logs"

    id : Mapped[int] = mapped_column(primary_key=True)
    tag_number : Mapped[str] = mapped_column(String(20), ForeignKey("animals.tag_number"),nullable=False)
    date : Mapped[datetime.date] = mapped_column(Date, server_default=func.now())
    shift: Mapped[str] = mapped_column(String(20), nullable=False)
    yield_liters: Mapped[float] = mapped_column(Float, nullable=False)
    # created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    animal : Mapped["Animal"] = relationship("Animal", back_populates="milking_records")
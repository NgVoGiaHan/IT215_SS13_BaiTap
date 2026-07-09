from sqlalchemy import Column, Integer, String, Float
from database import Base

class BoardingSlot(Base):
    __tablename__ = "boarding_slots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slot_number = Column(String(50), unique=True, nullable=False, index=True)
    room_size = Column(String(30), nullable=False)
    price_per_day = Column(Float, nullable=False)
    status = Column(String(30), default="VACANT", nullable=False)

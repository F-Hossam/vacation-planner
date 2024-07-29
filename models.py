from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True)
    email = Column(String(30), unique=True)
    first_name = Column(String(10))
    last_name = Column(String(10))
    hashed_password = Column(String(70))

    vacation = relationship("Vacations", back_populates="user")


class Vacations(Base):
    __tablename__ = 'vacations'

    id = Column(Integer, primary_key=True, index=True)
    city_of_residence = Column(String(100))
    destination = Column(String(50)) 
    iternary = Column(Text)
    budget_breakdown = Column(Text)
    total_estimated_cost = Column(String(30))
    travel_dates = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates="vacation")
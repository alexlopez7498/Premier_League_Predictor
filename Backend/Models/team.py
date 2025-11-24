from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

# current team model will add more attributes later
class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(Integer, index=True)
    name = Column(String, unique=True, index=True)
    city = Column(String, index=True)

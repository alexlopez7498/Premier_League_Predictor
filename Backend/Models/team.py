from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

# current team model table
class Team(Base):
    __tablename__ = "team"

    name = Column(String, primary_key=True, index=True)
    rank = Column(Integer, index=True)
    matchesPlayed = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    goalsFor = Column(Integer, default=0)
    goalsAgainst = Column(Integer, default=0)
    goalDifference = Column(Integer, default=0)
    points = Column(Integer, default=0)
    pointsPerGame = Column(Float, default=0.00)
    expectedGoals = Column(Float, default=0.00)
    expectedGoalsAllowed = Column(Float, default=0.00)  
    expectedGoalsDifference = Column(Float, default=0.00)
    expectedGoalsPerGame = Column(Float, default=0.00)
    attendence = Column(Integer, default=0)
    topScorer = Column(String, default="")
    goalkeeper = Column(String, default="")
    players = relationship("Player", back_populates="team")
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

# current team model table
class Team(Base):
    __tablename__ = "team"

    rank = Column(Integer, index=True)
    name = Column(String, primary_key=True, index=True)
    matchesPlayed = Column(Integer, default = 0)
    wins = Column(Integer, default = 0)
    draws = Column(Integer, default = 0)
    losses = Column(Integer, default = 0)
    goalsFor = Column(Integer, default = 0)
    goalsAgainst = Column(Integer, default = 0)
    goalDifference = Column(Integer, default = 0)
    points = Column(Integer, default = 0)
    goalsPer90 = Column(Float, default=0.00)
    expectedGoals = Column(Float, default=0.00)
    expectedGoalsAllowed = Column(Float, default=0.00)  
    expectedGoalsDifference = Column(Float, default=0.00)
    expectedGoalsDifferencePer90 = Column(Float, default=0.00)
    last5Wins = Column(String, index=True)
    attendance = Column(Integer, default = 0)
    topTeamScorer = Column(String)
    goalkeeper = Column(String)
    
    matches = relationship("Match", back_populates="team", cascade="all, delete", passive_deletes=True)
    players = relationship("Player", back_populates="team", cascade="all, delete", passive_deletes=True)
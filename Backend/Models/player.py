from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    nation = Column(String, index=True)
    position = Column(String, index=True)
    age = Column(Integer)
    matchesPlayed = Column(Integer, default=0)
    starts = Column(Integer, default=0)
    minutes = Column(Integer, default=0)
    minutesPerMatch = Column(Float, default=0.00)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    goalsAndAssists = Column(Float, default=0.00)
    nonPenaltyGoals = Column(Integer, default=0)
    penaltyGoals = Column(Integer, default=0)
    penaltyAttempts = Column(Integer, default=0)
    yellowCards = Column(Integer, default=0)
    redCards = Column(Integer, default=0)
    expectedGoals = Column(Float, default=0.00)
    expectedNonPenaltyGoals = Column(Float, default=0.00)
    expectedAssists = Column(Float, default=0.00)
    expectedNonPenaltyGoalsAndAssists = Column(Float, default=0.00)
    progressiveCarries = Column(Integer, default=0)
    progessivePasses = Column(Integer, default=0)
    progessivePassesReceived = Column(Integer, default=0)
    goalsPer90 = Column(Float, default=0.00)
    assistsPer90 = Column(Float, default=0.00)
    goalsAndAssistsPer90 = Column(Float, default=0.00)
    nonPenaltyGoalsPer90 = Column(Float, default=0.00)
    nonPenaltyGoalsAndAssistsPer90 = Column(Float, default=0.00)
    expectedGoalsPer90 = Column(Float, default=0.00)
    expectedAssistsPer90 = Column(Float, default=0.00)
    expectedGoalsAndAssistsPer90 = Column(Float, default=0.00)
    expectedNonPenaltyGoalsPer90 = Column(Float, default=0.00)
    expectedNonPenaltyGoalsAndAssistsPer90 = Column(Float, default=0.00)

    team_name = Column(String,ForeignKey("team.name", ondelete="CASCADE"),nullable=False)
    team = relationship("Team", back_populates="players")
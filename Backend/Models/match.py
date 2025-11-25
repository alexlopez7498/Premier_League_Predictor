from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

# current match model table
class Match(Base):
    __tablename__ = "match"

    match_id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    time = Column(String, index=True)
    round = Column(String, index=True)
    day = Column(String, index=True)
    venue = Column(String, index=True)
    result = Column(String, index=True)
    gf = Column(Integer, default=0)
    ga = Column(Integer, default=0)
    opponent = Column(String, index=True)
    xg = Column(Float, default=0.00)
    xga = Column(Float, default=0.00)
    poss = Column(Float, default=0.00)
    attendance = Column(Integer, default=0)
    captain = Column(String, index=True)
    formation = Column(String, index=True)
    oppFormation = Column(String, index=True)
    referee = Column(String, index=True)

    team_name = Column(String, ForeignKey("team.name"))

    team = relationship("Team", back_populates="matches")


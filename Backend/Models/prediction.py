from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

#Prediction model table
class Prediction(Base):
    __tablename__ = "prediction"

    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String, index=True)
    away_team = Column(String, index=True)
    home_win_prob = Column(Float, default=0.00)
    draw_prob = Column(Float, default=0.00)
    away_win_prob = Column(Float, default=0.00)
    predicted_score = Column(String, index=True)
    predicted_winner = Column(String, index=True)
    confidence = Column(Float, default=0.00)
    accuracy = Column(Float, default=0.00)
    precision = Column(Float, default=0.00)
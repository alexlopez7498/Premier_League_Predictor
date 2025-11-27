from fastapi import APIRouter, HTTPException, Depends
from Models.team import Base
from database import engine, get_db
from sqlalchemy.orm import Session
from Controllers.PredictionController import readPredictionPerTeam, readAllPredictions, predictMatchOutcome, Prediction
from Controllers.MatchController import MatchBase

router = APIRouter()

#API call post request to create a prediction of a match
@router.post("/predict/", tags=["predictions"])
async def predict_match(match: MatchBase, db: Session = Depends(get_db)):
    return await predictMatchOutcome(match, db)

#API call get request to get all entries of predictions
@router.get("/predictions/", tags=["predictions"])
async def getAllPredictions(db: Session = Depends(get_db)):
    return await readAllPredictions(db)

@router.get("/predictions/{teamName}", tags=["predictions"])
async def getPredictionsPerTeam(teamName: str, db:Session = Depends(get_db)):
    return await readPredictionPerTeam(teamName, db)
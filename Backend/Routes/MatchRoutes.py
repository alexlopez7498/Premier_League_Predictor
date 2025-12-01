from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Union
from typing import List, Annotated
from Models.team import Base
from database import engine, get_db
from sqlalchemy.orm import Session
from Controllers.TeamController import importLeagueTable, readTeams, createTeam, TeamBase
from Controllers.PlayerController import importPlayers, readAllPlayers, readPlayersPerTeam, createPlayer, PlayerBase
from Controllers.MatchController import getMatchesPerWeek, matchesCurrentWeek, importMatches, readAllMatches, readMatchesPerTeam, readMatchById, createMatch, MatchBase

router = APIRouter()

#API call get request to get all matches in the database
@router.get("/matches/", tags=["matches"])
async def getAllMatches(db: Session = Depends(get_db)):
    return readAllMatches(db)

@router.post("/matches/import", tags=["matches"])
async def importAllMatches(db: Session = Depends(get_db)):
    return await importMatches("../WebScraper/schedules_2025_2026.csv", db)

#API call get request to get all players from a specific team
@router.get("/matches/team/{team_name}", tags=["matches"])
async def getMatchesPerTeam(team_name: str, db: Session = Depends(get_db)):
    return await readMatchesPerTeam(team_name, db)

#API call post request to add a player to the database
@router.post("/matches/", tags=["matches"])
async def addMatch(match: MatchBase, db: Session = Depends(get_db)):
    return await createMatch(match,db)

#API call get request to get all matches in the current week
@router.get("/matches/current-week", tags=["matches"])
async def getMatchesCurrentWeek(db:Session = Depends(get_db)):
    return await matchesCurrentWeek(db)

#API call get request to get all matches for a specific week
@router.get("/matches/Matchweek/{weekNumber}",tags=["matches"])
async def getCallMatchesPerWeek(weekNumber:int, db:Session = Depends(get_db)):
    return await getMatchesPerWeek(weekNumber,db)

#API call get request to get a single match by match_id
@router.get("/matches/{match_id}", tags=["matches"])
async def getMatchById(match_id: int, db: Session = Depends(get_db)):
    return readMatchById(match_id, db)
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Union
from typing import List, Annotated
from Models.team import Base
from database import engine, get_db
from sqlalchemy.orm import Session
from Controllers.TeamController import importLeagueTable, readTeams, createTeam, TeamBase
from Controllers.PlayerController import importPlayers, readAllPlayers, readPlayersPerTeam, createPlayer, PlayerBase
from Controllers.MatchController import importMatches, readAllMatches, readMatchesPerTeam, createMatch, MatchBase

router = APIRouter()

#API call get request to get all teams in the database
@router.get("/teams/", tags=["teams"])
def getAllTeams(db: Session = Depends(get_db)):
    return readTeams(db)

#API call post request to add a team to the database
@router.post("/teams/import", tags=["teams"])
async def importTeams(db: Session = Depends(get_db)):
    return await importLeagueTable("WebScraper/table.csv", db)

@router.post("/teams/", tags=["teams"])
async def createTeamRoute(team: TeamBase, db: Session = Depends(get_db)):
    return await createTeam(team, db)
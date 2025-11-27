from fastapi import APIRouter, HTTPException, Depends
from Models.team import Base
from database import engine, get_db
from sqlalchemy.orm import Session
from Controllers.PlayerController import importPlayers, readAllPlayers, readPlayersPerTeam, createPlayer, PlayerBase

router = APIRouter()

#API call get request to get all players from the database
@router.get("/players/", tags=["players"])
async def getAllPlayers(db: Session = Depends(get_db)):
    return readAllPlayers(db)

#API call post request to add a player to the database
@router.post("/players/", tags=["players"])
async def addPlayer(player: PlayerBase, db: Session = Depends(get_db)):
    return await createPlayer(player,db)

#API call post request to import players from a CSV file
@router.post("/players/import", tags=["players"])
async def importAllPlayers(db: Session = Depends(get_db)):
    return await importPlayers("../WebScraper/stats.csv", db)

#API call get request to get all players from a specific team
@router.get("/players/{team_name}", tags=["players"])
async def getPlayersPerTeam(team_name: str, db: Session = Depends(get_db)):
    return await readPlayersPerTeam(team_name, db)

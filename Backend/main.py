from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Union
from typing import List, Annotated
from Models.team import Base
from database import engine, get_db
from sqlalchemy.orm import Session
from Controllers.TeamController import importLeagueTable, readTeams, createTeam, TeamBase
from Controllers.PlayerController import importPlayers, readAllPlayers, readPlayersPerTeam, createPlayer, PlayerBase
from Controllers.MatchController import importMatches, readAllMatches, readMatchesPerTeam, createMatch, MatchBase

#starts the FastAPI app
app = FastAPI()

#creates all tables and schemas in postgres database
Base.metadata.create_all(bind=engine)

#basic root get request to test if backend is running
@app.get("/")
def read_root():
    return {"Hello": "World"}



#API call get request to get all teams in the database
@app.get("/teams/")
def getAllTeams(db: Session = Depends(get_db)):
    return readTeams(db)

#API call post request to add a team to the database
@app.post("/teams/import")
async def importTeams(db: Session = Depends(get_db)):
    return await importLeagueTable("../WebScraper/table.csv", db)



#API call get request to get all players from the database
@app.get("/players/")
async def getAllPlayers(db: Session = Depends(get_db)):
    return readAllPlayers(db)

#API call get request to get all players from a specific team
@app.get("/players/team/{team_name}")
async def getPlayersPerTeam(team_name: str, db: Session = Depends(get_db)):
    return await readPlayersPerTeam(team_name, db)

#API call post request to add a player to the database
@app.post("/players/")
async def addPlayer(player: PlayerBase, db: Session = Depends(get_db)):
    return await createPlayer(player,db)

#API call post request to import players from a CSV file
@app.post("/players/import")
async def importAllPlayers(db: Session = Depends(get_db)):
    return await importPlayers("../WebScraper/stats.csv", db)

#API call get request to get all players from a specific team
@app.get("/players/{team_name}")
async def getPlayersPerTeam(team_name: str, db: Session = Depends(get_db)):
    return await readPlayersPerTeam(team_name, db)

#API call get request to get all matches in the database
@app.get("/matches/")
async def getAllMatches(db: Session = Depends(get_db)):
    return readAllMatches(db)

@app.post("/matches/import")
async def importAllMatches(db: Session = Depends(get_db)):
    return await importMatches("../WebScraper/schedules_2025_2026.csv", db)

#API call get request to get all players from a specific team
@app.get("/matches/team/{team_name}")
async def getMatchesPerTeam(team_name: str, db: Session = Depends(get_db)):
    return await readMatchesPerTeam(team_name, db)

#API call post request to add a player to the database
@app.post("/matches/")
async def addMatch(match: MatchBase, db: Session = Depends(get_db)):
    return await createMatch(match,db)



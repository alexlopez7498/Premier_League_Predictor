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
from Routes.PlayerRoutes import router as playerRouter
from Routes.TeamRoutes import router as teamRouter
from Routes.MatchRoutes import router as matchRouter

#starts the FastAPI app
app = FastAPI()

app.include_router(playerRouter)
app.include_router(teamRouter)
app.include_router(matchRouter)
#creates all tables and schemas in postgres database
Base.metadata.create_all(bind=engine)

#basic root get request to test if backend is running
@app.get("/")
def read_root():
    return {"Hello": "World"}
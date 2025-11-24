from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Union
from typing import List, Annotated
from Models.team import Base
from database import engine, get_db
from sqlalchemy.orm import Session
from Controllers.TeamController import read_teams, create_team, TeamBase

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
def get_all_teams(db: Session = Depends(get_db)):
    return read_teams(db)

#API call post request to add a team to the database
@app.post("/teams/")
async def add_team(team: TeamBase, db: Session = Depends(get_db)):
    return await create_team(team, db)

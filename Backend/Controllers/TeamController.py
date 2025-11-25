from fastapi import HTTPException, Depends
from pydantic import BaseModel
from Models.team import Team
from database import get_db
from sqlalchemy.orm import Session

class TeamBase(BaseModel):
    name: str
    city: str
    rank: int

# API call get request to get all teams in the database
def read_teams(db: Session):
    teams = db.query(Team).all()
    if teams is None:
        raise HTTPException(status_code=404, detail="No teams found")
    return teams

# API call post request to add a team to the database
async def create_team(team: TeamBase, db: Session):
    dbTeam = Team(name=team.name, city=team.city, rank=team.rank)
    db.add(dbTeam)
    db.commit()
    db.refresh(dbTeam)
    return dbTeam

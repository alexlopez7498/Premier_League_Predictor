from fastapi import HTTPException, Depends
from pydantic import BaseModel
from Models.team import Team
from database import Base, get_db
from sqlalchemy.orm import Session

class TeamBase(BaseModel):
    name: str
    city: str
    rank: int
    matchesPlayed: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goalsFor: int = 0
    goalsAgainst: int = 0
    goalDifference: int = 0
    points: int = 0
    pointsPerGame: float = 0.00
    expectedGoals: float = 0.00
    expectedGoalsAllowed: float = 0.00
    expectedGoalsDifference: float = 0.00
    expectedGoalsPerGame: float = 0.00
    attendence: int = 0
    topScorer: str = ""
    goalkeeper: str = ""


# API call get request to get all teams in the database
def read_teams(db: Session):
    teams = db.query(Team).all()
    if teams is None:
        raise HTTPException(status_code=404, detail="No teams found")
    return teams

# API call post request to add a team to the database
async def create_team(team: TeamBase, db: Session):
    dbTeam = Team(
        name=team.name, 
        rank=team.rank,
        matchesPlayed=team.matchesPlayed,
        wins=team.wins,
        draws=team.draws,
        losses=team.losses,
        goalsFor=team.goalsFor,
        goalsAgainst=team.goalsAgainst,
        goalDifference=team.goalDifference,
        points=team.points,
        pointsPerGame=team.pointsPerGame,
        expectedGoals=team.expectedGoals,
        expectedGoalsAllowed=team.expectedGoalsAllowed,
        expectedGoalsDifference=team.expectedGoalsDifference,
        expectedGoalsPerGame=team.expectedGoalsPerGame,
        attendence=team.attendence,
        topScorer=team.topScorer,
        goalkeeper=team.goalkeeper
    )
    db.add(dbTeam)
    db.commit()
    db.refresh(dbTeam)
    return dbTeam

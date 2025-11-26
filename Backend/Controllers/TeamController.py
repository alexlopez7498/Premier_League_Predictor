from fastapi import HTTPException, Depends
from pydantic import BaseModel
from Models.team import Team
from database import Base, get_db
from sqlalchemy.orm import Session
import pandas as pd

class TeamBase(BaseModel):
    rank: int
    name: str
    matchesPlayed: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goalsFor: int = 0
    goalsAgainst: int = 0
    goalDifference: int = 0
    points: int = 0
    goalsPer90: float = 0.00
    expectedGoals: float = 0.00
    expectedGoalsAllowed: float = 0.00
    expectedGoalsDifference: float = 0.00
    expectedGoalsDifferencePer90: float = 0.00
    last5Wins: str = ""
    attendance: int = 0
    topTeamScorer: str = ""
    goalkeeper: str = ""


# API call get request to get all teams in the database
def readTeams(db: Session):
    teams = db.query(Team).all()
    if teams is None:
        raise HTTPException(status_code=404, detail="No teams found")
    return teams

# Import league table from CSV and insert into database
async def importLeagueTable(csv_path: str, db: Session):
    try:
        df = pd.read_csv(csv_path)
        
        # Clear existing data
        db.query(Team).delete()
        db.commit()
        
        # Insert each row into database
        for _, row in df.iterrows():
            tableEntry = Team(
                rank=int(row.get('Rk', 0)) if pd.notna(row.get('Rk', 0)) else 0,
                name=str(row.get('Squad', '')),
                matchesPlayed=int(row.get('MP', 0)) if pd.notna(row.get('MP', 0)) else 0,
                wins=int(row.get('W', 0)) if pd.notna(row.get('W', 0)) else 0,
                draws=int(row.get('D', 0)) if pd.notna(row.get('D', 0)) else 0,
                losses=int(row.get('L', 0)) if pd.notna(row.get('L', 0)) else 0,
                goalsFor=int(row.get('GF', 0)) if pd.notna(row.get('GF', 0)) else 0,
                goalsAgainst=int(row.get('GA', 0)) if pd.notna(row.get('GA', 0)) else 0,
                goalDifference=int(row.get('GD', 0)) if pd.notna(row.get('GD', 0)) else 0,
                points=int(row.get('Pts', 0)) if pd.notna(row.get('Pts', 0)) else 0,
                goalsPer90=float(row.get('GF/90', 0)) if pd.notna(row.get('GF/90', 0)) else 0.00,
                expectedGoals=float(row.get('xG', 0)) if pd.notna(row.get('xG', 0)) else 0.00,
                expectedGoalsAllowed=float(row.get('xGA', 0)) if pd.notna(row.get('xGA', 0)) else 0.00,
                expectedGoalsDifference=float(row.get('xGD', 0)) if pd.notna(row.get('xGD', 0)) else 0.00,
                expectedGoalsDifferencePer90=float(row.get('xGD/90', 0)) if pd.notna(row.get('xGD/90', 0)) else 0.00,
                last5Wins=str(row.get('Last 5', '')),
                attendance=int(row.get('Attendance', 0)) if pd.notna(row.get('Attendance', 0)) else 0,
                topTeamScorer=str(row.get('Top Team Scorer', '')),
                goalkeeper=str(row.get('Goalkeeper', ''))
            )
            db.add(tableEntry)
        
        db.commit()
        return {"message": f"Successfully imported {len(df)} teams into database"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error importing table: {str(e)}")

# API call post request to add a team to the database
async def createTeam(team: TeamBase, db: Session):
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
        expectedGoals=team.expectedGoals,
        expectedGoalsAllowed=team.expectedGoalsAllowed,
        expectedGoalsDifference=team.expectedGoalsDifference,
        expectedGoalsPerGame=team.goalsPer90,
        expectedGoalsDifferencePer90=team.expectedGoalsDifferencePer90,
        last5Wins=team.last5Wins,
        attendence=team.attendance,
        topScorer=team.topTeamScorer,
        goalkeeper=team.goalkeeper
    )
    db.add(dbTeam)
    db.commit()
    db.refresh(dbTeam)
    return dbTeam

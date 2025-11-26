from fastapi import HTTPException, Depends
from pydantic import BaseModel
from Models.team import Team  
from Models.player import Player
from Models.match import Match
from database import get_db
from sqlalchemy.orm import Session
import pandas as pd

class MatchBase(BaseModel):
    date: str
    time: str
    round: str
    day: str
    venue: str
    result: str
    gf: int = 0
    ga: int = 0
    opponent: str
    xg: float = 0.00
    xga: float = 0.00
    poss: float = 0.00
    attendance: int = 0
    captain: str
    formation: str
    oppFormation: str
    referee: str
    team_name: str

# API call get request to get all matches
def readAllMatches (db:Session):
    matches = db.query(Match).all()
    if matches is None:
        raise HTTPException(status_code=404, detail="No matches found")
    return matches

# API call get request to get all matches for a team
async def readMatchesPerTeam(team_name: str, db:Session):
    matches = db.query(Match).filter(Match.team_name == team_name).all()
    if not matches:
        raise HTTPException(status_code=404, detail=f"No matches found for team: {team_name}")
    return matches

# Import league table from CSV and insert into database
async def importMatches(csv_path: str, db: Session):
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Clear existing data
        db.query(Match).delete()
        db.commit()

        # Insert each row into database
        for _, row in df.iterrows():
            tableEntry = Match(
                date=str(row.get('Date', '')),
                time=str(row.get('Time', '')),
                round=str(row.get('Round', '')),
                day=str(row.get('Day', '')),
                venue=str(row.get('Venue', '')),
                result=str(row.get('Result', '')),
                gf=int(row.get('GF', 0)) if pd.notna(row.get('GF', 0)) else 0,
                ga=int(row.get('GA', 0)) if pd.notna(row.get('GA', 0)) else 0,
                opponent=str(row.get('Opponent', '')),
                xg=float(row.get('xG', 0.00)) if pd.notna(row.get('xG', 0.00)) else 0.00,
                xga=float(row.get('xGA', 0.00)) if pd.notna(row.get('xGA', 0.00)) else 0.00,
                poss=float(row.get('Poss', 0.00)) if pd.notna(row.get('Poss', 0.00)) else 0.00,
                attendance=int(row.get('Attendance', 0)) if pd.notna(row.get('Attendance', 0)) else 0,
                captain=str(row.get('Captain', '')),
                formation=str(row.get('Formation', '')),
                oppFormation=str(row.get('Opp Formation', '')),
                referee=str(row.get('Referee', '')),
                team_name=str(row.get('Team', ''))
            )
            db.add(tableEntry)
        
        db.commit()
        return {"message": f"Successfully imported {len(df)} teams into database"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error importing table: {str(e)}")

# API call post request to add a match to the database
async def createMatch(match: MatchBase, db: Session):
    dbMatch = Match(
        date=match.date,
        time=match.time,
        round=match.round,
        day=match.day,
        venue=match.venue,
        result=match.result,
        gf=match.gf,
        ga=match.ga,
        opponent=match.opponent,
        xg=match.xg,
        xga=match.xga,
        poss=match.poss,
        attendance=match.attendance,
        captain=match.captain,
        formation=match.formation,
        oppFormation=match.oppFormation,
        referee=match.referee,
        team_name=match.team_name
    )
    db.add(dbMatch)
    db.commit()
    db.refresh(dbMatch)
    return dbMatch
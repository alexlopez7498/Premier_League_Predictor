from fastapi import HTTPException, Depends
from pydantic import BaseModel
from Models.team import Team  
from Models.player import Player
from Models.match import Match
from database import get_db
from sqlalchemy.orm import Session


class MatchBase(BaseModel):
    match_id: int
    date: str
    time: str
    round: str
    day: int
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
async def readAllMatches (db:Session):
    matches = db.query(Match).all()
    if matches is None:
        raise HTTPException(status_code=404, detail="No matches found")
    return matches

# API call get request to get all matches for a team
async def readMatchesPerTeam(db:Session):
    teams = db.query(Team).all()
    if teams is None:
        raise HTTPException(status_code=404, detail="Unable to rectreive teams")
    teamMatches = {}
    for team in teams:
        matches = db.query(Player).filter(Player.team_name == team.name).all()
        teamMatches[team.name] = matches
    return teamMatches

# API call post request to add a match to the database
async def create_match(match: MatchBase, db: Session):
    dbMatch = Match(
        match_id=match.match_id,
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
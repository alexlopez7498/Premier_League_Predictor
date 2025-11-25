from fastapi import HTTPException, Depends
from pydantic import BaseModel
from Models.team import Team  
from Models.player import Player
from database import get_db
from sqlalchemy.orm import Session

class PlayerBase(BaseModel):
    name: str
    nation: str
    position: str
    age: int
    matchesPlayed: int = 0
    starts: int = 0
    minutes: int = 0
    minutesPerMatch: float = 0.00
    goals: int = 0
    assists: int = 0
    goalsAndAssists: float = 0.00
    nonPenaltyGoals: int = 0
    penaltyGoals: int = 0
    penaltyAttempts: int = 0
    yellowCards: int = 0
    redCards: int = 0
    expectedGoals: float = 0.00
    expectedNonPenaltyGoals: float = 0.00
    expectedAssists: float = 0.00
    expectedNonPenaltyGoalsAndAssists: float = 0.00
    progressiveCarries: int = 0
    progessivePasses: int = 0
    progessivePassesReceived: int = 0
    goalsPer90: float = 0.00
    assistsPer90: float = 0.00
    goalsAndAssistsPer90: float = 0.00
    nonPenaltyGoalsPer90: float = 0.00
    nonPenaltyGoalsAndAssistsPer90: float = 0.00
    expectedGoalsPer90: float = 0.00
    expectedAssistsPer90: float = 0.00
    expectedGoalsAndAssistsPer90: float = 0.00
    expectedNonPenaltyGoalsPer90: float = 0.00
    expectedNonPenaltyGoalsAndAssistsPer90: float = 0.00
    team_name: str

# API call get request to get all players in the premier league
def readAllPlayers(db: Session):
    players = db.query(Player).all()
    if players is None:
        raise HTTPException(status_code=404, detail="No players found")
    return players

# API call get request to get all players from a specific team
async def readPlayersPerTeam(team_name: str, db: Session):
    players = db.query(Player).filter(Player.team_name == team_name).all()
    if not players:
        raise HTTPException(status_code=404, detail=f"No players found for team: {team_name}")
    return players

# API call post request to add a player to the database
async def create_player(player: PlayerBase, db: Session):
    dbPlayer = Player(
        name=player.name,
        nation=player.nation,
        position=player.position,
        age=player.age,
        matchesPlayed=player.matchesPlayed,
        starts=player.starts,
        minutes=player.minutes,
        minutesPerMatch=player.minutesPerMatch,
        goals=player.goals,
        assists=player.assists,
        goalsAndAssists=player.goalsAndAssists,
        nonPenaltyGoals=player.nonPenaltyGoals,
        penaltyGoals=player.penaltyGoals,
        penaltyAttempts=player.penaltyAttempts,
        yellowCards=player.yellowCards,
        redCards=player.redCards,
        expectedGoals=player.expectedGoals,
        expectedNonPenaltyGoals=player.expectedNonPenaltyGoals,
        expectedAssists=player.expectedAssists,
        expectedNonPenaltyGoalsAndAssists=player.expectedNonPenaltyGoalsAndAssists,
        progressiveCarries=player.progressiveCarries,
        progessivePasses=player.progessivePasses,
        progessivePassesReceived=player.progessivePassesReceived,
        goalsPer90=player.goalsPer90,
        assistsPer90=player.assistsPer90,
        goalsAndAssistsPer90=player.goalsAndAssistsPer90,
        nonPenaltyGoalsPer90=player.nonPenaltyGoalsPer90,
        nonPenaltyGoalsAndAssistsPer90=player.nonPenaltyGoalsAndAssistsPer90,
        expectedGoalsPer90=player.expectedGoalsPer90,
        expectedAssistsPer90=player.expectedAssistsPer90,
        expectedGoalsAndAssistsPer90=player.expectedGoalsAndAssistsPer90,
        expectedNonPenaltyGoalsPer90=player.expectedNonPenaltyGoalsPer90,
        expectedNonPenaltyGoalsAndAssistsPer90=player.expectedNonPenaltyGoalsAndAssistsPer90,

        team_name=player.team_name
    )
    db.add(dbPlayer)
    db.commit()
    db.refresh(dbPlayer)
    return dbPlayer
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from Models.team import Team  
from Models.player import Player
from database import get_db
from sqlalchemy.orm import Session
import pandas as pd

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

# Import league table from CSV and insert into database
async def importPlayers(csv_path: str, db: Session):
    try:
        df = pd.read_csv(csv_path)
        
        # Clear existing data
        db.query(Player).delete()
        db.commit()

        # Insert each row into database
        for _, row in df.iterrows():
            age_raw = str(row.get('Age', "0"))
            tableEntry = Player(
                name=str(row.get('Player', '')),
                nation=str(row.get('Nation', '')),
                position=str(row.get('Pos', '')),
                age = float(age_raw.split("-")[0] if age_raw and age_raw[0].isdigit() else 0),
                matchesPlayed= int(row.get('MP', 0)) if pd.notna(row.get('MP', 0)) else 0,
                starts= int(row.get('Starts', 0)) if pd.notna(row.get('Starts', 0)) else 0,
                minutes = int(float(row.get('Min', 0))) if pd.notna(row.get('Min', None)) else 0,
                minutesPerMatch=float(row.get('90s', 0.00)) if pd.notna(row.get('90s', 0.00)) else 0.00,
                goals=int(float(row.get('Gls', 0))) if pd.notna(row.get('Gls', 0)) else 0,
                assists=int(float(row.get('Ast', 0))) if pd.notna(row.get('Ast', 0)) else 0,
                goalsAndAssists=float(row.get('G+A', 0.00)) if pd.notna(row.get('G+A', 0.00)) else 0.00,
                nonPenaltyGoals=int(float(row.get('G-PK', 0))) if pd.notna(row.get('G-PK', 0)) else 0,
                penaltyGoals=int(float(row.get('PK', 0))) if pd.notna(row.get('PK', 0)) else 0,
                penaltyAttempts=int(float(row.get('PKatt', 0))) if pd.notna(row.get('PKatt', 0)) else 0,
                yellowCards=int(float(row.get('CrdY', 0))) if pd.notna(row.get('CrdY', 0)) else 0,
                redCards=int(float(row.get('CrdR', 0))) if pd.notna(row.get('CrdR', 0)) else 0,
                expectedGoals=float(row.get('xG', 0.00)) if pd.notna(row.get('xG', 0.00)) else 0.00,
                expectedNonPenaltyGoals=float(row.get('npxG', 0.00)) if pd.notna(row.get('npxG', 0.00)) else 0.00,
                expectedAssists=float(row.get('xAG', 0.00)) if pd.notna(row.get('xAG', 0.00)) else 0.00,
                expectedNonPenaltyGoalsAndAssists=float(row.get('npxG+xAG', 0.00)) if pd.notna(row.get('npxG+xAG', 0.00)) else 0.00,
                progressiveCarries=int(float(row.get('PrgC', 0))) if pd.notna(row.get('PrgC', 0)) else 0,
                progessivePasses=int(float(row.get('PrgP', 0))) if pd.notna(row.get('PrgP', 0)) else 0,
                progessivePassesReceived=int(float(row.get('PrgR', 0))) if pd.notna(row.get('PrgR', 0)) else 0,
                goalsPer90=float(row.get('Gls', 0.00)) if pd.notna(row.get('Gls', 0.00)) else 0.00,
                assistsPer90=float(row.get('Ast', 0.00)) if pd.notna(row.get('Ast', 0.00)) else 0.00,
                goalsAndAssistsPer90=float(row.get('G+A', 0.00)) if pd.notna(row.get('G+A', 0.00)) else 0.00,
                nonPenaltyGoalsPer90=float(row.get('G-PK', 0.00)) if pd.notna(row.get('G-PK', 0.00)) else 0.00,
                nonPenaltyGoalsAndAssistsPer90=float(row.get('G+A-PK', 0.00)) if pd.notna(row.get('G+A-PK', 0.00)) else 0.00,
                expectedGoalsPer90=float(row.get('xG', 0.00)) if pd.notna(row.get('xG', 0.00)) else 0.00,
                expectedAssistsPer90=float(row.get('xAG', 0.00)) if pd.notna(row.get('xAG', 0.00)) else 0.00,
                expectedGoalsAndAssistsPer90=float(row.get('xG+xAG', 0.00)) if pd.notna(row.get('xG+xAG', 0.00)) else 0.00,
                expectedNonPenaltyGoalsPer90=float(row.get('npxG', 0.00)) if pd.notna(row.get('npxG', 0.00)) else 0.00,
                expectedNonPenaltyGoalsAndAssistsPer90=float(row.get('npxG+xAG', 0.00)) if pd.notna(row.get('npxG+xAG', 0.00)) else 0.00,
                team_name=str(row.get('Team', ''))
            )
            db.add(tableEntry)
        
        db.commit()
        return {"message": f"Successfully imported {len(df)} players into database"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error importing table: {str(e)}")

# API call post request to add a player to the database
async def createPlayer(player: PlayerBase, db: Session):
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
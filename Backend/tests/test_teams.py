"""
Unit tests for Team endpoints and controllers.
"""
import pytest
from fastapi import status


def test_create_team(client):
    """Test creating a new team via POST /teams/"""
    team_data = {
        "rank": 1,
        "name": "Arsenal",
        "matchesPlayed": 10,
        "wins": 7,
        "draws": 2,
        "losses": 1,
        "goalsFor": 20,
        "goalsAgainst": 10,
        "goalDifference": 10,
        "points": 23,
        "goalsPer90": 2.0,
        "expectedGoals": 18.5,
        "expectedGoalsAllowed": 12.0,
        "expectedGoalsDifference": 6.5,
        "expectedGoalsPerGame": 1.85,
        "expectedGoalsDifferencePer90": 0.65,
        "last5Wins": "WWWDW",
        "attendance": 60000,
        "topTeamScorer": "Bukayo Saka",
        "goalkeeper": "Aaron Ramsdale"
    }
    response = client.post("/teams/", json=team_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Arsenal"
    assert data["rank"] == 1
    assert data["points"] == 23


def test_read_all_teams(client):
    """Test reading all teams via GET /teams/"""
    # First create a team
    team_data = {
        "rank": 1,
        "name": "Manchester City",
        "matchesPlayed": 10,
        "wins": 8,
        "draws": 1,
        "losses": 1,
        "goalsFor": 25,
        "goalsAgainst": 8,
        "goalDifference": 17,
        "points": 25
    }
    client.post("/teams/", json=team_data)
    
    # Then read all teams
    response = client.get("/teams/")
    assert response.status_code == status.HTTP_200_OK
    teams = response.json()
    assert isinstance(teams, list)
    assert len(teams) > 0
    assert any(team["name"] == "Manchester City" for team in teams)

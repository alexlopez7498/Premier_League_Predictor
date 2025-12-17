"""
Unit tests for Match endpoints and controllers.
"""
import pytest
from fastapi import status


def test_create_match(client):
    """Test creating a new match via POST /matches/"""
    match_data = {
        "date": "2025-01-15",
        "time": "15:00",
        "round": "Matchweek 1",
        "day": "Saturday",
        "venue": "Home",
        "result": "W",
        "gf": 2,
        "ga": 1,
        "opponent": "Chelsea",
        "team_name": "Arsenal",
        "xg": 1.8,
        "xga": 1.2,
        "poss": 55.0,
        "attendance": 60000,
        "captain": "Martin Odegaard",
        "formation": "4-3-3",
        "oppFormation": "4-2-3-1",
        "referee": "Michael Oliver"
    }
    response = client.post("/matches/", json=match_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["team_name"] == "Arsenal"
    assert data["opponent"] == "Chelsea"
    assert data["gf"] == 2
    assert data["ga"] == 1


def test_read_matches_by_team(client):
    """Test reading matches for a specific team via GET /matches/team/{team_name}"""
    # First create a match
    match_data = {
        "date": "2025-01-15",
        "time": "15:00",
        "round": "Matchweek 1",
        "day": "Saturday",
        "venue": "Home",
        "result": "W",
        "gf": 3,
        "ga": 0,
        "opponent": "Tottenham",
        "team_name": "Arsenal",
        "xg": 2.5,
        "xga": 0.8,
        "poss": 60.0,
        "attendance": 60000,
        "captain": "Martin Odegaard",
        "formation": "4-3-3",
        "oppFormation": "4-4-2",
        "referee": "Anthony Taylor"
    }
    client.post("/matches/", json=match_data)
    
    # Then get matches for Arsenal
    response = client.get("/matches/team/Arsenal")
    assert response.status_code == status.HTTP_200_OK
    matches = response.json()
    assert isinstance(matches, list)
    assert len(matches) > 0
    assert all(match["team_name"] == "Arsenal" for match in matches)

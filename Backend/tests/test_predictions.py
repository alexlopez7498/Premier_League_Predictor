"""
Unit tests for Prediction endpoints and controllers.
"""
import pytest
from fastapi import status


def test_predict_match_validation(client):
    """Test prediction endpoint validates required fields"""
    # Test with missing required fields
    incomplete_match_data = {
        "date": "2025-01-15",
        "time": "15:00"
    }
    response = client.post("/predict/", json=incomplete_match_data)
    if response.status_code == 405:
        response = client.post("/predict", json=incomplete_match_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_all_predictions(client):
    """Test reading all predictions via GET /predictions/"""
    response = client.get("/predictions/")
    assert response.status_code == status.HTTP_200_OK
    predictions = response.json()
    assert isinstance(predictions, list)

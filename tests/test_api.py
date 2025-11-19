import pytest

def test_get_earthquake_by_id(override_dependency, api_mock_repository, mock_earthquake, client):
    # Setup
    api_mock_repository.get_by_id.return_value = mock_earthquake
    
    # Execute
    response = client.get("/api/v1/earthquakes/test_id")
    
    # Verify
    assert response.status_code == 200
    assert response.json()["id"] == "test_id"

def test_get_earthquake_not_found(override_dependency, api_mock_repository, client):
    api_mock_repository.get_by_id.return_value = None
    response = client.get("/api/v1/earthquakes/nonexistent")
    assert response.status_code == 404

def test_list_earthquakes(override_dependency, api_mock_repository, mock_earthquake, client):
    # Setup
    api_mock_repository.get_filtered.return_value = ([mock_earthquake], 1)
    
    # Execute
    response = client.get("/api/v1/earthquakes?page=1&limit=10")
    
    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["earthquakes"]) == 1
    assert data["page"] == 1
    assert data["limit"] == 10

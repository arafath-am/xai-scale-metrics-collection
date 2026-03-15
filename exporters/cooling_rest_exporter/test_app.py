#!/usr/bin/env python3
"""
Unit tests for cooling_rest_exporter.

Run with: python -m pytest test_app.py
"""
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock

# Mock environment before importing app
import os
os.environ["COOLING_JSON_FILE"] = "/tmp/test_payload.json"

from app import fetch_data, update_gauges, app as flask_app

@pytest.fixture
def mock_payload():
    return {
        "units": {
            "CRAC-01": {
                "supply_air_temp_c": 18.5,
                "return_air_temp_c": 28.3,
                "fan_rpm": 1450,
                "alarm": 0
            },
            "CRAC-02": {
                "supply_air_temp_c": 19.2,
                "return_air_temp_c": 27.8,
                "fan_rpm": 1425,
                "alarm": 1
            }
        }
    }

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

class TestFetchData:
    
    def test_fetch_from_file(self, mock_payload):
        mock_file_content = json.dumps(mock_payload)
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            data = fetch_data()
            assert data == mock_payload
    
    @patch.dict(os.environ, {"COOLING_API_URL": "http://test.local/api"})
    @patch("requests.get")
    def test_fetch_from_http(self, mock_get, mock_payload):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_payload
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        data = fetch_data()
        assert data == mock_payload
        mock_get.assert_called_once()
    
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_fetch_file_not_found(self, mock_file):
        with pytest.raises(FileNotFoundError):
            fetch_data()

class TestUpdateGauges:
    
    def test_update_valid_payload(self, mock_payload):
        # Should not raise any exceptions
        update_gauges(mock_payload)
    
    def test_update_empty_units(self):
        # Should handle missing 'units' key
        update_gauges({})
    
    def test_update_malformed_data(self):
        # Should skip units with invalid data types
        payload = {
            "units": {
                "BAD-01": {
                    "supply_air_temp_c": "not_a_number"
                }
            }
        }
        # Should not crash
        update_gauges(payload)

class TestEndpoints:
    
    def test_metrics_endpoint(self, client):
        response = client.get('/metrics')
        assert response.status_code == 200
        assert b'cooling_supply_air_temp_celsius' in response.data
    
    def test_healthz_endpoint(self, client):
        response = client.get('/healthz')
        assert response.status_code in [200, 503]
        data = response.get_json()
        assert 'healthy' in data
        assert 'staleness_seconds' in data

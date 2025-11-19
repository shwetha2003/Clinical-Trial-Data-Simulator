import pytest
import json
from unittest.mock import patch, MagicMock

class TestAPI:
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "timestamp" in data
    
    @patch('api.app.patient_simulator.generate_patient_dataset')
    def test_generate_patients(self, mock_generate, client):
        """Test patient generation endpoint"""
        # Mock the patient generation
        mock_generate.return_value = [{
            'patient_id': 'TEST123',
            'age': 45,
            'gender': 'Male',
            'condition': 'Hypertension'
        }]
        
        response = client.post("/generate-patients?num_patients=10")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "patients" in data
    
    def test_design_trial(self, client):
        """Test trial design endpoint"""
        trial_data = {
            "design": "parallel",
            "alpha": 0.05,
            "power": 0.8,
            "effect_size": 0.5,
            "duration_weeks": 12
        }
        
        response = client.post("/design-trial", json=trial_data)
        assert response.status_code == 200
        data = response.json()
        assert "trial_id" in data
        assert "design_type" in data
        assert "sample_size" in data
    
    def test_get_patients(self, client):
        """Test patients retrieval endpoint"""
        response = client.get("/patients?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "patients" in data
        assert "pagination" in data
    
    def test_analytics_summary(self, client):
        """Test analytics summary endpoint"""
        response = client.get("/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "distributions" in data
    
    def test_validate_data(self, client):
        """Test data validation endpoint"""
        response = client.post("/validate-data")
        assert response.status_code == 200
        data = response.json()
        assert "validation_results" in data
        assert "quality_metrics" in data
    
    def test_export_patients(self, client):
        """Test patient export endpoint"""
        response = client.get("/export/patients/csv")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "filename" in data
    
    def test_invalid_endpoint(self, client):
        """Test invalid endpoint handling"""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404
    
    def test_generate_patients_invalid_parameter(self, client):
        """Test patient generation with invalid parameters"""
        response = client.post("/generate-patients?num_patients=0")
        assert response.status_code == 200  # Should handle gracefully

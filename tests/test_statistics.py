import pytest
import numpy as np
from scipy import stats

class TestStatistics:
    
    def test_ttest_endpoint(self, client):
        """Test t-test endpoint"""
        test_data = {
            "data": [1.2, 1.5, 1.8, 1.3, 1.6, 1.4, 1.7, 1.9, 1.1, 1.5],
            "reference_value": 1.0,
            "alpha": 0.05
        }
        
        response = client.post("/statistics/t-test", json=test_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "test_type" in data
        assert "t_statistic" in data
        assert "p_value" in data
        assert "significant" in data
        assert "sample_size" in data
        
        # Verify statistical properties
        assert data['sample_size'] == len(test_data['data'])
        assert 0 <= data['p_value'] <= 1
    
    def test_anova_endpoint(self, client):
        """Test ANOVA endpoint"""
        anova_data = {
            "group1": [1.2, 1.5, 1.8, 1.3, 1.6],
            "group2": [2.1, 2.4, 2.7, 2.2, 2.5],
            "group3": [1.8, 2.1, 2.4, 1.9, 2.2]
        }
        
        response = client.post("/statistics/anova", json=anova_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "test_type" in data
        assert "f_statistic" in data
        assert "p_value" in data
        assert "groups" in data
        assert "group_means" in data
        
        # Check group means calculation
        for group, mean in data['group_means'].items():
            expected_mean = np.mean(anova_data[group])
            assert abs(mean - expected_mean) < 0.001
    
    def test_correlation_endpoint(self, client):
        """Test correlation endpoint"""
        correlation_data = {
            "x_data": [1, 2, 3, 4, 5],
            "y_data": [2, 4, 6, 8, 10]  # Perfect correlation
        }
        
        response = client.post("/statistics/correlation", json=correlation_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "test_type" in data
        assert "correlation" in data
        assert "p_value" in data
        assert "sample_size" in data
        assert "interpretation" in data
        
        # Perfect correlation should be close to 1
        assert abs(data['correlation'] - 1.0) < 0.001
        assert data['interpretation'] == "Very strong"
    
    def test_correlation_unequal_arrays(self, client):
        """Test correlation with unequal arrays"""
        correlation_data = {
            "x_data": [1, 2, 3],
            "y_data": [2, 4]  # Different lengths
        }
        
        response = client.post("/statistics/correlation", json=correlation_data)
        assert response.status_code == 400  # Should return bad request
    
    def test_efficacy_by_condition(self, client):
        """Test efficacy by condition endpoint"""
        response = client.get("/analytics/efficacy-by-condition")
        assert response.status_code == 200
        data = response.json()
        
        # Should return analysis for different conditions
        assert len(data) > 0
        
        for condition, analysis in data.items():
            assert "mean_efficacy" in analysis
            assert "std_efficacy" in analysis
            assert "sample_size" in analysis
            assert "good_response_rate" in analysis
            
            # Check value ranges
            assert 0 <= analysis['mean_efficacy'] <= 1
            assert 0 <= analysis['good_response_rate'] <= 100
    
    def test_safety_profile(self, client):
        """Test safety profile endpoint"""
        response = client.get("/analytics/safety-profile")
        assert response.status_code == 200
        data = response.json()
        
        assert "adverse_events" in data
        assert "summary" in data
        assert "most_common_events" in data
        
        # Check summary structure
        summary = data['summary']
        assert "total_patients" in summary
        assert "patients_with_events" in summary
        assert "total_events" in summary
        assert "event_rate_per_patient" in summary

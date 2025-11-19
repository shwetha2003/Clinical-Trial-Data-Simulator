import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.app import app
from data_generator.patient_simulator import PatientSimulator
from data_generator.trial_designer import TrialDesigner
from data_generator.data_validator import DataValidator

@pytest.fixture
def client():
    """Test client for FastAPI"""
    return TestClient(app)

@pytest.fixture
def patient_simulator():
    """Patient simulator instance"""
    return PatientSimulator()

@pytest.fixture
def trial_designer():
    """Trial designer instance"""
    return TrialDesigner()

@pytest.fixture
def data_validator():
    """Data validator instance"""
    return DataValidator()

@pytest.fixture
def sample_patient_data():
    """Sample valid patient data for testing"""
    return {
        'patient_id': 'TEST123',
        'age': 45,
        'gender': 'Male',
        'weight': 75.5,
        'height': 175.0,
        'bmi': 24.7,
        'condition': 'Hypertension',
        'lab_results': [
            {
                'test_name': 'WBC',
                'test_value': 6.5,
                'normal_min': 4.5,
                'normal_max': 11.0,
                'unit': '10^3/μL',
                'is_abnormal': False
            }
        ]
    }

@pytest.fixture
def sample_trial_params():
    """Sample trial parameters for testing"""
    return {
        'design': 'parallel',
        'alpha': 0.05,
        'power': 0.8,
        'effect_size': 0.5,
        'duration_weeks': 12
    }

import pytest
import numpy as np
from datetime import datetime

class TestPatientSimulator:
    
    def test_generate_demographics(self, patient_simulator):
        """Test demographic data generation"""
        demographics = patient_simulator.generate_demographics()
        
        # Check required fields
        assert 'patient_id' in demographics
        assert 'age' in demographics
        assert 'gender' in demographics
        assert 'weight' in demographics
        assert 'height' in demographics
        assert 'bmi' in demographics
        assert 'condition' in demographics
        
        # Check data types and ranges
        assert 18 <= demographics['age'] <= 85
        assert demographics['gender'] in ['Male', 'Female', 'Other']
        assert 30 <= demographics['weight'] <= 200
        assert 140 <= demographics['height'] <= 210
        assert 15 <= demographics['bmi'] <= 50
        assert demographics['condition'] in patient_simulator.conditions
    
    def test_generate_lab_results(self, patient_simulator):
        """Test lab results generation"""
        patient_data = {
            'condition': 'Hypertension',
            'age': 45
        }
        
        lab_results = patient_simulator.generate_lab_results(patient_data)
        
        assert len(lab_results) > 0
        
        for lab in lab_results:
            # Check required fields
            assert 'test_name' in lab
            assert 'test_value' in lab
            assert 'normal_min' in lab
            assert 'normal_max' in lab
            assert 'unit' in lab
            assert 'is_abnormal' in lab
            
            # Check value ranges
            assert lab['normal_min'] < lab['normal_max']
            assert lab['test_value'] >= 0
    
    def test_simulate_treatment_response(self, patient_simulator):
        """Test treatment response simulation"""
        patient_data = {
            'age': 45,
            'bmi': 24.7,
            'condition': 'Hypertension'
        }
        
        response = patient_simulator.simulate_treatment_response(patient_data, 'Lisinopril')
        
        assert 'treatment' in response
        assert 'efficacy_score' in response
        assert 'response_category' in response
        assert 'side_effects' in response
        assert 'treatment_duration_days' in response
        
        # Check efficacy score range
        assert 0.1 <= response['efficacy_score'] <= 0.95
        assert response['response_category'] in ['Poor', 'Moderate', 'Good']
        assert 30 <= response['treatment_duration_days'] <= 180
    
    def test_generate_patient_dataset(self, patient_simulator):
        """Test complete patient dataset generation"""
        dataset = patient_simulator.generate_patient_dataset(10)
        
        assert len(dataset) == 10
        
        for patient in dataset:
            # Check structure
            assert 'patient_id' in patient
            assert 'lab_results' in patient
            assert 'treatment_response' in patient
            assert 'adverse_events' in patient
            
            # Check lab results
            assert len(patient['lab_results']) >= 5
    
    def test_adverse_events_generation(self, patient_simulator):
        """Test adverse events generation"""
        patient_data = {
            'age': 70,  # Higher age for increased risk
            'condition': 'Hypertension'
        }
        
        events = patient_simulator.generate_adverse_events(patient_data, 'Lisinopril')
        
        # Events should be a list
        assert isinstance(events, list)
        
        for event in events:
            assert 'event_type' in event
            assert 'severity' in event
            assert 'description' in event
            assert 'resolved' in event
            assert event['severity'] in ['Mild', 'Moderate', 'Severe']
    
    def test_export_functionality(self, patient_simulator, tmp_path):
        """Test data export functionality"""
        dataset = patient_simulator.generate_patient_dataset(5)
        
        # Test CSV export
        csv_file = tmp_path / "test_patients.csv"
        patient_simulator.export_to_csv(dataset, str(csv_file))
        assert csv_file.exists()
        
        # Test JSON export
        json_file = tmp_path / "test_patients.json"
        patient_simulator.export_to_json(dataset, str(json_file))
        assert json_file.exists()

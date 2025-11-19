import pytest
import numpy as np

class TestDataValidator:
    
    def test_validate_patient_data_valid(self, data_validator, sample_patient_data):
        """Test validation of valid patient data"""
        is_valid, errors = data_validator.validate_patient_data(sample_patient_data)
        
        assert is_valid == True
        assert len(errors) == 0
    
    def test_validate_patient_data_missing_field(self, data_validator):
        """Test validation with missing required field"""
        invalid_data = {
            'patient_id': 'TEST123',
            'age': 45,
            # Missing gender, weight, height, bmi, condition
        }
        
        is_valid, errors = data_validator.validate_patient_data(invalid_data)
        
        assert is_valid == False
        assert len(errors) > 0
        assert any('Missing required field' in error for error in errors)
    
    def test_validate_patient_data_out_of_range(self, data_validator):
        """Test validation with out-of-range values"""
        invalid_data = {
            'patient_id': 'TEST123',
            'age': 15,  # Below minimum
            'gender': 'Male',
            'weight': 250,  # Above maximum
            'height': 130,  # Below minimum
            'bmi': 60,  # Above maximum
            'condition': 'Hypertension'
        }
        
        is_valid, errors = data_validator.validate_patient_data(invalid_data)
        
        assert is_valid == False
        assert len(errors) > 0
        assert any('out of range' in error for error in errors)
    
    def test_validate_lab_results(self, data_validator):
        """Test lab results validation"""
        valid_labs = [
            {
                'test_name': 'WBC',
                'test_value': 6.5,
                'normal_min': 4.5,
                'normal_max': 11.0,
                'unit': '10^3/μL',
                'is_abnormal': False
            }
        ]
        
        errors = data_validator._validate_lab_results(valid_labs)
        assert len(errors) == 0
        
        # Test invalid lab (min >= max)
        invalid_labs = [
            {
                'test_name': 'WBC',
                'test_value': 6.5,
                'normal_min': 11.0,  # Greater than max
                'normal_max': 4.5,
                'unit': '10^3/μL',
                'is_abnormal': False
            }
        ]
        
        errors = data_validator._validate_lab_results(invalid_labs)
        assert len(errors) > 0
        assert any('Invalid normal range' in error for error in errors)
    
    def test_validate_dataset(self, data_validator, sample_patient_data):
        """Test dataset validation"""
        dataset = [sample_patient_data] * 5  # Create multiple copies
        
        results = data_validator.validate_dataset(dataset)
        
        assert 'total_patients' in results
        assert 'valid_patients' in results
        assert 'invalid_patients' in results
        assert 'errors' in results
        assert 'summary_stats' in results
        
        assert results['total_patients'] == 5
        assert results['valid_patients'] == 5
        assert results['invalid_patients'] == 0
    
    def test_check_data_quality(self, data_validator, sample_patient_data):
        """Test data quality metrics calculation"""
        dataset = [sample_patient_data] * 10
        
        quality_metrics = data_validator.check_data_quality(dataset)
        
        assert 'completeness_score' in quality_metrics
        assert 'validity_score' in quality_metrics
        assert 'overall_quality_score' in quality_metrics
        
        # All scores should be between 0 and 100
        for score in quality_metrics.values():
            assert 0 <= score <= 100
        
        # With valid data, scores should be high
        assert quality_metrics['overall_quality_score'] > 90
    
    def test_condition_distribution(self, data_validator, sample_patient_data):
        """Test condition distribution calculation"""
        dataset = [
            {**sample_patient_data, 'condition': 'Hypertension'},
            {**sample_patient_data, 'condition': 'Diabetes Type 2'},
            {**sample_patient_data, 'condition': 'Hypertension'}
        ]
        
        distribution = data_validator._get_condition_distribution(dataset)
        
        assert distribution['Hypertension'] == 2
        assert distribution['Diabetes Type 2'] == 1

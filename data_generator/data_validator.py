import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple

class DataValidator:
    def __init__(self):
        self.validation_rules = {
            'age': {'min': 18, 'max': 100, 'required': True},
            'weight': {'min': 30, 'max': 200, 'required': True},
            'height': {'min': 140, 'max': 210, 'required': True},
            'bmi': {'min': 15, 'max': 50, 'required': True},
            'lab_results': {'required': True, 'min_tests': 5}
        }
    
    def validate_patient_data(self, patient_data: Dict) -> Tuple[bool, List[str]]:
        """Validate individual patient data"""
        errors = []
        
        # Check required fields
        for field, rules in self.validation_rules.items():
            if rules['required'] and field not in patient_data:
                errors.append(f"Missing required field: {field}")
            elif field in patient_data and field != 'lab_results':
                value = patient_data[field]
                if value < rules['min'] or value > rules['max']:
                    errors.append(f"{field} out of range: {value}")
        
        # Validate lab results
        if 'lab_results' in patient_data:
            lab_errors = self._validate_lab_results(patient_data['lab_results'])
            errors.extend(lab_errors)
        
        return len(errors) == 0, errors
    
    def _validate_lab_results(self, lab_results: List[Dict]) -> List[str]:
        """Validate laboratory results"""
        errors = []
        
        if len(lab_results) < self.validation_rules['lab_results']['min_tests']:
            errors.append(f"Insufficient lab tests: {len(lab_results)}")
        
        required_lab_fields = ['test_name', 'test_value', 'normal_min', 'normal_max', 'unit']
        for i, lab in enumerate(lab_results):
            for field in required_lab_fields:
                if field not in lab:
                    errors.append(f"Lab result {i} missing field: {field}")
            
            if 'test_value' in lab and 'normal_min' in lab and 'normal_max' in lab:
                value = lab['test_value']
                min_val = lab['normal_min']
                max_val = lab['normal_max']
                if value < 0:
                    errors.append(f"Lab value cannot be negative: {value}")
                if min_val >= max_val:
                    errors.append(f"Invalid normal range: {min_val}-{max_val}")
        
        return errors
    
    def validate_dataset(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Validate entire dataset"""
        validation_results = {
            'total_patients': len(dataset),
            'valid_patients': 0,
            'invalid_patients': 0,
            'errors': [],
            'summary_stats': {}
        }
        
        for i, patient in enumerate(dataset):
            is_valid, errors = self.validate_patient_data(patient)
            if is_valid:
                validation_results['valid_patients'] += 1
            else:
                validation_results['invalid_patients'] += 1
                validation_results['errors'].append({
                    'patient_index': i,
                    'patient_id': patient.get('patient_id', 'Unknown'),
                    'errors': errors
                })
        
        # Calculate summary statistics
        if dataset:
            ages = [p.get('age', 0) for p in dataset if p.get('age')]
            bmis = [p.get('bmi', 0) for p in dataset if p.get('bmi')]
            
            validation_results['summary_stats'] = {
                'mean_age': round(np.mean(ages), 1) if ages else 0,
                'mean_bmi': round(np.mean(bmis), 1) if bmis else 0,
                'age_range': f"{min(ages)}-{max(ages)}" if ages else "N/A",
                'condition_distribution': self._get_condition_distribution(dataset)
            }
        
        return validation_results
    
    def _get_condition_distribution(self, dataset: List[Dict]) -> Dict[str, int]:
        """Get distribution of medical conditions"""
        distribution = {}
        for patient in dataset:
            condition = patient.get('condition', 'Unknown')
            distribution[condition] = distribution.get(condition, 0) + 1
        return distribution
    
    def check_data_quality(self, dataset: List[Dict]) -> Dict[str, float]:
        """Calculate data quality metrics"""
        total_fields = 0
        missing_fields = 0
        valid_ranges = 0
        total_range_checks = 0
        
        for patient in dataset:
            for field, rules in self.validation_rules.items():
                if field != 'lab_results':
                    total_fields += 1
                    if field not in patient:
                        missing_fields += 1
                    else:
                        total_range_checks += 1
                        value = patient[field]
                        if rules['min'] <= value <= rules['max']:
                            valid_ranges += 1
        
        completeness = 1 - (missing_fields / total_fields) if total_fields > 0 else 0
        validity = valid_ranges / total_range_checks if total_range_checks > 0 else 0
        
        return {
            'completeness_score': round(completeness * 100, 2),
            'validity_score': round(validity * 100, 2),
            'overall_quality_score': round((completeness + validity) / 2 * 100, 2)
        }

import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import numpy as np

class PatientSimulator:
    def __init__(self):
        self.conditions = [
            "Hypertension", "Diabetes Type 2", "Asthma", "COPD", 
            "Rheumatoid Arthritis", "Osteoporosis", "Migraine"
        ]
        self.treatments = {
            "Hypertension": ["Lisinopril", "Amlodipine", "Metoprolol"],
            "Diabetes Type 2": ["Metformin", "Insulin", "Glipizide"],
            "Asthma": ["Albuterol", "Fluticasone", "Montelukast"],
            "COPD": ["Tiotropium", "Salmeterol", "Prednisone"],
            "Rheumatoid Arthritis": ["Methotrexate", "Adalimumab", "Etanercept"],
            "Osteoporosis": ["Alendronate", "Risedronate", "Zoledronic Acid"],
            "Migraine": ["Sumatriptan", "Rizatriptan", "Propranolol"]
        }
        
    def generate_demographics(self) -> Dict[str, Any]:
        """Generate realistic patient demographics"""
        gender = random.choice(['Male', 'Female'])
        age = random.randint(18, 85)
        
        # Weight and height based on gender and age
        if gender == 'Male':
            weight = round(random.uniform(60, 120), 1)
            height = round(random.uniform(160, 190), 1)
        else:
            weight = round(random.uniform(45, 90), 1)
            height = round(random.uniform(150, 175), 1)
            
        bmi = round(weight / ((height/100) ** 2), 1)
        
        return {
            'patient_id': str(uuid.uuid4())[:8],
            'age': age,
            'gender': gender,
            'weight': weight,
            'height': height,
            'bmi': bmi,
            'condition': random.choice(self.conditions)
        }
    
    def generate_lab_results(self, patient_data: Dict) -> List[Dict]:
        """Generate lab results with normal/abnormal ranges"""
        condition = patient_data['condition']
        age = patient_data['age']
        
        labs = []
        
        # Common lab tests with normal ranges
        lab_tests = [
            {
                'name': 'WBC', 'unit': '10^3/μL', 
                'normal_min': 4.5, 'normal_max': 11.0,
                'condition_effect': 0.1
            },
            {
                'name': 'Hemoglobin', 'unit': 'g/dL',
                'normal_min': 12.0, 'normal_max': 16.0,
                'condition_effect': -0.2
            },
            {
                'name': 'Platelets', 'unit': '10^3/μL',
                'normal_min': 150, 'normal_max': 450,
                'condition_effect': 0.05
            },
            {
                'name': 'Sodium', 'unit': 'mmol/L',
                'normal_min': 135, 'normal_max': 145,
                'condition_effect': -0.1
            },
            {
                'name': 'Potassium', 'unit': 'mmol/L',
                'normal_min': 3.5, 'normal_max': 5.2,
                'condition_effect': 0.05
            },
            {
                'name': 'Creatinine', 'unit': 'mg/dL',
                'normal_min': 0.6, 'normal_max': 1.3,
                'condition_effect': 0.3
            },
            {
                'name': 'ALT', 'unit': 'U/L',
                'normal_min': 7, 'normal_max': 56,
                'condition_effect': 0.4
            }
        ]
        
        for test in lab_tests:
            base_value = random.uniform(test['normal_min'], test['normal_max'])
            
            # Apply condition-specific effects
            if random.random() < 0.3:  # 30% chance of abnormality
                effect = test['condition_effect']
                if effect > 0:
                    value = base_value * (1 + random.uniform(0.1, 0.5))
                else:
                    value = base_value * (1 - random.uniform(0.1, 0.3))
            else:
                value = base_value
                
            is_abnormal = not (test['normal_min'] <= value <= test['normal_max'])
            
            labs.append({
                'test_name': test['name'],
                'test_value': round(value, 2),
                'normal_min': test['normal_min'],
                'normal_max': test['normal_max'],
                'unit': test['unit'],
                'is_abnormal': is_abnormal,
                'test_date': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            })
            
        return labs
    
    def simulate_treatment_response(self, patient_data: Dict, treatment: str) -> Dict[str, Any]:
        """Simulate patient response to treatment"""
        base_efficacy = random.uniform(0.3, 0.9)
        
        # Adjust efficacy based on age and condition
        age_factor = 1.0 - (patient_data['age'] - 40) * 0.005  # Slight decrease with age
        bmi_factor = 1.1 if patient_data['bmi'] < 25 else 0.9
        
        final_efficacy = base_efficacy * age_factor * bmi_factor
        final_efficacy = max(0.1, min(0.95, final_efficacy))
        
        # Simulate side effects
        side_effects = []
        side_effect_chance = random.uniform(0.1, 0.4)
        
        common_side_effects = ['Headache', 'Nausea', 'Dizziness', 'Fatigue', 'Rash']
        if random.random() < side_effect_chance:
            num_effects = random.randint(1, 3)
            side_effects = random.sample(common_side_effects, num_effects)
            
        return {
            'treatment': treatment,
            'efficacy_score': round(final_efficacy, 2),
            'response_category': 'Good' if final_efficacy > 0.7 else 'Moderate' if final_efficacy > 0.4 else 'Poor',
            'side_effects': side_effects,
            'treatment_duration_days': random.randint(30, 180)
        }
    
    def generate_patient_dataset(self, num_patients: int = 100) -> List[Dict]:
        """Generate complete patient dataset"""
        dataset = []
        
        for _ in range(num_patients):
            demographics = self.generate_demographics()
            lab_results = self.generate_lab_results(demographics)
            condition = demographics['condition']
            treatment = random.choice(self.treatments[condition])
            treatment_response = self.simulate_treatment_response(demographics, treatment)
            
            patient_record = {
                **demographics,
                'lab_results': lab_results,
                'treatment_response': treatment_response,
                'adverse_events': self.generate_adverse_events(demographics, treatment),
                'created_at': datetime.now().isoformat()
            }
            
            dataset.append(patient_record)
            
        return dataset
    
    def generate_adverse_events(self, patient_data: Dict, treatment: str) -> List[Dict]:
        """Generate adverse events based on patient and treatment"""
        events = []
        base_risk = random.uniform(0.05, 0.2)
        
        # Increase risk for older patients or those with comorbidities
        if patient_data['age'] > 65:
            base_risk *= 1.5
            
        adverse_events_pool = [
            {'type': 'Mild', 'events': ['Headache', 'Nausea', 'Dizziness']},
            {'type': 'Moderate', 'events': ['Hypertension', 'Elevated Liver Enzymes', 'Rash']},
            {'type': 'Severe', 'events': ['Anaphylaxis', 'Severe Hypertension', 'Liver Toxicity']}
        ]
        
        for severity_level in adverse_events_pool:
            if random.random() < base_risk:
                event = random.choice(severity_level['events'])
                events.append({
                    'event_type': event,
                    'severity': severity_level['type'],
                    'description': f"{event} possibly related to {treatment}",
                    'resolved': random.choice([True, False]),
                    'event_date': (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
                })
                base_risk *= 0.5  # Reduce probability for multiple events
                
        return events
    
    def export_to_csv(self, dataset: List[Dict], filename: str):
        """Export dataset to CSV format"""
        # Flatten structure for CSV
        flat_data = []
        for patient in dataset:
            flat_patient = {k: v for k, v in patient.items() if k not in ['lab_results', 'treatment_response', 'adverse_events']}
            flat_patient['treatment'] = patient['treatment_response']['treatment']
            flat_patient['efficacy_score'] = patient['treatment_response']['efficacy_score']
            flat_data.append(flat_patient)
            
        df = pd.DataFrame(flat_data)
        df.to_csv(filename, index=False)
        print(f"Dataset exported to {filename}")
    
    def export_to_json(self, dataset: List[Dict], filename: str):
        """Export dataset to JSON format"""
        with open(filename, 'w') as f:
            json.dump(dataset, f, indent=2)
        print(f"Dataset exported to {filename}")

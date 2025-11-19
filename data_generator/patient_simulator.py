import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any
import json

class ClinicalTrialSimulator:
    """
    Simulates clinical trial data with realistic patient profiles,
    treatment responses, and adverse events
    """
    
    def __init__(self):
        self.fake = Faker()
        self.drugs = ['Drug_A', 'Drug_B', 'Placebo']
        self.conditions = ['Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'Migraine']
        self.adverse_events = ['Headache', 'Nausea', 'Fatigue', 'Rash', 'Dizziness', 'None']
        
    def generate_patient_demographics(self, patient_id: int) -> Dict[str, Any]:
        """Generate realistic patient demographic data"""
        age = random.randint(18, 85)
        gender = random.choice(['Male', 'Female'])
        bmi = round(random.uniform(18.5, 35.0), 1)
        
        return {
            'patient_id': f"PT{patient_id:06d}",
            'age': age,
            'gender': gender,
            'weight_kg': round(bmi * (1.7 ** 2), 1),  # Approximate weight from BMI
            'height_cm': random.randint(150, 190),
            'bmi': bmi,
            'ethnicity': random.choice(['Caucasian', 'African American', 'Asian', 'Hispanic']),
            'medical_history': random.sample(self.conditions, random.randint(0, 2)),
            'screening_date': self.fake.date_between(start_date='-30d', end_date='today'),
            'site_id': f"SITE{random.randint(1, 10):03d}"
        }
    
    def generate_lab_results(self, patient_id: str, visit_day: int) -> Dict[str, Any]:
        """Generate laboratory test results with realistic ranges"""
        base_values = {
            'hdl_cholesterol': random.uniform(40, 60),
            'ldl_cholesterol': random.uniform(70, 130),
            'triglycerides': random.uniform(70, 150),
            'fasting_glucose': random.uniform(70, 100),
            'hemoglobin_a1c': random.uniform(4.5, 6.5),
            'creatinine': random.uniform(0.6, 1.2),
            'alt': random.uniform(10, 40),
            'ast': random.uniform(10, 35)
        }
        
        # Add some variability and trends
        results = {}
        for test, value in base_values.items():
            # Simulate some patients with abnormal results
            if random.random() < 0.1:  # 10% chance of abnormal
                if test in ['ldl_cholesterol', 'triglycerides', 'fasting_glucose', 'hemoglobin_a1c']:
                    value *= random.uniform(1.3, 2.0)  # Elevated
                else:
                    value *= random.uniform(0.5, 0.8)  # Low
                    
            results[test] = round(value, 2)
            
        return {
            'patient_id': patient_id,
            'visit_day': visit_day,
            'lab_results': results,
            'collection_timestamp': datetime.now().isoformat()
        }
    
    def generate_vital_signs(self, patient_id: str, visit_day: int, treatment: str) -> Dict[str, Any]:
        """Generate vital signs with treatment effects"""
        base_bp = {
            'systolic': random.randint(110, 140),
            'diastolic': random.randint(70, 90)
        }
        
        # Simulate treatment effect
        if treatment == 'Drug_A':
            base_bp['systolic'] -= random.randint(5, 15)
            base_bp['diastolic'] -= random.randint(3, 8)
        elif treatment == 'Drug_B':
            base_bp['systolic'] -= random.randint(3, 10)
            base_bp['diastolic'] -= random.randint(2, 6)
            
        return {
            'patient_id': patient_id,
            'visit_day': visit_day,
            'blood_pressure': base_bp,
            'heart_rate': random.randint(60, 100),
            'temperature_c': round(random.uniform(36.1, 37.2), 1),
            'respiratory_rate': random.randint(12, 20)
        }
    
    def generate_adverse_events(self, patient_id: str, visit_day: int, treatment: str) -> Dict[str, Any]:
        """Generate adverse events with treatment-specific probabilities"""
        ae_probability = 0.15 if treatment != 'Placebo' else 0.08
        has_ae = random.random() < ae_probability
        
        if has_ae:
            ae = random.choice([ae for ae in self.adverse_events if ae != 'None'])
            severity = random.choice(['Mild', 'Moderate', 'Severe'])
            related_to_treatment = random.random() < 0.7 if treatment != 'Placebo' else random.random() < 0.3
        else:
            ae = 'None'
            severity = None
            related_to_treatment = False
            
        return {
            'patient_id': patient_id,
            'visit_day': visit_day,
            'adverse_event': ae,
            'severity': severity,
            'related_to_treatment': related_to_treatment,
            'action_taken': random.choice(['None', 'Dose reduced', 'Treatment interrupted', 'Treatment discontinued']) if has_ae else 'None'
        }
    
    def generate_treatment_response(self, patient_id: str, demographics: Dict, treatment: str) -> List[Dict[str, Any]]:
        """Generate treatment response over multiple visits"""
        responses = []
        baseline_score = random.randint(15, 25)  # Baseline symptom score
        
        for visit_day in [0, 7, 14, 28, 56, 84]:  # Standard visit schedule
            # Calculate improvement based on treatment
            if visit_day == 0:
                improvement = 0
            else:
                if treatment == 'Drug_A':
                    improvement = min(15, baseline_score * (visit_day/84) * random.uniform(0.6, 0.9))
                elif treatment == 'Drug_B':
                    improvement = min(12, baseline_score * (visit_day/84) * random.uniform(0.4, 0.7))
                else:  # Placebo
                    improvement = min(8, baseline_score * (visit_day/84) * random.uniform(0.1, 0.3))
            
            current_score = max(0, round(baseline_score - improvement, 1))
            
            responses.append({
                'patient_id': patient_id,
                'visit_day': visit_day,
                'symptom_score': current_score,
                'improvement_from_baseline': round(improvement, 1),
                'patient_global_impression': random.choice(['Very much improved', 'Much improved', 'Minimally improved', 'No change', 'Worse']),
                'investigator_global_impression': random.choice(['Very much improved', 'Much improved', 'Minimally improved', 'No change', 'Worse'])
            })
            
        return responses
    
    def generate_complete_trial_data(self, num_patients: int = 100) -> Dict[str, Any]:
        """Generate complete clinical trial dataset"""
        print(f"🚀 Generating clinical trial data for {num_patients} patients...")
        
        all_data = {
            'patients': [],
            'lab_results': [],
            'vital_signs': [],
            'adverse_events': [],
            'treatment_responses': [],
            'trial_metadata': {
                'simulation_date': datetime.now().isoformat(),
                'number_of_patients': num_patients,
                'number_of_sites': 10,
                'treatment_arms': self.drugs,
                'study_duration_days': 84
            }
        }
        
        for i in range(1, num_patients + 1):
            # Assign treatment arm
            treatment = random.choice(self.drugs)
            
            # Generate patient demographics
            demographics = self.generate_patient_demographics(i)
            demographics['treatment_arm'] = treatment
            all_data['patients'].append(demographics)
            
            # Generate data for each visit
            visit_days = [0, 7, 14, 28, 56, 84]
            for visit_day in visit_days:
                # Lab results (not every visit)
                if visit_day in [0, 28, 84] or random.random() < 0.3:
                    all_data['lab_results'].append(self.generate_lab_results(demographics['patient_id'], visit_day))
                
                # Vital signs (every visit)
                all_data['vital_signs'].append(self.generate_vital_signs(demographics['patient_id'], visit_day, treatment))
                
                # Adverse events (reported at visits)
                all_data['adverse_events'].append(self.generate_adverse_events(demographics['patient_id'], visit_day, treatment))
            
            # Treatment response over time
            all_data['treatment_responses'].extend(
                self.generate_treatment_response(demographics['patient_id'], demographics, treatment)
            )
            
            if i % 20 == 0:
                print(f"✅ Generated data for {i} patients...")
        
        print("🎉 Clinical trial data generation complete!")
        return all_data
    
    def export_to_files(self, data: Dict[str, Any], output_dir: str = 'output'):
        """Export data to multiple file formats"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Export to JSON
        with open(f'{output_dir}/clinical_trial_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        # Export to CSV files
        pd.DataFrame(data['patients']).to_csv(f'{output_dir}/patients.csv', index=False)
        pd.DataFrame(data['lab_results']).to_csv(f'{output_dir}/lab_results.csv', index=False)
        pd.DataFrame(data['vital_signs']).to_csv(f'{output_dir}/vital_signs.csv', index=False)
        pd.DataFrame(data['adverse_events']).to_csv(f'{output_dir}/adverse_events.csv', index=False)
        pd.DataFrame(data['treatment_responses']).to_csv(f'{output_dir}/treatment_responses.csv', index=False)
        
        print(f"📁 Data exported to {output_dir}/ directory")

# Example usage
if __name__ == "__main__":
    simulator = ClinicalTrialSimulator()
    trial_data = simulator.generate_complete_trial_data(num_patients=50)
    simulator.export_to_files(trial_data)

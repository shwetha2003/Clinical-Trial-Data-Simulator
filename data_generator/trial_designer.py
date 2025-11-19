import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

class TrialAnalyzer:
    """Analyze clinical trial data and generate insights"""
    
    def __init__(self, data_path: str):
        with open(data_path, 'r') as f:
            self.data = json.load(f)
        
        self.patients_df = pd.DataFrame(self.data['patients'])
        self.lab_df = pd.DataFrame(self.data['lab_results'])
        self.vitals_df = pd.DataFrame(self.data['vital_signs'])
        self.ae_df = pd.DataFrame(self.data['adverse_events'])
        self.response_df = pd.DataFrame(self.data['treatment_responses'])
    
    def calculate_treatment_efficacy(self):
        """Calculate treatment efficacy metrics"""
        print("📊 Analyzing Treatment Efficacy...")
        
        # Get final visit responses
        final_responses = self.response_df[self.response_df['visit_day'] == 84]
        
        efficacy_results = {}
        
        for treatment in self.patients_df['treatment_arm'].unique():
            treatment_patients = self.patients_df[self.patients_df['treatment_arm'] == treatment]['patient_id']
            treatment_responses = final_responses[final_responses['patient_id'].isin(treatment_patients)]
            
            mean_improvement = treatment_responses['improvement_from_baseline'].mean()
            response_rate = (treatment_responses['improvement_from_baseline'] > 10).mean() * 100
            
            efficacy_results[treatment] = {
                'mean_improvement': round(mean_improvement, 2),
                'response_rate': round(response_rate, 1),
                'patient_count': len(treatment_patients)
            }
        
        return efficacy_results
    
    def analyze_safety_profile(self):
        """Analyze safety and adverse events"""
        print("🛡️ Analyzing Safety Profile...")
        
        safety_results = {}
        
        for treatment in self.patients_df['treatment_arm'].unique():
            treatment_patients = self.patients_df[self.patients_df['treatment_arm'] == treatment]['patient_id']
            treatment_ae = self.ae_df[
                (self.ae_df['patient_id'].isin(treatment_patients)) & 
                (self.ae_df['adverse_event'] != 'None')
            ]
            
            total_ae = len(treatment_ae)
            serious_ae = len(treatment_ae[treatment_ae['severity'] == 'Severe'])
            related_ae = len(treatment_ae[treatment_ae['related_to_treatment'] == True])
            
            safety_results[treatment] = {
                'total_adverse_events': total_ae,
                'serious_adverse_events': serious_ae,
                'treatment_related_events': related_ae,
                'ae_per_patient': round(total_ae / len(treatment_patients), 2)
            }
        
        return safety_results
    
    def generate_statistical_tests(self):
        """Perform statistical analysis"""
        print("📈 Performing Statistical Analysis...")
        
        # ANOVA test for treatment efficacy
        final_responses = self.response_df[self.response_df['visit_day'] == 84]
        merged_data = final_responses.merge(self.patients_df[['patient_id', 'treatment_arm']], on='patient_id')
        
        groups = [merged_data[merged_data['treatment_arm'] == treatment]['improvement_from_baseline'] 
                 for treatment in merged_data['treatment_arm'].unique()]
        
        f_stat, p_value = stats.f_oneway(*groups)
        
        return {
            'anova_f_statistic': round(f_stat, 3),
            'anova_p_value': round(p_value, 4),
            'significant_difference': p_value < 0.05
        }
    
    def create_visualizations(self, output_dir: str = 'output'):
        """Generate visualization plots"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Treatment Efficacy Plot
        plt.figure(figsize=(10, 6))
        merged_data = self.response_df.merge(self.patients_df[['patient_id', 'treatment_arm']], on='patient_id')
        
        for treatment in merged_data['treatment_arm'].unique():
            treatment_data = merged_data[merged_data['treatment_arm'] == treatment]
            mean_scores = treatment_data.groupby('visit_day')['symptom_score'].mean()
            plt.plot(mean_scores.index, mean_scores.values, marker='o', label=treatment, linewidth=2)
        
        plt.title('Treatment Efficacy Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Visit Day', fontsize=12)
        plt.ylabel('Mean Symptom Score', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/treatment_efficacy.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Adverse Events Comparison
        plt.figure(figsize=(10, 6))
        ae_summary = self.ae_df[self.ae_df['adverse_event'] != 'None']
        ae_summary = ae_summary.merge(self.patients_df[['patient_id', 'treatment_arm']], on='patient_id')
        
        ae_counts = ae_summary.groupby(['treatment_arm', 'adverse_event']).size().unstack(fill_value=0)
        ae_counts.plot(kind='bar', ax=plt.gca())
        
        plt.title('Adverse Events by Treatment Arm', fontsize=14, fontweight='bold')
        plt.xlabel('Treatment Arm', fontsize=12)
        plt.ylabel('Number of Events', fontsize=12)
        plt.legend(title='Adverse Event', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/adverse_events.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Visualizations saved to {output_dir}/")
    
    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        print("📋 Generating Analysis Report...")
        
        efficacy = self.calculate_treatment_efficacy()
        safety = self.analyze_safety_profile()
        stats_results = self.generate_statistical_tests()
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'trial_metadata': self.data['trial_metadata'],
            'efficacy_analysis': efficacy,
            'safety_analysis': safety,
            'statistical_analysis': stats_results,
            'key_findings': self._generate_key_findings(efficacy, safety, stats_results)
        }
        
        # Save report
        with open('output/analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self._print_summary(report)
        
        return report
    
    def _generate_key_findings(self, efficacy, safety, stats):
        """Generate key findings from analysis"""
        findings = []
        
        # Find most effective treatment
        best_treatment = max(efficacy.items(), key=lambda x: x[1]['mean_improvement'])
        findings.append(f"Most effective treatment: {best_treatment[0]} with {best_treatment[1]['mean_improvement']} point improvement")
        
        # Safety findings
        safest_treatment = min(safety.items(), key=lambda x: x[1]['ae_per_patient'])
        findings.append(f"Best safety profile: {safest_treatment[0]} with {safest_treatment[1]['ae_per_patient']} AEs per patient")
        
        # Statistical significance
        if stats['significant_difference']:
            findings.append("Statistically significant difference between treatment arms (p < 0.05)")
        else:
            findings.append("No statistically significant difference between treatment arms")
            
        return findings
    
    def _print_summary(self, report):
        """Print summary to console"""
        print("\n" + "="*60)
        print("🎯 CLINICAL TRIAL ANALYSIS SUMMARY")
        print("="*60)
        
        print("\n📊 EFFICACY RESULTS:")
        for treatment, results in report['efficacy_analysis'].items():
            print(f"   {treatment}:")
            print(f"     • Mean Improvement: {results['mean_improvement']} points")
            print(f"     • Response Rate: {results['response_rate']}%")
            print(f"     • Patients: {results['patient_count']}")
        
        print("\n🛡️ SAFETY RESULTS:")
        for treatment, results in report['safety_analysis'].items():
            print(f"   {treatment}:")
            print(f"     • Total AEs: {results['total_adverse_events']}")
            print(f"     • Serious AEs: {results['serious_adverse_events']}")
            print(f"     • AEs per Patient: {results['ae_per_patient']}")
        
        print("\n📈 STATISTICAL ANALYSIS:")
        print(f"   ANOVA F-statistic: {report['statistical_analysis']['anova_f_statistic']}")
        print(f"   P-value: {report['statistical_analysis']['anova_p_value']}")
        print(f"   Significant: {'Yes' if report['statistical_analysis']['significant_difference'] else 'No'}")
        
        print("\n🔑 KEY FINDINGS:")
        for finding in report['key_findings']:
            print(f"   • {finding}")

# Example usage
if __name__ == "__main__":
    # First generate data, then analyze
    from patient_simulator import ClinicalTrialSimulator
    
    simulator = ClinicalTrialSimulator()
    trial_data = simulator.generate_complete_trial_data(num_patients=100)
    simulator.export_to_files(trial_data)
    
    # Analyze the generated data
    analyzer = TrialAnalyzer('output/clinical_trial_data.json')
    report = analyzer.generate_analysis_report()
    analyzer.create_visualizations()

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any
import json

class TrialDesigner:
    def __init__(self):
        self.design_templates = {
            "parallel": {
                "description": "Parallel group design",
                "arms": 2,
                "randomization": "1:1"
            },
            "crossover": {
                "description": "Crossover design",
                "arms": 2,
                "periods": 2
            },
            "factorial": {
                "description": "Factorial design",
                "factors": 2,
                "levels": 2
            }
        }
    
    def calculate_sample_size(self, alpha: float = 0.05, power: float = 0.8, 
                            effect_size: float = 0.5, design: str = "parallel") -> int:
        """Calculate required sample size for trial"""
        if design == "parallel":
            # Two-sample t-test sample size calculation
            t_alpha = stats.norm.ppf(1 - alpha/2)
            t_beta = stats.norm.ppf(power)
            n_per_group = 2 * ((t_alpha + t_beta) / effect_size) ** 2
            return int(np.ceil(n_per_group)) * 2
        else:
            # Simplified for other designs
            base_size = 100
            return int(base_size * 1.2)  # 20% increase for complex designs
    
    def design_trial(self, trial_params: Dict) -> Dict[str, Any]:
        """Design a clinical trial based on parameters"""
        design_type = trial_params.get('design', 'parallel')
        primary_endpoint = trial_params.get('primary_endpoint', 'efficacy_score')
        
        sample_size = self.calculate_sample_size(
            alpha=trial_params.get('alpha', 0.05),
            power=trial_params.get('power', 0.8),
            effect_size=trial_params.get('effect_size', 0.5),
            design=design_type
        )
        
        return {
            'trial_id': f"TRIAL_{np.random.randint(1000, 9999)}",
            'design_type': design_type,
            'sample_size': sample_size,
            'primary_endpoint': primary_endpoint,
            'duration_weeks': trial_params.get('duration_weeks', 12),
            'arms': self.design_templates[design_type].get('arms', 2),
            'inclusion_criteria': self.generate_inclusion_criteria(),
            'exclusion_criteria': self.generate_exclusion_criteria(),
            'statistical_plan': self.generate_statistical_plan(design_type)
        }
    
    def generate_inclusion_criteria(self) -> List[str]:
        """Generate standard inclusion criteria"""
        return [
            "Age 18-75 years",
            "Diagnosed with condition for at least 3 months",
            "Stable concomitant medications for 4 weeks",
            "Willing and able to provide informed consent"
        ]
    
    def generate_exclusion_criteria(self) -> List[str]:
        """Generate standard exclusion criteria"""
        return [
            "Pregnancy or lactation",
            "Severe hepatic or renal impairment",
            "History of hypersensitivity to study drug components",
            "Participation in another clinical trial within 30 days"
        ]
    
    def generate_statistical_plan(self, design: str) -> Dict[str, Any]:
        """Generate statistical analysis plan"""
        plans = {
            "parallel": {
                "primary_analysis": "ANCOVA with baseline as covariate",
                "alpha": 0.05,
                "multiple_testing_correction": "Bonferroni",
                "interim_analysis": "At 50% enrollment"
            },
            "crossover": {
                "primary_analysis": "Mixed effects model with period and sequence effects",
                "alpha": 0.05,
                "carryover_testing": True
            },
            "factorial": {
                "primary_analysis": "Two-way ANOVA with interaction term",
                "alpha": 0.05,
                "interaction_test": True
            }
        }
        return plans.get(design, plans["parallel"])

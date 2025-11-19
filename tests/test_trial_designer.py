import pytest
import numpy as np

class TestTrialDesigner:
    
    def test_calculate_sample_size(self, trial_designer):
        """Test sample size calculation"""
        # Test parallel design
        sample_size = trial_designer.calculate_sample_size(
            alpha=0.05, power=0.8, effect_size=0.5, design="parallel"
        )
        
        assert sample_size > 0
        assert isinstance(sample_size, int)
        
        # Test that larger effect sizes require smaller samples
        small_effect_size = trial_designer.calculate_sample_size(effect_size=0.2)
        large_effect_size = trial_designer.calculate_sample_size(effect_size=0.8)
        
        assert small_effect_size > large_effect_size
    
    def test_design_trial(self, trial_designer, sample_trial_params):
        """Test trial design functionality"""
        design = trial_designer.design_trial(sample_trial_params)
        
        # Check required fields
        assert 'trial_id' in design
        assert 'design_type' in design
        assert 'sample_size' in design
        assert 'primary_endpoint' in design
        assert 'duration_weeks' in design
        assert 'arms' in design
        assert 'inclusion_criteria' in design
        assert 'exclusion_criteria' in design
        assert 'statistical_plan' in design
        
        # Check values
        assert design['design_type'] == 'parallel'
        assert design['sample_size'] > 0
        assert design['duration_weeks'] == 12
        assert design['arms'] == 2
    
    def test_inclusion_criteria(self, trial_designer):
        """Test inclusion criteria generation"""
        criteria = trial_designer.generate_inclusion_criteria()
        
        assert isinstance(criteria, list)
        assert len(criteria) > 0
        assert all(isinstance(criterion, str) for criterion in criteria)
        
        # Check for common criteria
        criteria_text = ' '.join(criteria)
        assert 'age' in criteria_text.lower()
        assert 'consent' in criteria_text.lower()
    
    def test_exclusion_criteria(self, trial_designer):
        """Test exclusion criteria generation"""
        criteria = trial_designer.generate_exclusion_criteria()
        
        assert isinstance(criteria, list)
        assert len(criteria) > 0
        assert all(isinstance(criterion, str) for criterion in criteria)
    
    def test_statistical_plan(self, trial_designer):
        """Test statistical plan generation"""
        for design_type in ['parallel', 'crossover', 'factorial']:
            plan = trial_designer.generate_statistical_plan(design_type)
            
            assert isinstance(plan, dict)
            assert 'primary_analysis' in plan
            assert 'alpha' in plan
            
            # Check alpha value
            assert plan['alpha'] == 0.05
    
    def test_design_templates(self, trial_designer):
        """Test design templates"""
        templates = trial_designer.design_templates
        
        assert 'parallel' in templates
        assert 'crossover' in templates
        assert 'factorial' in templates
        
        # Check parallel design template
        parallel_template = templates['parallel']
        assert 'description' in parallel_template
        assert 'arms' in parallel_template
        assert 'randomization' in parallel_template

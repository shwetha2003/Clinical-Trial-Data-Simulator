from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
from scipy import stats
import numpy as np
import json

router = APIRouter()

class StatisticalTestRequest(BaseModel):
    data: List[float]
    reference_value: float = 0
    alpha: float = 0.05

class CorrelationRequest(BaseModel):
    x_data: List[float]
    y_data: List[float]

@router.post("/statistics/t-test")
async def perform_ttest(request: StatisticalTestRequest):
    """Perform one-sample t-test"""
    try:
        t_stat, p_value = stats.ttest_1samp(request.data, request.reference_value)
        
        return {
            "test_type": "one_sample_ttest",
            "t_statistic": round(t_stat, 4),
            "p_value": round(p_value, 4),
            "significant": p_value < request.alpha,
            "alpha": request.alpha,
            "sample_size": len(request.data),
            "mean": round(np.mean(request.data), 4),
            "std_dev": round(np.std(request.data), 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing t-test: {str(e)}")

@router.post("/statistics/anova")
async def perform_anova(groups: Dict[str, List[float]]):
    """Perform ANOVA test"""
    try:
        group_data = list(groups.values())
        f_stat, p_value = stats.f_oneway(*group_data)
        
        return {
            "test_type": "anova",
            "f_statistic": round(f_stat, 4),
            "p_value": round(p_value, 4),
            "groups": list(groups.keys()),
            "group_means": {group: round(np.mean(data), 4) for group, data in groups.items()},
            "group_stds": {group: round(np.std(data), 4) for group, data in groups.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing ANOVA: {str(e)}")

@router.post("/statistics/correlation")
async def calculate_correlation(request: CorrelationRequest):
    """Calculate Pearson correlation"""
    try:
        if len(request.x_data) != len(request.y_data):
            raise HTTPException(status_code=400, detail="x_data and y_data must have same length")
        
        correlation, p_value = stats.pearsonr(request.x_data, request.y_data)
        
        return {
            "test_type": "pearson_correlation",
            "correlation": round(correlation, 4),
            "p_value": round(p_value, 4),
            "sample_size": len(request.x_data),
            "interpretation": _interpret_correlation(correlation)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating correlation: {str(e)}")

def _interpret_correlation(r: float) -> str:
    """Interpret correlation coefficient"""
    abs_r = abs(r)
    if abs_r >= 0.8:
        return "Very strong"
    elif abs_r >= 0.6:
        return "Strong"
    elif abs_r >= 0.4:
        return "Moderate"
    elif abs_r >= 0.2:
        return "Weak"
    else:
        return "Very weak"

@router.get("/analytics/efficacy-by-condition")
async def efficacy_by_condition():
    """Analyze efficacy by medical condition"""
    try:
        # This would typically query the database
        # For now, return mock analysis
        conditions = ["Hypertension", "Diabetes Type 2", "Asthma", "COPD"]
        analysis = {}
        
        for condition in conditions:
            # Simulate efficacy scores for each condition
            efficacy_scores = np.random.normal(0.6, 0.2, 50)
            efficacy_scores = np.clip(efficacy_scores, 0, 1)
            
            analysis[condition] = {
                "mean_efficacy": round(float(np.mean(efficacy_scores)), 3),
                "std_efficacy": round(float(np.std(efficacy_scores)), 3),
                "sample_size": len(efficacy_scores),
                "good_response_rate": round(float(np.mean(np.array(efficacy_scores) > 0.7) * 100), 1)
            }
        
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing efficacy: {str(e)}")

@router.get("/analytics/safety-profile")
async def safety_profile():
    """Generate safety profile analysis"""
    try:
        # Mock safety analysis
        adverse_events = {
            "Headache": {"mild": 15, "moderate": 5, "severe": 1},
            "Nausea": {"mild": 12, "moderate": 3, "severe": 0},
            "Dizziness": {"mild": 8, "moderate": 2, "severe": 0},
            "Fatigue": {"mild": 10, "moderate": 2, "severe": 0},
            "Rash": {"mild": 6, "moderate": 1, "severe": 0}
        }
        
        total_patients = 100
        total_events = sum(sum(severity.values()) for severity in adverse_events.values())
        
        return {
            "adverse_events": adverse_events,
            "summary": {
                "total_patients": total_patients,
                "patients_with_events": 45,  # Mock data
                "total_events": total_events,
                "event_rate_per_patient": round(total_events / total_patients, 2)
            },
            "most_common_events": sorted(
                [(event, sum(severity.values())) for event, severity in adverse_events.items()],
                key=lambda x: x[1],
                reverse=True
            )[:3]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating safety profile: {str(e)}")

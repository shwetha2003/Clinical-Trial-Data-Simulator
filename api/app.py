from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import mysql.connector
from mysql.connector import Error
import json
import uuid
from datetime import datetime

# Import our modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_generator.patient_simulator import PatientSimulator
from data_generator.trial_designer import TrialDesigner
from data_generator.data_validator import DataValidator

app = FastAPI(
    title="Clinical Trial Simulator API",
    description="API for simulating clinical trial data and analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'clinical_trial_simulator'
}

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Initialize modules
patient_simulator = PatientSimulator()
trial_designer = TrialDesigner()
data_validator = DataValidator()

class TrialDesignRequest(BaseModel):
    design: str = "parallel"
    alpha: float = 0.05
    power: float = 0.8
    effect_size: float = 0.5
    duration_weeks: int = 12
    primary_endpoint: str = "efficacy_score"

class AnalysisRequest(BaseModel):
    trial_id: str
    analysis_type: str = "efficacy"
    parameters: Dict[str, Any] = {}

@app.get("/")
async def root():
    return {"message": "Clinical Trial Simulator API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_conn = get_db_connection()
    if db_conn and db_conn.is_connected():
        db_status = "connected"
        db_conn.close()
    else:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/generate-patients")
async def generate_patients(num_patients: int = 100):
    """Generate simulated patient data"""
    try:
        dataset = patient_simulator.generate_patient_dataset(num_patients)
        
        # Store in database
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            for patient in dataset:
                # Insert patient
                patient_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO patients (id, patient_id, age, gender, weight, height, bmi, condition)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    patient_id,
                    patient['patient_id'],
                    patient['age'],
                    patient['gender'],
                    patient['weight'],
                    patient['height'],
                    patient['bmi'],
                    patient['condition']
                ))
                
                # Insert lab results
                for lab in patient['lab_results']:
                    cursor.execute("""
                        INSERT INTO lab_results (id, patient_id, test_name, test_value, normal_min, normal_max, unit, is_abnormal, test_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        str(uuid.uuid4()),
                        patient_id,
                        lab['test_name'],
                        lab['test_value'],
                        lab['normal_min'],
                        lab['normal_max'],
                        lab['unit'],
                        lab['is_abnormal'],
                        lab['test_date']
                    ))
                
                # Insert treatment
                treatment_response = patient['treatment_response']
                cursor.execute("""
                    INSERT INTO treatments (id, patient_id, treatment_name, dosage, frequency, efficacy_score, response_category, treatment_duration_days)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    patient_id,
                    treatment_response['treatment'],
                    1.0,  # Default dosage
                    "once daily",
                    treatment_response['efficacy_score'],
                    treatment_response['response_category'],
                    treatment_response['treatment_duration_days']
                ))
                
                # Insert adverse events
                for event in patient['adverse_events']:
                    cursor.execute("""
                        INSERT INTO adverse_events (id, patient_id, event_type, severity, description, resolved, event_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        str(uuid.uuid4()),
                        patient_id,
                        event['event_type'],
                        event['severity'],
                        event['description'],
                        event['resolved'],
                        event['event_date']
                    ))
            
            connection.commit()
            cursor.close()
            connection.close()
        
        return {
            "message": f"Generated {num_patients} patients",
            "patients": dataset[:5],  # Return first 5 for preview
            "total_generated": len(dataset)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating patients: {str(e)}")

@app.post("/design-trial")
async def design_trial(request: TrialDesignRequest):
    """Design a clinical trial"""
    try:
        trial_params = request.dict()
        trial_design = trial_designer.design_trial(trial_params)
        
        # Store trial design
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO trial_designs (id, trial_id, design_type, sample_size, primary_endpoint, duration_weeks, arms, inclusion_criteria, exclusion_criteria, statistical_plan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                trial_design['trial_id'],
                trial_design['design_type'],
                trial_design['sample_size'],
                trial_design['primary_endpoint'],
                trial_design['duration_weeks'],
                trial_design['arms'],
                json.dumps(trial_design['inclusion_criteria']),
                json.dumps(trial_design['exclusion_criteria']),
                json.dumps(trial_design['statistical_plan'])
            ))
            connection.commit()
            cursor.close()
            connection.close()
        
        return trial_design
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error designing trial: {str(e)}")

@app.get("/patients")
async def get_patients(limit: int = 100, offset: int = 0):
    """Get patient data"""
    try:
        connection = get_db_connection()
        if not connection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor(dictionary=True)
        
        # Get patients with their treatments
        cursor.execute("""
            SELECT p.*, t.treatment_name, t.efficacy_score, t.response_category
            FROM patients p
            LEFT JOIN treatments t ON p.id = t.patient_id
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        patients = cursor.fetchall()
        
        # Get lab results for each patient
        for patient in patients:
            cursor.execute("""
                SELECT test_name, test_value, normal_min, normal_max, unit, is_abnormal
                FROM lab_results 
                WHERE patient_id = %s
            """, (patient['id'],))
            patient['lab_results'] = cursor.fetchall()
            
            cursor.execute("""
                SELECT event_type, severity, description, resolved
                FROM adverse_events 
                WHERE patient_id = %s
            """, (patient['id'],))
            patient['adverse_events'] = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {
            "patients": patients,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(patients)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patients: {str(e)}")

@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    try:
        connection = get_db_connection()
        if not connection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor(dictionary=True)
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) as total_patients FROM patients")
        total_patients = cursor.fetchone()['total_patients']
        
        cursor.execute("SELECT COUNT(*) as total_trials FROM trial_designs")
        total_trials = cursor.fetchone()['total_trials']
        
        cursor.execute("SELECT COUNT(*) as abnormal_labs FROM lab_results WHERE is_abnormal = TRUE")
        abnormal_labs = cursor.fetchone()['abnormal_labs']
        
        cursor.execute("SELECT COUNT(*) as adverse_events FROM adverse_events")
        adverse_events = cursor.fetchone()['adverse_events']
        
        # Condition distribution
        cursor.execute("""
            SELECT condition, COUNT(*) as count 
            FROM patients 
            GROUP BY condition 
            ORDER BY count DESC
        """)
        condition_distribution = cursor.fetchall()
        
        # Efficacy distribution
        cursor

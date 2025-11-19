-- Clinical Trial Simulator Database Schema

CREATE DATABASE IF NOT EXISTS clinical_trial_simulator;
USE clinical_trial_simulator;

-- Patients table
CREATE TABLE patients (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(50) UNIQUE NOT NULL,
    age INT NOT NULL CHECK (age BETWEEN 18 AND 100),
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    weight DECIMAL(5,2) CHECK (weight BETWEEN 30 AND 200),
    height DECIMAL(5,2) CHECK (height BETWEEN 140 AND 210),
    bmi DECIMAL(4,2) CHECK (bmi BETWEEN 15 AND 50),
    condition VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_condition (condition),
    INDEX idx_age (age),
    INDEX idx_created (created_at)
);

-- Lab results table
CREATE TABLE lab_results (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    test_name VARCHAR(100) NOT NULL,
    test_value DECIMAL(8,2) NOT NULL,
    normal_min DECIMAL(8,2) NOT NULL,
    normal_max DECIMAL(8,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    is_abnormal BOOLEAN DEFAULT FALSE,
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_patient_test (patient_id, test_name),
    INDEX idx_abnormal (is_abnormal),
    INDEX idx_test_date (test_date),
    CHECK (normal_min < normal_max),
    CHECK (test_value >= 0)
);

-- Treatments table
CREATE TABLE treatments (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    treatment_name VARCHAR(100) NOT NULL,
    dosage DECIMAL(8,2) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NULL,
    efficacy_score DECIMAL(3,2) CHECK (efficacy_score BETWEEN 0 AND 1),
    response_category ENUM('Poor', 'Moderate', 'Good') NOT NULL,
    treatment_duration_days INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_treatment (treatment_name),
    INDEX idx_efficacy (efficacy_score),
    INDEX idx_response (response_category)
);

-- Adverse events table
CREATE TABLE adverse_events (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    severity ENUM('Mild', 'Moderate', 'Severe') NOT NULL,
    description TEXT,
    event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved),
    INDEX idx_event_date (event_date)
);

-- Trial designs table
CREATE TABLE trial_designs (
    id VARCHAR(36) PRIMARY KEY,
    trial_id VARCHAR(50) UNIQUE NOT NULL,
    design_type VARCHAR(50) NOT NULL,
    sample_size INT NOT NULL CHECK (sample_size > 0),
    primary_endpoint VARCHAR(100) NOT NULL,
    duration_weeks INT NOT NULL CHECK (duration_weeks > 0),
    arms INT NOT NULL CHECK (arms > 0),
    inclusion_criteria JSON NOT NULL,
    exclusion_criteria JSON NOT NULL,
    statistical_plan JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_design_type (design_type),
    INDEX idx_sample_size (sample_size)
);

-- Analysis results table
CREATE TABLE analysis_results (
    id VARCHAR(36) PRIMARY KEY,
    trial_id VARCHAR(50) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    parameters JSON NOT NULL,
    results JSON NOT NULL,
    p_value DECIMAL(6,4),
    significance BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trial_id) REFERENCES trial_designs(trial_id),
    INDEX idx_analysis_type (analysis_type),
    INDEX idx_significance (significance),
    INDEX idx_created (created_at)
);

-- Data quality reports table
CREATE TABLE data_quality_reports (
    id VARCHAR(36) PRIMARY KEY,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_patients INT NOT NULL,
    valid_patients INT NOT NULL,
    completeness_score DECIMAL(5,2),
    validity_score DECIMAL(5,2),
    overall_quality_score DECIMAL(5,2),
    validation_errors JSON,
    summary_stats JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_report_date (report_date),
    INDEX idx_quality_score (overall_quality_score)
);

-- Views for common queries

CREATE VIEW patient_summary AS
SELECT 
    p.patient_id,
    p.age,
    p.gender,
    p.condition,
    p.bmi,
    t.treatment_name,
    t.efficacy_score,
    t.response_category,
    COUNT(DISTINCT l.id) as lab_test_count,
    COUNT(DISTINCT ae.id) as adverse_event_count
FROM patients p
LEFT JOIN treatments t ON p.id = t.patient_id
LEFT JOIN lab_results l ON p.id = l.patient_id
LEFT JOIN adverse_events ae ON p.id = ae.patient_id
GROUP BY p.id, t.id;

CREATE VIEW trial_overview AS
SELECT 
    td.trial_id,
    td.design_type,
    td.sample_size,
    td.duration_weeks,
    COUNT(DISTINCT p.id) as enrolled_patients,
    AVG(t.efficacy_score) as avg_efficacy,
    COUNT(DISTINCT ae.id) as total_adverse_events
FROM trial_designs td
LEFT JOIN patients p ON 1=1
LEFT JOIN treatments t ON p.id = t.patient_id
LEFT JOIN adverse_events ae ON p.id = ae.patient_id
GROUP BY td.id;

// API base URL
const API_BASE = 'http://localhost:8000';

// Chart instances
let conditionChart = null;
let efficacyChart = null;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
});

// Load all dashboard data
async function loadDashboardData() {
    try {
        await loadSummaryMetrics();
        await loadAnalyticsData();
        await loadRecentPatients();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Error loading dashboard data', 'danger');
    }
}

// Load summary metrics
async function loadSummaryMetrics() {
    const response = await fetch(`${API_BASE}/analytics/summary`);
    const data = await response.json();
    
    // Update metric cards
    document.getElementById('metricPatients').textContent = data.summary.total_patients;
    document.getElementById('metricTrials').textContent = data.summary.total_trials;
    document.getElementById('metricEfficacy').textContent = '65%'; // Mock data
    document.getElementById('metricQuality').textContent = '98%'; // Mock data
    
    // Update quick stats
    document.getElementById('totalPatients').textContent = data.summary.total_patients;
    document.getElementById('dataQuality').textContent = '98%';
    document.getElementById('avgEfficacy').textContent = '65%';
    document.getElementById('adverseEvents').textContent = data.summary.adverse_events;
}

// Load analytics data for charts
async function loadAnalyticsData() {
    const response = await fetch(`${API_BASE}/analytics/summary`);
    const data = await response.json();
    
    // Condition distribution chart
    const conditionCtx = document.getElementById('conditionChart').getContext('2d');
    const conditions = data.distributions.conditions.map(item => item.condition);
    const counts = data.distributions.conditions.map(item => item.count);
    
    if (conditionChart) {
        conditionChart.destroy();
    }
    
    conditionChart = new Chart(conditionCtx, {
        type: 'doughnut',
        data: {
            labels: conditions,
            datasets: [{
                data: counts,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
    
    // Efficacy by condition chart
    const efficacyResponse = await fetch(`${API_BASE}/analytics/efficacy-by-condition`);
    const efficacyData = await efficacyResponse.json();
    
    const efficacyCtx = document.getElementById('efficacyChart').getContext('2d');
    const efficacyConditions = Object.keys(efficacyData);
    const efficacyScores = efficacyConditions.map(condition => 
        Math.round(efficacyData[condition].mean_efficacy * 100)
    );
    
    if (efficacyChart) {
        efficacyChart.destroy();
    }
    
    efficacyChart = new Chart(efficacyCtx, {
        type: 'bar',
        data: {
            labels: efficacyConditions,
            datasets: [{
                label: 'Efficacy (%)',
                data: efficacyScores,
                backgroundColor: '#36A2EB',
                borderColor: '#2c3e50',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Efficacy (%)'
                    }
                }
            }
        }
    });
}

// Load recent patients table
async function loadRecentPatients() {
    const response = await fetch(`${API_BASE}/patients?limit=10`);
    const data = await response.json();
    
    const tbody = document.querySelector('#patientsTable tbody');
    tbody.innerHTML = '';
    
    data.patients.forEach(patient => {
        const row = document.createElement('tr');
        
        // Determine status badge
        let statusClass = 'status-moderate';
        let statusText = 'Moderate';
        if (patient.efficacy_score > 0.7) {
            statusClass = 'status-good';
            statusText = 'Good';
        } else if (patient.efficacy_score < 0.4) {
            statusClass = 'status-poor';
            statusText = 'Poor';
        }
        
        row.innerHTML = `
            <td>${patient.patient_id}</td>
            <td>${patient.age}</td>
            <td>${patient.gender}</td>
            <td>${patient.condition}</td>
            <td>${patient.treatment_name || 'N/A'}</td>
            <td>${patient.efficacy_score ? Math.round(patient.efficacy_score * 100) + '%' : 'N/A'}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
        `;
        
        tbody.appendChild(row);
    });
}

// Generate patients
async function generatePatients() {
    const patientCount = document.getElementById('patientCount').value;
    
    showAlert('Generating patients...', 'info');
    setLoadingState(true);
    
    try {
        const response = await fetch(`${API_BASE}/generate-patients?num_patients=${patientCount}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        showAlert(`Successfully generated ${data.total_generated} patients`, 'success');
        loadDashboardData();
    } catch (error) {
        console.error('Error generating patients:', error);
        showAlert('Error generating patients', 'danger');
    } finally {
        setLoadingState(false);
    }
}

// Design trial modal
function designTrial() {
    const modal = new bootstrap.Modal(document.getElementById('trialDesignModal'));
    modal.show();
}

// Submit trial design
async function submitTrialDesign() {
    const designData = {
        design: document.getElementById('designType').value,
        duration_weeks: parseInt(document.getElementById('trialDuration').value),
        alpha: parseFloat(document.getElementById('alpha').value),
        power: parseFloat(document.getElementById('power').value),
        effect_size: parseFloat(document.getElementById('effectSize').value)
    };
    
    try {
        const response = await fetch(`${API_BASE}/design-trial`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(designData)
        });
        
        const result = await response.json();
        
        // Display results
        const resultDiv = document.getElementById('trialDesignResult');
        const contentDiv = document.getElementById('designResultContent');
        
        contentDiv.innerHTML = `
            <p><strong>Trial ID:</strong> ${result.trial_id}</p>
            <p><strong>Design Type:</strong> ${result.design_type}</p>
            <p><strong>Sample Size:</strong> ${result.sample_size} patients</p>
            <p><strong>Duration:</strong> ${result.duration_weeks} weeks</p>
            <p><strong>Arms:</strong> ${result.arms}</p>
            <p><strong>Primary Endpoint:</strong> ${result.primary_endpoint}</p>
        `;
        
        resultDiv.style.display = 'block';
        showAlert('Trial designed successfully!', 'success');
    } catch (error) {
        console.error('Error designing trial:', error);
        showAlert('Error designing trial', 'danger');
    }
}

// Validate data
async function validateData() {
    showAlert('Validating data quality...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/validate-data`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        const quality = result.quality_metrics.overall_quality_score;
        const validPatients = result.validation_results.valid_patients;
        const totalPatients = result.validation_results.total_patients;
        
        showAlert(
            `Data validation complete! Quality score: ${quality}% (${validPatients}/${totalPatients} valid patients)`,
            quality > 90 ? 'success' : quality > 70 ? 'warning' : 'danger'
        );
        
        loadDashboardData();
    } catch (error) {
        console.error('Error validating data:', error);
        showAlert('Error validating data', 'danger');
    }
}

// Export data
async function exportData() {
    showAlert('Exporting data to CSV...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/export/patients/csv`);
        const result = await response.json();
        
        showAlert(`Data exported successfully: ${result.filename}`, 'success');
    } catch (error) {
        console.error('Error exporting data:', error);
        showAlert('Error exporting data', 'danger');
    }
}

// Refresh dashboard
function refreshDashboard() {
    showAlert('Refreshing dashboard...', 'info');
    loadDashboardData();
}

// Utility functions
function setLoadingState(loading) {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        if (loading) {
            button.classList.add('loading');
        } else {
            button.classList.remove('loading');
        }
    });
}

function showAlert(message, type) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert-dismissible');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Error handling for fetch requests
function handleFetchError(error) {
    console.error('Fetch error:', error);
    showAlert('Network error occurred. Please check if the server is running.', 'danger');
}

// Add global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showAlert('An unexpected error occurred', 'danger');
});

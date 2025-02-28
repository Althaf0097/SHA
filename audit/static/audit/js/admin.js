// Admin Panel JavaScript

// District Management
function addDistrict(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch('/admin/district/add/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('Success', data.message, 'success');
            location.reload();
        } else {
            showToast('Error', data.message, 'error');
        }
    })
    .catch(error => {
        showToast('Error', 'An error occurred while adding the district', 'error');
    });
}

function editDistrict(districtId) {
    const name = prompt('Enter new district name:');
    if (name) {
        const formData = new FormData();
        formData.append('name', name);

        fetch(`/admin/district/${districtId}/edit/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('Success', data.message, 'success');
                location.reload();
            } else {
                showToast('Error', data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Error', 'An error occurred while updating the district', 'error');
        });
    }
}

function deleteDistrict(districtId) {
    if (confirm('Are you sure you want to delete this district?')) {
        fetch(`/admin/district/${districtId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('Success', data.message, 'success');
                location.reload();
            } else {
                showToast('Error', data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Error', 'An error occurred while deleting the district', 'error');
        });
    }
}

// User Management
function addUser(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch('/admin/user/add/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('Success', data.message, 'success');
            location.reload();
        } else {
            showToast('Error', data.message, 'error');
        }
    })
    .catch(error => {
        showToast('Error', 'An error occurred while adding the user', 'error');
    });
}

function editUser(userId) {
    // Get current user data and show in modal
    const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
    const form = document.getElementById('editUserForm');
    form.dataset.userId = userId;
    modal.show();
}

function submitEditUser(event) {
    event.preventDefault();
    const form = event.target;
    const userId = form.dataset.userId;
    const formData = new FormData(form);

    fetch(`/admin/user/${userId}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('Success', data.message, 'success');
            location.reload();
        } else {
            showToast('Error', data.message, 'error');
        }
    })
    .catch(error => {
        showToast('Error', 'An error occurred while updating the user', 'error');
    });
}

function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        fetch(`/admin/user/${userId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('Success', data.message, 'success');
                location.reload();
            } else {
                showToast('Error', data.message, 'error');
            }
        })
        .catch(error => {
            showToast('Error', 'An error occurred while deleting the user', 'error');
        });
    }
}

// Statistics
function loadStatistics() {
    fetch('/admin/statistics/')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateStatisticsCharts(data.data);
            }
        })
        .catch(error => {
            console.error('Error loading statistics:', error);
        });
}

function updateStatisticsCharts(data) {
    // Update audit status chart
    const auditStatusCtx = document.getElementById('auditStatusChart').getContext('2d');
    new Chart(auditStatusCtx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Pending', 'In Progress'],
            datasets: [{
                data: [
                    data.completed_audits,
                    data.pending_audits,
                    data.in_progress_audits
                ],
                backgroundColor: ['#28a745', '#ffc107', '#17a2b8']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Update district statistics chart
    const districtStatsCtx = document.getElementById('districtStatsChart').getContext('2d');
    new Chart(districtStatsCtx, {
        type: 'bar',
        data: {
            labels: data.district_stats.map(d => d.name),
            datasets: [
                {
                    label: 'Total Audits',
                    data: data.district_stats.map(d => d.audit_count),
                    backgroundColor: '#007bff'
                },
                {
                    label: 'Fraud Cases',
                    data: data.district_stats.map(d => d.fraud_count),
                    backgroundColor: '#dc3545'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showToast(title, message, type) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}:</strong> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    document.getElementById('toastContainer').appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Initialize tooltips and charts when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Load initial statistics
    loadStatistics();
});

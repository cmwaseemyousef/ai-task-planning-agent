// Main JavaScript for AI Task Planning Agent

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', autoResize);
        autoResize.call(textarea);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Search functionality
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }

    // Copy plan link functionality
    const copyButtons = document.querySelectorAll('.copy-link-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', copyPlanLink);
    });

    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (alert.classList.contains('auto-hide')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
});

// Auto-resize textarea function
function autoResize() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle search functionality
function handleSearch(event) {
    const query = event.target.value.trim();
    if (query.length >= 3 || query.length === 0) {
        // Automatically submit search after 3 characters or when cleared
        const form = event.target.closest('form');
        if (form) {
            form.submit();
        }
    }
}

// Copy plan link to clipboard
function copyPlanLink(event) {
    const button = event.target.closest('button');
    const planId = button.dataset.planId;
    const url = `${window.location.origin}/plan/${planId}`;
    
    navigator.clipboard.writeText(url).then(() => {
        // Show success feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
        button.classList.remove('btn-outline-secondary');
        button.classList.add('btn-success');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
        // Fallback: show URL in a prompt
        prompt('Copy this link:', url);
    });
}

// Format duration text
function formatDuration(duration) {
    if (!duration) return 'Unknown';
    
    // Convert various duration formats to a standardized format
    const text = duration.toLowerCase();
    
    if (text.includes('day')) {
        return duration.replace(/(\d+)\s*day/g, '$1d');
    } else if (text.includes('hour')) {
        return duration.replace(/(\d+)\s*hour/g, '$1h');
    } else if (text.includes('minute')) {
        return duration.replace(/(\d+)\s*minute/g, '$1m');
    }
    
    return duration;
}

// Weather icon mapping
function getWeatherIcon(description) {
    const desc = description.toLowerCase();
    
    if (desc.includes('clear')) return 'fas fa-sun';
    if (desc.includes('cloud')) return 'fas fa-cloud';
    if (desc.includes('rain')) return 'fas fa-rain';
    if (desc.includes('snow')) return 'fas fa-snowflake';
    if (desc.includes('storm')) return 'fas fa-bolt';
    if (desc.includes('mist') || desc.includes('fog')) return 'fas fa-smog';
    
    return 'fas fa-cloud-sun'; // default
}

// Plan card interactions
function initializePlanCards() {
    const planCards = document.querySelectorAll('.plan-card');
    
    planCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        });
    });
}

// API helpers
const API = {
    async getPlan(planId) {
        try {
            const response = await fetch(`/api/plans/${planId}`);
            if (!response.ok) throw new Error('Plan not found');
            return await response.json();
        } catch (error) {
            console.error('Error fetching plan:', error);
            throw error;
        }
    },

    async deletePlan(planId) {
        try {
            const response = await fetch(`/api/plans/${planId}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete plan');
            return await response.json();
        } catch (error) {
            console.error('Error deleting plan:', error);
            throw error;
        }
    },

    async getStats() {
        try {
            const response = await fetch('/api/stats');
            if (!response.ok) throw new Error('Failed to get stats');
            return await response.json();
        } catch (error) {
            console.error('Error fetching stats:', error);
            throw error;
        }
    }
};

// Utility functions
const Utils = {
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    truncateText(text, length = 100) {
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    },

    showToast(message, type = 'info') {
        // Create and show a Bootstrap toast
        const toastContainer = document.querySelector('.toast-container') || 
                             document.createElement('div');
        
        if (!document.querySelector('.toast-container')) {
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
};

// Export for use in other scripts
window.PlannerApp = {
    API,
    Utils,
    initializePlanCards,
    formatDuration,
    getWeatherIcon
};
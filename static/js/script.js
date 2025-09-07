// JavaScript for Email Spoofing Tool

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form submissions
    const emailForm = document.getElementById('emailForm');
    const testForm = document.getElementById('testForm');
    const serversForm = document.getElementById('serversForm');

    // Email form submission
    if (emailForm) {
        emailForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendEmail();
        });
    }

    // Test connection form submission
    if (testForm) {
        testForm.addEventListener('submit', function(e) {
            e.preventDefault();
            testConnection();
        });
    }

    // Test servers form submission
    if (serversForm) {
        serversForm.addEventListener('submit', function(e) {
            e.preventDefault();
            testServers();
        });
    }

    // Spoof check form submission
    const spoofForm = document.getElementById('spoofForm');
    if (spoofForm) {
        spoofForm.addEventListener('submit', function(e) {
            e.preventDefault();
            checkDomainSpoofing();
        });
    }

    // Tab switching - copy SMTP settings between tabs
    const smtpFields = ['smtp_server', 'smtp_port', 'username', 'password'];
    
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            const target = e.target.getAttribute('data-bs-target');
            
            if (target === '#test') {
                // Copy from send tab to test tab
                smtpFields.forEach(field => {
                    const sourceField = document.getElementById(field);
                    const targetField = document.getElementById('test_' + field);
                    if (sourceField && targetField) {
                        targetField.value = sourceField.value;
                    }
                });
            } else if (target === '#send') {
                // Copy from test tab to send tab
                smtpFields.forEach(field => {
                    const sourceField = document.getElementById('test_' + field);
                    const targetField = document.getElementById(field);
                    if (sourceField && targetField && sourceField.value) {
                        targetField.value = sourceField.value;
                    }
                });
            }
        });
    });

    // Auto-fill reply-to with from-email (only if reply-to is empty and user hasn't touched it)
    const fromEmailField = document.getElementById('from_email');
    const replyToField = document.getElementById('reply_to');
    
    if (fromEmailField && replyToField) {
        // Track if user has manually entered reply-to
        let userModifiedReplyTo = false;
        let initialReplyToValue = replyToField.value;
        
        // Only auto-fill on blur if reply-to is empty and user hasn't modified it
        fromEmailField.addEventListener('blur', function() {
            if (!replyToField.value.trim() && !userModifiedReplyTo) {
                replyToField.value = this.value;
            }
        });
        
        // Track when user manually enters reply-to
        replyToField.addEventListener('input', function() {
            userModifiedReplyTo = true;
        });
        
        // Track when user focuses on reply-to field (indicates intent to modify)
        replyToField.addEventListener('focus', function() {
            userModifiedReplyTo = true;
        });
        
        // Don't auto-fill on from_email input changes - only on blur
        // This prevents the annoying auto-fill while typing
    }

    // Dark mode toggle functionality
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
    
    function updateThemeIcon(theme) {
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
});

function showLoading(text = 'Please wait while we process your request.') {
    const loadingText = document.getElementById('loadingText');
    if (loadingText) {
        loadingText.textContent = text;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
}

function hideLoading() {
    const modalElement = document.getElementById('loadingModal');
    if (modalElement) {
        // Try to get existing modal instance
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        } else {
            // Create new modal instance and hide it
            const newModal = new bootstrap.Modal(modalElement);
            newModal.hide();
        }
        
        // Force cleanup after a short delay
        setTimeout(() => {
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
            modalElement.setAttribute('aria-hidden', 'true');
            modalElement.removeAttribute('aria-modal');
            modalElement.removeAttribute('role');
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            // Remove any remaining backdrop
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => backdrop.remove());
        }, 100);
    }
}

function showAlert(message, type = 'success') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());

    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function sendEmail() {
    showLoading('Sending email...');
    
    const formData = new FormData(document.getElementById('emailForm'));
    
    fetch('/send_email', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert(data.message, 'success');
            // Reset form
            document.getElementById('emailForm').reset();
        } else {
            showAlert(data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('An error occurred: ' + error.message, 'danger');
    });
}

function testConnection() {
    showLoading('Testing SMTP connection...');
    
    const formData = new FormData(document.getElementById('testForm'));
    
    fetch('/test_connection', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert(data.message, 'success');
        } else {
            showAlert(data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('An error occurred: ' + error.message, 'danger');
    });
}

function testServers() {
    showLoading('Testing SMTP servers...');
    
    const formData = new FormData(document.getElementById('serversForm'));
    
    fetch('/test_servers', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert(data.message, 'success');
            displayServerResults(data.working_servers);
        } else {
            showAlert(data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('An error occurred: ' + error.message, 'danger');
    });
}

function checkDomainSpoofing() {
    const domain = document.getElementById('domain_check').value.trim();
    if (!domain) {
        showAlert('Please enter a domain name', 'warning');
        return;
    }
    
    showLoading('Checking domain security...');
    
    fetch('/check_spoofing', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain: domain })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            displaySpoofResults(data.analysis);
        } else {
            showAlert(data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('An error occurred: ' + error.message, 'danger');
    });
}

function displayServerResults(servers) {
    const resultsDiv = document.getElementById('serversResults');
    const serversListDiv = document.getElementById('serversList');
    
    if (servers && servers.length > 0) {
        let html = '<div class="row">';
        
        servers.forEach(server => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="server-item server-success">
                        <div class="d-flex align-items-center">
                            <span class="status-indicator status-success"></span>
                            <div>
                                <h6 class="mb-1">${server.server}:${server.port}</h6>
                                <small class="text-muted">${server.username}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        serversListDiv.innerHTML = html;
        resultsDiv.style.display = 'block';
    } else {
        serversListDiv.innerHTML = '<p class="text-muted">No working servers found.</p>';
        resultsDiv.style.display = 'block';
    }
}

function displaySpoofResults(analysis) {
    const resultsDiv = document.getElementById('spoofResults');
    const analysisDiv = document.getElementById('spoofAnalysis');
    
    // Decorate DMARC policy display when policy is "none"
    const dmarcPolicyRaw = analysis.dmarc && analysis.dmarc.policy ? analysis.dmarc.policy : null;
    const dmarcPolicyDisplay = dmarcPolicyRaw === 'none' ? 'none (vulnerable)' : (dmarcPolicyRaw || 'Not found');
    
    let html = `
        <div class="row">
            <div class="col-md-12">
                <div class="card mb-3">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">Domain: ${analysis.domain}</h6>
                        <span class="badge ${analysis.overall_status === 'vulnerable' ? 'bg-danger' : analysis.overall_status === 'partially_secure' ? 'bg-danger' : 'bg-success'}">
                            ${analysis.overall_status === 'partially_secure' ? 'Potentially Spoofable' : analysis.overall_status.toUpperCase()}
                        </span>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>SPF Record</h6>
                                <p class="mb-1"><strong>Status:</strong> 
                                    <span class="badge ${analysis.spf.status === 'present' ? 'bg-success' : 'bg-danger'}">${analysis.spf.status}</span>
                                </p>
                                <p class="mb-1"><strong>Record:</strong> ${analysis.spf.record || 'Not found'}</p>
                                <p class="mb-0"><strong>Vulnerability:</strong> ${analysis.spf.vulnerable ? 'Yes' : 'No'}</p>
                            </div>
                            <div class="col-md-6">
                                <h6>DMARC Record</h6>
                                <p class="mb-1"><strong>Status:</strong> 
                                    <span class="badge ${analysis.dmarc.status === 'present' ? 'bg-success' : 'bg-danger'}">${analysis.dmarc.status}</span>
                                </p>
                                <p class="mb-1"><strong>Policy:</strong> ${dmarcPolicyDisplay}</p>
                                <p class="mb-1"><strong>Subdomain Policy (sp):</strong> ${analysis.dmarc.subdomain_policy ? (analysis.dmarc.subdomain_policy === 'none' ? 'none (vulnerable)' : analysis.dmarc.subdomain_policy) : 'Inherits primary policy'}</p>
                                <p class="mb-0"><strong>Vulnerability:</strong> ${analysis.dmarc.vulnerable ? 'Yes' : 'No'} | <strong>Subdomains Spoofable:</strong> ${analysis.dmarc.subdomain_vulnerable ? 'Yes' : 'No'}</p>
                            </div>
                        </div>
                        <hr>
                        <div class="alert ${analysis.overall_status === 'vulnerable' ? 'alert-danger' : analysis.overall_status === 'partially_secure' ? 'alert-danger' : 'alert-success'}">
                            <strong>Summary:</strong> ${analysis.summary}
                        </div>
                        <div class="mt-3">
                            <h6>Recommendations:</h6>
                            <ul class="mb-0">
                                ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    analysisDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

// Form validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
        
        // Email validation
        if (field.type === 'email' && field.value) {
            if (!validateEmail(field.value)) {
                field.classList.add('is-invalid');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

// Add form validation to all forms
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!validateForm(this.id)) {
            e.preventDefault();
            showAlert('Please fill in all required fields correctly.', 'warning');
        }
    });
});

// Real-time validation
document.querySelectorAll('input[required], textarea[required]').forEach(field => {
    field.addEventListener('blur', function() {
        if (this.value.trim()) {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
        } else {
            this.classList.remove('is-valid');
            this.classList.add('is-invalid');
        }
    });
});

// File upload validation
document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function() {
        const files = this.files;
        const maxSize = 16 * 1024 * 1024; // 16MB
        const allowedTypes = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'];
        
        for (let file of files) {
            // Check file size
            if (file.size > maxSize) {
                showAlert(`File ${file.name} is too large. Maximum size is 16MB.`, 'warning');
                this.value = '';
                return;
            }
            
            // Check file type
            const extension = file.name.split('.').pop().toLowerCase();
            if (!allowedTypes.includes(extension)) {
                showAlert(`File ${file.name} has an unsupported format.`, 'warning');
                this.value = '';
                return;
            }
        }
    });
});

// Auto-resize textarea
document.querySelectorAll('textarea').forEach(textarea => {
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
});

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('Copied to clipboard!', 'success');
    }, function(err) {
        showAlert('Failed to copy to clipboard', 'danger');
    });
}

// Add copy buttons to server results
function addCopyButtons() {
    document.querySelectorAll('.server-item').forEach(item => {
        const serverInfo = item.querySelector('h6').textContent;
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm btn-outline-primary ms-auto';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.onclick = () => copyToClipboard(serverInfo);
        
        const flexDiv = item.querySelector('.d-flex');
        flexDiv.appendChild(copyBtn);
    });
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to submit forms
    if (e.ctrlKey && e.key === 'Enter') {
        const activeForm = document.querySelector('form:not([style*="display: none"])');
        if (activeForm) {
            activeForm.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const modal = bootstrap.Modal.getInstance(document.querySelector('.modal.show'));
        if (modal) {
            modal.hide();
        }
    }
});

// Auto-save form data to localStorage
function saveFormData(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`form_${formId}`, JSON.stringify(data));
}

function loadFormData(formId) {
    const data = localStorage.getItem(`form_${formId}`);
    if (data) {
        const formData = JSON.parse(data);
        const form = document.getElementById(formId);
        
        Object.keys(formData).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field && field.type !== 'file') {
                field.value = formData[key];
            }
        });
    }
}

// Auto-save and load for all forms
document.querySelectorAll('form').forEach(form => {
    // Load saved data on page load
    loadFormData(form.id);
    
    // Save data on input change
    form.addEventListener('input', function() {
        saveFormData(this.id);
    });
    
    // Clear saved data on successful submit
    form.addEventListener('submit', function() {
        setTimeout(() => {
            localStorage.removeItem(`form_${this.id}`);
        }, 1000);
    });
});

// Enhanced form data management with dropdown suggestions
function saveFormField(fieldName, value) {
    if (!value.trim()) return;
    
    const key = `field_history_${fieldName}`;
    let history = JSON.parse(localStorage.getItem(key) || '[]');
    
    // Remove if already exists
    history = history.filter(item => item !== value);
    
    // Add to beginning
    history.unshift(value);
    
    // Keep only last 10 entries (5 for passwords for security)
    const maxEntries = fieldName === 'password' ? 5 : 10;
    history = history.slice(0, maxEntries);
    
    localStorage.setItem(key, JSON.stringify(history));
}

function loadFormFieldHistory(fieldName) {
    const key = `field_history_${fieldName}`;
    return JSON.parse(localStorage.getItem(key) || '[]');
}

function createDropdown(field, fieldName) {
    // Remove existing dropdown
    const existingDropdown = field.parentNode.querySelector('.dropdown-menu');
    if (existingDropdown) {
        existingDropdown.remove();
    }
    
    const history = loadFormFieldHistory(fieldName);
    if (history.length === 0) return;
    
    // Create dropdown container
    const dropdownContainer = document.createElement('div');
    dropdownContainer.className = 'position-relative';
    
    // Create dropdown menu
    const dropdownMenu = document.createElement('div');
    dropdownMenu.className = 'dropdown-menu show position-absolute w-100';
    dropdownMenu.style.zIndex = '1050';
    dropdownMenu.style.top = '100%';
    dropdownMenu.style.left = '0';
    
    history.forEach(item => {
        const dropdownItem = document.createElement('a');
        dropdownItem.className = 'dropdown-item';
        dropdownItem.href = '#';
        
        // For password fields, show plain text
        if (fieldName === 'password') {
            dropdownItem.textContent = item;
            dropdownItem.title = 'Click to use this password';
        } else {
            dropdownItem.textContent = item;
        }
        
        dropdownItem.addEventListener('click', function(e) {
            e.preventDefault();
            field.value = item;
            field.focus();
            dropdownMenu.remove();
        });
        dropdownMenu.appendChild(dropdownItem);
    });
    
    // Add clear history option for password fields
    if (fieldName === 'password' && history.length > 0) {
        const clearItem = document.createElement('a');
        clearItem.className = 'dropdown-item text-danger';
        clearItem.href = '#';
        clearItem.innerHTML = '<i class="fas fa-trash me-2"></i>Clear Password History';
        clearItem.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem(`field_history_${fieldName}`);
            dropdownMenu.remove();
            showAlert('Password history cleared', 'info');
        });
        dropdownMenu.appendChild(clearItem);
    }
    
    // Insert dropdown after field
    field.parentNode.insertBefore(dropdownContainer, field.nextSibling);
    dropdownContainer.appendChild(dropdownMenu);
    
    // Hide dropdown when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function hideDropdown(e) {
            if (!field.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.remove();
                document.removeEventListener('click', hideDropdown);
            }
        });
    }, 100);
}

// Add dropdown functionality to specific fields
const fieldsWithHistory = ['smtp_server', 'username', 'password', 'from_name', 'from_email', 'reply_to', 'to_email', 'cc', 'bcc', 'subject', 'domain_check'];
fieldsWithHistory.forEach(fieldName => {
    const field = document.getElementById(fieldName);
    if (field) {
        // Show dropdown on focus
        field.addEventListener('focus', function() {
            createDropdown(this, fieldName);
        });
        
        // Save field value on blur
        field.addEventListener('blur', function() {
            if (this.value.trim()) {
                saveFormField(fieldName, this.value.trim());
            }
        });
        
        // Show dropdown on keyup (for typing)
        field.addEventListener('keyup', function() {
            if (this.value.length > 0) {
                createDropdown(this, fieldName);
            }
        });
    }
});

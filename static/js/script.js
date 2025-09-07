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

    // DKIM check form submission
    const dkimForm = document.getElementById('dkimForm');
    if (dkimForm) {
        dkimForm.addEventListener('submit', function(e) {
            e.preventDefault();
            checkDKIM();
        });
    }

    // Headers analysis form submission
    const headersForm = document.getElementById('headersForm');
    if (headersForm) {
        headersForm.addEventListener('submit', function(e) {
            e.preventDefault();
            analyzeHeaders();
        });
    }
    


    // Report generation
    const generateReportBtn = document.getElementById('generateReportBtn');
    if (generateReportBtn) {
        generateReportBtn.addEventListener('click', function() {
            generateReport();
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

    // Enhanced form interactions
    enhanceFormInteractions();

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
    
    const modalElement = document.getElementById('loadingModal');
    if (modalElement) {
        // Force show the modal
        modalElement.style.display = 'block';
        modalElement.classList.add('show');
        modalElement.setAttribute('aria-modal', 'true');
        modalElement.removeAttribute('aria-hidden');
        document.body.classList.add('modal-open');
        
        // Create backdrop if it doesn't exist
        if (!document.querySelector('.modal-backdrop')) {
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            document.body.appendChild(backdrop);
        }
    }
}

function hideLoading() {
    const modalElement = document.getElementById('loadingModal');
    if (modalElement) {
        // Immediately force hide the modal
        modalElement.classList.remove('show');
        modalElement.style.display = 'none';
        modalElement.setAttribute('aria-hidden', 'true');
        modalElement.removeAttribute('aria-modal');
        modalElement.removeAttribute('role');
        
        // Clean up body classes and styles
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Remove any remaining backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // Try to properly hide using Bootstrap modal instance
        try {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        } catch (e) {
            // Silent fail - modal cleanup not critical
        }
    }
    
    // Reset all form buttons to their original state
    resetFormButtons();
}

function resetFormButtons() {
    document.querySelectorAll('button[type="submit"][data-original-text]').forEach(button => {
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.disabled = false;
            button.innerHTML = originalText;
            button.removeAttribute('data-original-text');
        }
    });
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
    const domainInput = document.getElementById('domain_check').value.trim();
    if (!domainInput) {
        showAlert('Please enter domain name(s)', 'warning');
        return;
    }
    
    // Check if multiple domains are provided (comma-separated)
    const domains = domainInput.split(',').map(d => d.trim()).filter(d => d);
    
    if (domains.length > 1) {
        // Multiple domains - use bulk analysis
        showLoading('Checking multiple domains...');
        
        fetch('/check_multiple_domains', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domains: domainInput })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                displayMultiDomainResults(data.results);
            } else {
                showAlert(data.error, 'danger');
            }
        })
        .catch(error => {
            hideLoading();
            showAlert('An error occurred: ' + error.message, 'danger');
        });
    } else {
        // Single domain - use original analysis
        showLoading('Checking domain security...');
        
        fetch('/check_spoofing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain: domains[0] })
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
        
        // Default allowed types for file uploads
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

// Enhanced form interactions for professional UI
function enhanceFormInteractions() {
    // Add loading states to buttons
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                button.disabled = true;
                const originalText = button.innerHTML;
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
                
                // Store original text for restoration
                button.setAttribute('data-original-text', originalText);
                
                // Re-enable button after 10 seconds as fallback
                setTimeout(() => {
                    button.disabled = false;
                    button.innerHTML = originalText;
                }, 10000);
            });
        }
    });

    // Enhanced password field toggle
    document.querySelectorAll('input[type="password"]').forEach(field => {
        const wrapper = document.createElement('div');
        wrapper.className = 'position-relative';
        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);
        
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'btn btn-outline-secondary position-absolute top-50 end-0 translate-middle-y me-2';
        toggleBtn.style.border = 'none';
        toggleBtn.style.background = 'none';
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        
        toggleBtn.addEventListener('click', function() {
            const type = field.type === 'password' ? 'text' : 'password';
            field.type = type;
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
        
        wrapper.appendChild(toggleBtn);
    });

    // Auto-resize textareas
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 300) + 'px';
        });
    });

    // Professional form validation styling
    document.querySelectorAll('input, textarea, select').forEach(field => {
        field.addEventListener('blur', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    });
}

// DKIM checking function
function checkDKIM() {
    const domain = document.getElementById('dkim_domain').value.trim();
    const selectorsInput = document.getElementById('dkim_selectors').value.trim();
    
    if (!domain) {
        showAlert('Please enter a domain name', 'warning');
        return;
    }
    
    showLoading('Checking DKIM records...');
    
    const requestData = { domain: domain };
    if (selectorsInput) {
        requestData.selectors = selectorsInput.split(',').map(s => s.trim());
    }
    
    fetch('/check_dkim', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            displayDKIMResults(data.analysis);
        } else {
            showAlert(data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('An error occurred: ' + error.message, 'danger');
    });
}

// Display DKIM results
function displayDKIMResults(analysis) {
    const resultsDiv = document.getElementById('dkimResults');
    const analysisDiv = document.getElementById('dkimAnalysis');
    
    let html = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">DKIM Analysis: ${analysis.domain}</h3>
            </div>
            <div class="card-body">
                <div class="alert ${analysis.selectors_found.length > 0 ? 'alert-success' : 'alert-warning'}">
                    <strong>Summary:</strong> ${analysis.summary}
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-4">
                        <div class="text-center">
                            <h5>${analysis.selectors_found.length}</h5>
                            <small class="text-muted">Selectors Found</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <h5>${analysis.valid_keys}</h5>
                            <small class="text-muted">Valid Keys</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <h5>${analysis.selectors_checked}</h5>
                            <small class="text-muted">Selectors Checked</small>
                        </div>
                    </div>
                </div>
    `;
    
    if (analysis.selectors_found.length > 0) {
        html += '<h6>DKIM Selectors Found:</h6>';
        analysis.selectors_found.forEach(selector => {
            html += `
                <div class="card mb-2">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6>${selector.selector}</h6>
                                <p class="mb-1"><strong>Valid:</strong> 
                                    <span class="badge ${selector.valid ? 'bg-success' : 'bg-danger'}">${selector.valid ? 'Yes' : 'No'}</span>
                                </p>
                                <p class="mb-1"><strong>Key Type:</strong> ${selector.key_type || 'Not specified'}</p>
                                <p class="mb-0"><strong>Algorithm:</strong> ${selector.algorithm || 'Not specified'}</p>
                            </div>
                        </div>
                        <details class="mt-2">
                            <summary class="text-muted small">View Raw Record</summary>
                            <pre class="mt-2 small">${selector.record}</pre>
                        </details>
                    </div>
                </div>
            `;
        });
    }
    
    if (analysis.recommendations.length > 0) {
        html += `
            <div class="mt-3">
                <h6>Recommendations:</h6>
                <ul>
                    ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    html += `
                <div class="mt-3">
                    <button class="btn btn-outline-primary btn-sm" onclick="showReportModal('dkim')">
                        <i class="fas fa-file-alt me-2"></i>Generate Report
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Store the analysis data globally for report generation
    window.currentAnalysisData = analysis;
    
    analysisDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

// Header analysis function
function analyzeHeaders() {
    const headers = document.getElementById('email_headers').value.trim();
    
    if (!headers) {
        showAlert('Please paste email headers', 'warning');
        return;
    }
    
    showLoading('Analyzing email headers...');
    
    fetch('/analyze_headers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ headers: headers })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        hideLoading(); // Hide loading after successful response
        if (data.success) {
            displayHeadersResults(data.analysis);
        } else {
            showAlert(data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading(); // Ensure loading is hidden on error
        showAlert('An error occurred: ' + error.message, 'danger');
    });
}

// Display header analysis results
function displayHeadersResults(analysis) {
    const resultsDiv = document.getElementById('headersResults');
    const analysisDiv = document.getElementById('headersAnalysis');
    
    const scoreClass = analysis.security_score >= 80 ? 'success' : analysis.security_score >= 60 ? 'warning' : 'danger';
    
    let html = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Email Header Analysis</h3>
            </div>
            <div class="card-body">
                <div class="alert alert-${scoreClass}">
                    <strong>Summary:</strong> ${analysis.summary}
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-3">
                        <div class="text-center">
                            <h5 class="text-${scoreClass}">${analysis.security_score}/100</h5>
                            <small class="text-muted">Security Score</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <span class="badge ${analysis.spf_result === 'pass' ? 'bg-success' : analysis.spf_result === 'fail' ? 'bg-danger' : 'bg-secondary'}">${analysis.spf_result || 'N/A'}</span>
                            <br><small class="text-muted">SPF Result</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <span class="badge ${analysis.dkim_result === 'pass' ? 'bg-success' : analysis.dkim_result === 'fail' ? 'bg-danger' : 'bg-secondary'}">${analysis.dkim_result || 'N/A'}</span>
                            <br><small class="text-muted">DKIM Result</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <span class="badge ${analysis.dmarc_result === 'pass' ? 'bg-success' : analysis.dmarc_result === 'fail' ? 'bg-danger' : 'bg-secondary'}">${analysis.dmarc_result || 'N/A'}</span>
                            <br><small class="text-muted">DMARC Result</small>
                        </div>
                    </div>
                </div>
    `;
    
    if (analysis.authentication_results.length > 0) {
        html += `
            <h6>Authentication Results:</h6>
            <div class="mb-3">
        `;
        analysis.authentication_results.forEach(result => {
            html += `<pre class="small">${result}</pre>`;
        });
        html += '</div>';
    }
    
    if (analysis.received_chain.length > 0) {
        html += `
            <details class="mb-3">
                <summary><h6>Email Routing Chain (${analysis.received_chain.length} hops)</h6></summary>
                <div class="mt-2">
        `;
        analysis.received_chain.forEach((received, index) => {
            html += `<div class="small mb-2"><strong>Hop ${index + 1}:</strong> ${received}</div>`;
        });
        html += '</div></details>';
    }
    
    if (analysis.suspicious_indicators.length > 0) {
        html += `
            <div class="alert alert-warning">
                <h6><i class="fas fa-exclamation-triangle me-2"></i>Suspicious Indicators:</h6>
                <ul class="mb-0">
                    ${analysis.suspicious_indicators.map(indicator => `<li>${indicator}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (analysis.recommendations.length > 0) {
        html += `
            <div class="mt-3">
                <h6>Recommendations:</h6>
                <ul>
                    ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    html += `
                <div class="mt-3">
                    <button class="btn btn-outline-primary btn-sm" onclick="showReportModal('headers')">
                        <i class="fas fa-file-alt me-2"></i>Generate Report
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Store the analysis data globally for report generation
    window.currentAnalysisData = analysis;
    
    analysisDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}


// Display multi-domain results
function displayMultiDomainResults(results) {
    const resultsDiv = document.getElementById('spoofResults');
    const analysisDiv = document.getElementById('spoofAnalysis');
    
    // Decorate DMARC policy display when policy is "none"
    const decoratePolicy = (policy) => policy === 'none' ? 'none (vulnerable)' : (policy || 'Not found');
    
    let html = `
        <div class="card mb-3">
            <div class="card-header">
                <h3 class="card-title">Multi-Domain Analysis Results</h3>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <strong>Summary:</strong> ${results.summary}
                </div>
                
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="text-center">
                            <h5 class="text-success">${results.secure_count}</h5>
                            <small class="text-muted">Secure</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h5 class="text-warning">${results.partially_secure_count}</h5>
                            <small class="text-muted">Potentially Spoofable</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h5 class="text-danger">${results.vulnerable_count}</h5>
                            <small class="text-muted">Vulnerable</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h5>${results.total_checked}</h5>
                            <small class="text-muted">Total Checked</small>
                        </div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <button class="btn btn-outline-primary btn-sm" onclick="showReportModal('multi-domain')">
                        <i class="fas fa-file-alt me-2"></i>Generate Report
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add detailed analysis for each domain
    results.domains.forEach((domain, index) => {
        const statusClass = domain.overall_status === 'secure' ? 'success' : domain.overall_status === 'partially_secure' ? 'warning' : 'danger';
        const statusText = domain.overall_status === 'partially_secure' ? 'Potentially Spoofable' : domain.overall_status.toUpperCase();
        const dmarcPolicyDisplay = decoratePolicy(domain.dmarc.policy);
        const dmarcSubdomainPolicyDisplay = domain.dmarc.subdomain_policy ? 
            (domain.dmarc.subdomain_policy === 'none' ? 'none (vulnerable)' : domain.dmarc.subdomain_policy) : 
            'Inherits primary policy';
        
        html += `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Domain: ${domain.domain}</h6>
                    <span class="badge ${domain.overall_status === 'vulnerable' ? 'bg-danger' : domain.overall_status === 'partially_secure' ? 'bg-danger' : 'bg-success'}">
                        ${statusText}
                    </span>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>SPF Record</h6>
                            <p class="mb-1"><strong>Status:</strong> 
                                <span class="badge ${domain.spf.status === 'present' ? 'bg-success' : 'bg-danger'}">${domain.spf.status}</span>
                            </p>
                            <p class="mb-1"><strong>Record:</strong> ${domain.spf.record || 'Not found'}</p>
                            <p class="mb-0"><strong>Vulnerability:</strong> ${domain.spf.vulnerable ? 'Yes' : 'No'}</p>
                        </div>
                        <div class="col-md-6">
                            <h6>DMARC Record</h6>
                            <p class="mb-1"><strong>Status:</strong> 
                                <span class="badge ${domain.dmarc.status === 'present' ? 'bg-success' : 'bg-danger'}">${domain.dmarc.status}</span>
                            </p>
                            <p class="mb-1"><strong>Policy:</strong> ${dmarcPolicyDisplay}</p>
                            <p class="mb-1"><strong>Subdomain Policy (sp):</strong> ${dmarcSubdomainPolicyDisplay}</p>
                            <p class="mb-0"><strong>Vulnerability:</strong> ${domain.dmarc.vulnerable ? 'Yes' : 'No'} | <strong>Subdomains Spoofable:</strong> ${domain.dmarc.subdomain_vulnerable ? 'Yes' : 'No'}</p>
                        </div>
                    </div>
                    <hr>
                    <div class="alert ${domain.overall_status === 'vulnerable' ? 'alert-danger' : domain.overall_status === 'partially_secure' ? 'alert-danger' : 'alert-success'}">
                        <strong>Summary:</strong> ${domain.summary}
                    </div>
                    ${domain.recommendations.length > 0 ? `
                        <div class="mt-3">
                            <h6>Recommendations:</h6>
                            <ul class="mb-0">
                                ${domain.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    // Store the results data globally for report generation
    window.currentAnalysisData = results;
    
    analysisDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

// Show report modal
function showReportModal(type) {
    const modal = new bootstrap.Modal(document.getElementById('reportModal'));
    modal.show();
    
    // Store data for report generation using the globally stored analysis data
    if (window.currentAnalysisData) {
        window.reportData = { type: type, data: window.currentAnalysisData };
    } else {
        showAlert('No analysis data available for report generation', 'warning');
        return;
    }
}

// Generate report
function generateReport() {
    if (!window.reportData) {
        showAlert('No data available for report generation', 'warning');
        return;
    }
    
    const format = document.getElementById('reportFormat').value;
    const reportData = {};
    reportData[window.reportData.type] = window.reportData.data;
    
    showLoading('Generating report...');
    
    fetch('/generate_report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            data: reportData,
            format: format 
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            if (data.format === 'html') {
                // Open HTML report in new window
                const newWindow = window.open();
                newWindow.document.write(data.report);
                newWindow.document.close();
            } else {
                // Download JSON report
                const blob = new Blob([JSON.stringify(data.report, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `security-report-${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
            modal.hide();
            
            showAlert('Report generated successfully!', 'success');
        } else {
            showAlert(data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('An error occurred: ' + error.message, 'danger');
    });
}


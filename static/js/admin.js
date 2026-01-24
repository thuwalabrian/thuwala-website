// Admin Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile menu
    initMobileMenu();
    
    // Initialize modals
    initModals();
    
    // Initialize status indicators
    initStatusIndicators();
    
    // Initialize interactive elements
    initInteractiveElements();
    
    // Initialize portfolio features if on portfolio page
    initPortfolioFeatures();
    
    // Initialize service form features if on service page
    initServiceFormFeatures();
});

// Mobile menu functionality
function initMobileMenu() {
    const toggleBtn = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('adminSidebar');
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
                    sidebar.classList.remove('active');
                }
            }
        });
    }
}

// Modal functionality
function initModals() {
    // Message modal functionality
    const messageModalOverlay = document.getElementById('messageModalOverlay');
    const messageModalContent = document.getElementById('messageModalContent');
    
    // Close modals with escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
    
    // Close modals when clicking outside
    if (messageModalOverlay) {
        messageModalOverlay.addEventListener('click', (e) => {
            if (e.target === messageModalOverlay) {
                closeModal(messageModalOverlay);
            }
        });
    }
}

function openModal(modalElement) {
    if (modalElement) {
        modalElement.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalElement) {
    if (modalElement) {
        modalElement.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => {
        closeModal(modal);
    });
}

// Message viewing
async function viewMessage(messageId) {
    try {
        const response = await fetch(`/admin/message/${messageId}/view`);
        const data = await response.json();
        
        if (data.success) {
            const modalContent = document.getElementById('messageModalContent');
            const modalOverlay = document.getElementById('messageModalOverlay');
            
            if (modalContent && modalOverlay) {
                modalContent.innerHTML = `
                    <div class="message-modal-content">
                        <div class="sender-info">
                            <div class="sender-avatar">${data.message.name[0]}</div>
                            <div>
                                <h3>${data.message.name}</h3>
                                <p>${data.message.email}</p>
                            </div>
                        </div>
                        <div class="message-meta">
                            <div class="meta-item">
                                <i class="fas fa-clock"></i>
                                <span>${data.message.created_at}</span>
                            </div>
                            <div class="meta-item">
                                <i class="fas fa-phone"></i>
                                <span>${data.message.phone || 'Not provided'}</span>
                            </div>
                        </div>
                        
                        <div class="message-subject">
                            <i class="fas fa-tag"></i>
                            <strong>Subject:</strong>
                            <span>${data.message.subject || 'No Subject'}</span>
                        </div>
                        
                        <div class="message-body">
                            <div class="message-text">${data.message.message}</div>
                        </div>
                        
                        <div class="form-actions">
                            <a href="mailto:${data.message.email}" class="btn btn-primary">
                                <i class="fas fa-reply"></i> Reply
                            </a>
                            <button class="btn btn-secondary" onclick="closeAllModals()">
                                <i class="fas fa-times"></i> Close
                            </button>
                        </div>
                    </div>
                `;
                openModal(modalOverlay);
            }
        } else {
            showToast('Error loading message', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error loading message', 'error');
    }
}

// Status indicators animation
function initStatusIndicators() {
    const indicators = document.querySelectorAll('.status-indicator.online');
    indicators.forEach(indicator => {
        indicator.style.animation = 'pulse 2s infinite';
    });
}

// Interactive elements
function initInteractiveElements() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.stat-card, .card, .action-item, .service-management-card, .portfolio-management-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transition = 'all 0.3s ease';
        });
    });
    
    // Confirmation for delete actions
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
    
    // Update active nav item based on current page
    updateActiveNav();
}

// Update active navigation based on current URL
function updateActiveNav() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href.replace('/admin/', ''))) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Portfolio Form Functions
function initPortfolioForm() {
    // Get all form elements with data-preview attribute
    const formElements = document.querySelectorAll('[data-preview]');
    const previewElements = {};
    
    // Initialize preview elements mapping
    document.querySelectorAll('[id^="preview"]').forEach(el => {
        const key = el.id.replace('preview', '').toLowerCase();
        previewElements[key] = el;
    });
    
    // Add event listeners to form elements
    formElements.forEach(element => {
        const previewKey = element.dataset.preview;
        
        element.addEventListener('input', function() {
            updatePortfolioPreview(previewKey, this.value, this.type);
        });
        
        element.addEventListener('change', function() {
            updatePortfolioPreview(previewKey, this.value, this.type, this.checked);
        });
        
        // Initial update
        if (element.type === 'checkbox') {
            updatePortfolioPreview(previewKey, element.value, element.type, element.checked);
        } else {
            updatePortfolioPreview(previewKey, element.value, element.type);
        }
    });
    
    // Handle file upload preview
    const imageFileInput = document.getElementById('image_file');
    if (imageFileInput) {
        imageFileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (previewElements.image) {
                        previewElements.image.src = e.target.result;
                        const imageUrlInput = document.getElementById('image_url');
                        if (imageUrlInput) {
                            imageUrlInput.value = '';
                        }
                    }
                };
                reader.readAsDataURL(this.files[0]);
                
                // Update file info
                const fileInfo = document.getElementById('fileInfo');
                if (fileInfo) {
                    fileInfo.textContent = this.files[0].name;
                }
            }
        });
    }
    
    // Handle tags input for technologies
    const technologiesInput = document.getElementById('technologies');
    if (technologiesInput) {
        const tagsPreview = document.getElementById('tagsPreview');
        
        technologiesInput.addEventListener('keydown', function(e) {
            if (e.key === ',' || e.key === 'Enter') {
                e.preventDefault();
                updateTechTags();
            }
        });
        
        technologiesInput.addEventListener('blur', updateTechTags);
        
        function updateTechTags() {
            const tags = technologiesInput.value.split(',')
                .filter(tag => tag.trim())
                .map(tag => tag.trim());
            
            if (tagsPreview) {
                tagsPreview.innerHTML = '';
                tags.forEach(tag => {
                    const tagElement = document.createElement('span');
                    tagElement.className = 'tech-tag-preview';
                    tagElement.textContent = tag;
                    tagsPreview.appendChild(tagElement);
                });
            }
            
            // Update main preview
            if (previewElements.tech) {
                previewElements.tech.innerHTML = '';
                tags.slice(0, 5).forEach(tag => {
                    const tagElement = document.createElement('span');
                    tagElement.className = 'tech-tag';
                    tagElement.textContent = tag;
                    previewElements.tech.appendChild(tagElement);
                });
                
                if (tags.length > 5) {
                    const moreTag = document.createElement('span');
                    moreTag.className = 'tech-tag';
                    moreTag.textContent = `+${tags.length - 5}`;
                    previewElements.tech.appendChild(moreTag);
                }
                
                if (tags.length === 0) {
                    ['Technology', 'Tools', 'Platform'].forEach(text => {
                        const placeholderTag = document.createElement('span');
                        placeholderTag.className = 'tech-tag placeholder';
                        placeholderTag.textContent = text;
                        previewElements.tech.appendChild(placeholderTag);
                    });
                }
            }
        }
        
        // Initial update
        updateTechTags();
    }
    
    function updatePortfolioPreview(key, value, type, checked = false) {
        const previewElement = previewElements[key];
        if (!previewElement) return;
        
        switch (type) {
            case 'checkbox':
                previewElement.style.display = checked ? 'flex' : 'none';
                break;
                
            case 'select-one':
                if (value) {
                    previewElement.textContent = value.charAt(0).toUpperCase() + value.slice(1);
                }
                break;
                
            case 'textarea':
                if (key === 'description') {
                    const truncated = value.length > 150 ? value.substring(0, 150) + '...' : value;
                    previewElement.textContent = truncated || 'Project description will appear here...';
                }
                break;
                
            case 'url':
                if (key === 'image' && value) {
                    previewElement.src = value;
                }
                break;
                
            default:
                if (value) {
                    previewElement.textContent = value;
                } else {
                    // Set default placeholder based on key
                    const placeholders = {
                        title: 'Project Title',
                        client: 'Client Name',
                        category: 'Category'
                    };
                    previewElement.textContent = placeholders[key] || '';
                }
        }
    }
}

// Service Form Functions
function initServiceFormFeatures() {
    const serviceForm = document.querySelector('.modern-form');
    if (!serviceForm) return;
    
    // Get form elements
    const titleInput = document.getElementById('title');
    const descriptionInput = document.getElementById('description');
    const iconInput = document.getElementById('icon');
    const categorySelect = document.getElementById('category');
    const iconPreview = document.getElementById('iconPreview');
    const previewIcon = document.getElementById('previewIcon');
    const previewTitle = document.getElementById('previewTitle');
    const previewDescription = document.getElementById('previewDescription');
    const previewCategory = document.getElementById('previewCategory');
    const iconOptions = document.querySelectorAll('.icon-option');
    
    // Update preview in real-time
    if (titleInput && previewTitle) {
        titleInput.addEventListener('input', function() {
            previewTitle.textContent = this.value || 'Service Title';
        });
    }
    
    if (descriptionInput && previewDescription) {
        descriptionInput.addEventListener('input', function() {
            previewDescription.textContent = this.value || 'Service description will appear here...';
        });
    }
    
    if (iconInput && iconPreview && previewIcon) {
        iconInput.addEventListener('input', function() {
            const iconClass = this.value.trim();
            iconPreview.className = iconClass;
            previewIcon.className = iconClass;
        });
    }
    
    if (categorySelect && previewCategory) {
        categorySelect.addEventListener('change', function() {
            previewCategory.textContent = this.value || 'category';
        });
    }
    
    // Icon selection from gallery
    if (iconOptions.length > 0) {
        iconOptions.forEach(option => {
            option.addEventListener('click', function() {
                const iconClass = this.getAttribute('data-icon');
                if (iconInput) iconInput.value = iconClass;
                if (iconPreview) iconPreview.className = iconClass;
                if (previewIcon) previewIcon.className = iconClass;
                
                // Update active state
                iconOptions.forEach(opt => opt.classList.remove('active'));
                this.classList.add('active');
            });
        });
        
        // Initialize icon gallery active state
        if (iconInput) {
            const currentIcon = iconInput.value;
            iconOptions.forEach(option => {
                if (option.getAttribute('data-icon') === currentIcon) {
                    option.classList.add('active');
                }
            });
        }
    }
    
    // Form validation
    if (serviceForm) {
        serviceForm.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = this.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('error');
                    isValid = false;
                    
                    // Add error message
                    if (!field.nextElementSibling?.classList.contains('error-message')) {
                        const errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'This field is required';
                        field.parentNode.appendChild(errorMsg);
                    }
                } else {
                    field.classList.remove('error');
                    const errorMsg = field.parentNode.querySelector('.error-message');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'error');
            }
        });
    }
}

// Portfolio features initialization
function initPortfolioFeatures() {
    // Only initialize if we're on a portfolio edit page
    const portfolioForm = document.querySelector('.modern-form');
    if (!portfolioForm || !document.getElementById('title')) return;
    
    initPortfolioForm();
    initPortfolioValidation();
    initPortfolioEvents();
}

function initPortfolioValidation() {
    const form = document.querySelector('.modern-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        let isValid = true;
        const requiredFields = this.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                isValid = false;
                
                // Add error message
                if (!field.nextElementSibling?.classList.contains('error-message')) {
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'error-message';
                    errorMsg.textContent = 'This field is required';
                    field.parentNode.appendChild(errorMsg);
                }
            } else {
                field.classList.remove('error');
                const errorMsg = field.parentNode.querySelector('.error-message');
                if (errorMsg) {
                    errorMsg.remove();
                }
            }
        });
        
        // Validate image URL if provided
        const imageUrl = document.getElementById('image_url');
        if (imageUrl && imageUrl.value) {
            try {
                new URL(imageUrl.value);
                imageUrl.classList.remove('error');
                const errorMsg = imageUrl.parentNode.querySelector('.error-message');
                if (errorMsg) {
                    errorMsg.remove();
                }
            } catch (_) {
                imageUrl.classList.add('error');
                if (!imageUrl.nextElementSibling?.classList.contains('error-message')) {
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'error-message';
                    errorMsg.textContent = 'Please enter a valid URL';
                    imageUrl.parentNode.appendChild(errorMsg);
                }
                isValid = false;
            }
        }
        
        if (!isValid) {
            e.preventDefault();
            showToast('Please fill in all required fields correctly', 'error');
        }
    });
}

function initPortfolioEvents() {
    // Category color coding
    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const categoryBadge = document.getElementById('previewCategory');
            if (categoryBadge) {
                // Add category-specific color classes
                const colors = {
                    'web': 'blue',
                    'mobile': 'green',
                    'design': 'purple',
                    'consulting': 'orange',
                    'analytics': 'teal',
                    'data': 'indigo',
                    'branding': 'pink',
                    'business': 'yellow',
                    'systems': 'cyan',
                    'training': 'emerald'
                };
                
                // Remove existing color classes
                Object.values(colors).forEach(color => {
                    categoryBadge.classList.remove(`badge-${color}`);
                });
                
                // Add new color class
                const colorClass = colors[this.value] || 'blue';
                categoryBadge.classList.add(`badge-${colorClass}`);
            }
        });
        
        // Trigger initial color
        if (categorySelect.value) {
            categorySelect.dispatchEvent(new Event('change'));
        }
    }
    
    // Auto-format technologies input
    const techInput = document.getElementById('technologies');
    if (techInput) {
        techInput.addEventListener('blur', function() {
            // Clean up the input: remove extra spaces, proper capitalization
            const tags = this.value.split(',')
                .filter(tag => tag.trim())
                .map(tag => tag.trim().charAt(0).toUpperCase() + tag.trim().slice(1).toLowerCase());
            
            this.value = tags.join(', ');
        });
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    // Remove existing toasts
    document.querySelectorAll('.toast').forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles for toast
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 9999;
        max-width: 350px;
        animation: toastSlideIn 0.3s ease;
    `;
    
    const toastContent = toast.querySelector('.toast-content');
    toastContent.style.cssText = `
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex: 1;
    `;
    
    const toastIcon = toastContent.querySelector('i');
    toastIcon.style.cssText = `
        font-size: 1.25rem;
        color: ${getToastColor(type)};
    `;
    
    toastContent.querySelector('span').style.cssText = `
        font-size: 0.875rem;
        color: var(--dark);
    `;
    
    const toastClose = toast.querySelector('.toast-close');
    toastClose.style.cssText = `
        background: none;
        border: none;
        color: var(--gray);
        cursor: pointer;
        font-size: 1rem;
        padding: 0.25rem;
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'toastSlideOut 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }, 5000);
    
    // Add CSS animations if not already present
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            @keyframes toastSlideIn {
                from {
                    opacity: 0;
                    transform: translateX(100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            @keyframes toastSlideOut {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getToastColor(type) {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    return colors[type] || '#3b82f6';
}

// Export functions for use in templates
window.viewMessage = viewMessage;
window.openModal = openModal;
window.closeModal = closeModal;
window.closeAllModals = closeAllModals;
window.showToast = showToast;
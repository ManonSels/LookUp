// Form interaction handlers
function initializeFormHandlers() {
    // Publish toggle functionality
    const publishToggle = document.getElementById('publishToggle');
    const isPublishedInput = document.getElementById('is_published');
    
    if (publishToggle && isPublishedInput) {
        publishToggle.addEventListener('click', function() {
            const isCurrentlyPublished = isPublishedInput.checked;
            
            if (isCurrentlyPublished) {
                isPublishedInput.checked = false;
                this.textContent = 'Draft';
                this.classList.remove('published');
                this.classList.add('draft');
            } else {
                isPublishedInput.checked = true;
                this.textContent = 'Published';
                this.classList.remove('draft');
                this.classList.add('published');
            }
        });
    }

    // Color picker functionality
    const colorInputs = document.querySelectorAll('.color-picker-input');
    colorInputs.forEach(input => {
        input.addEventListener('input', function() {
            const previewId = this.id.replace('_light', 'PreviewLight').replace('_dark', 'PreviewDark');
            const preview = document.getElementById(previewId);
            if (preview) {
                preview.textContent = this.value;
                preview.style.backgroundColor = this.value;
                
                // Update text color for better contrast
                const hex = this.value.replace('#', '');
                const r = parseInt(hex.substr(0, 2), 16);
                const g = parseInt(hex.substr(2, 2), 16);
                const b = parseInt(hex.substr(4, 2), 16);
                const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
                preview.style.color = brightness > 128 ? 'black' : 'white';
            }
        });
        
        // Initialize preview on load
        const previewId = input.id.replace('_light', 'PreviewLight').replace('_dark', 'PreviewDark');
        const preview = document.getElementById(previewId);
        if (preview) {
            preview.style.backgroundColor = input.value;
            
            // Set initial text color
            const hex = input.value.replace('#', '');
            const r = parseInt(hex.substr(0, 2), 16);
            const g = parseInt(hex.substr(2, 2), 16);
            const b = parseInt(hex.substr(4, 2), 16);
            const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000;
            preview.style.color = brightness > 128 ? 'black' : 'white';
        }
    });
    
    // Auto-save functionality for forms
    initializeAutoSave();
}

// Auto-save functionality
function initializeAutoSave() {
    const forms = document.querySelectorAll('form.topic-form, form.item-form, form.category-form');
    
    forms.forEach(form => {
        const formId = form.id || `form-${Math.random().toString(36).substr(2, 9)}`;
        const inputs = form.querySelectorAll('input, textarea, select');
        let saveTimeout;
        
        // Save function
        const saveFormState = () => {
            const formData = {};
            inputs.forEach(input => {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    formData[input.name] = input.checked;
                } else {
                    formData[input.name] = input.value;
                }
            });
            localStorage.setItem(`autosave-${formId}`, JSON.stringify(formData));
        };
        
        // Restore function
        const restoreFormState = () => {
            const saved = localStorage.getItem(`autosave-${formId}`);
            if (saved) {
                try {
                    const formData = JSON.parse(saved);
                    inputs.forEach(input => {
                        if (input.name in formData) {
                            if (input.type === 'checkbox' || input.type === 'radio') {
                                input.checked = formData[input.name];
                            } else {
                                input.value = formData[input.name];
                            }
                            
                            // Trigger change events for dependent elements
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    });
                    
                    // Show restore notification
                    showAutoSaveNotification('Form data restored from previous session');
                } catch (e) {
                    console.error('Error restoring form data:', e);
                }
            }
        };
        
        // Auto-save on input with debounce
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(saveFormState, 1000);
            });
            
            input.addEventListener('change', () => {
                clearTimeout(saveTimeout);
                saveFormState();
            });
        });
        
        // Clear on successful submit
        form.addEventListener('submit', () => {
            clearTimeout(saveTimeout);
            localStorage.removeItem(`autosave-${formId}`);
        });
        
        // Restore on page load if form hasn't been submitted
        if (!form.querySelector('[data-submitted]')) {
            setTimeout(restoreFormState, 100);
        }
    });
}

function showAutoSaveNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'alert alert-success';
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 1000;
        max-width: 300px;
    `;
    notification.innerHTML = `
        <div>${message}</div>
        <button onclick="this.parentElement.remove()" style="
            background: none;
            border: none;
            color: inherit;
            cursor: pointer;
            float: right;
            margin-left: 1rem;
        ">×</button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeFormHandlers);
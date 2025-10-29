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
            }
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeFormHandlers);
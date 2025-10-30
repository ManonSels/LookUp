// Admin dashboard drag and drop functionality
function updateAdminTopicColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.querySelectorAll('.topic-card.admin').forEach(card => {
        const lightColor = card.getAttribute('data-color-light') || '#ffffff';
        const darkColor = card.getAttribute('data-color-dark') || '#1a1a1a';
        const color = isDark ? darkColor : lightColor;
        
        // Update the color indicator - ONLY set the indicator background
        const colorIndicator = card.querySelector('.topic-color-indicator');
        if (colorIndicator) {
            colorIndicator.style.backgroundColor = color;
        }
        
        // Remove any background color from the admin card itself - use default theme background
        card.style.backgroundColor = '';
        card.style.removeProperty('background-color');
    });
}

function initializeDashboardDragDrop() {
    console.log('Initializing drag and drop...');
    
    // Initial color update
    updateAdminTopicColors();
    
    // Update when theme changes
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            setTimeout(updateAdminTopicColors, 100);
        });
    }
    
    // Store the original category of each topic when drag starts
    let originalCategories = new Map();
    const topicLists = document.querySelectorAll('.topics-list');
    
    topicLists.forEach(topicList => {
        const categoryId = topicList.getAttribute('id').replace('topics-list-', '');
        console.log(`Initializing category ${categoryId}`);
        
        new Sortable(topicList, {
            group: {
                name: 'topics',
                pull: true,
                put: true
            },
            handle: '.topic-handle .handle-icon',
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            
            // When drag starts
            onStart: function(evt) {
                const topicId = evt.item.getAttribute('data-topic-id');
                const fromCategoryId = evt.from.getAttribute('id').replace('topics-list-', '');
                originalCategories.set(topicId, fromCategoryId);
                console.log(`Started dragging topic ${topicId} from category ${fromCategoryId}`);
            },
            
            // When item is added to a new list (category change)
            onAdd: function(evt) {
                const topicId = evt.item.getAttribute('data-topic-id');
                const newCategoryId = evt.to.getAttribute('id').replace('topics-list-', '');
                const oldCategoryId = originalCategories.get(topicId);
                
                console.log(`Topic ${topicId} moved from category ${oldCategoryId} to ${newCategoryId}`);
                updateTopicCategory(topicId, newCategoryId, oldCategoryId);
            },
            
            // When order changes within the same category
            onUpdate: function(evt) {
                const categoryId = evt.to.getAttribute('id').replace('topics-list-', '');
                console.log(`Order changed in category ${categoryId}`);
                updateTopicOrderInCategory(categoryId);
            },
            
            // When drag ends
            onEnd: function(evt) {
                const topicId = evt.item.getAttribute('data-topic-id');
                originalCategories.delete(topicId);
            }
        });
    });

    function updateTopicCategory(topicId, newCategoryId, oldCategoryId) {
        console.log(`Updating topic ${topicId} to category ${newCategoryId}`);
        
        fetch("/admin/api/topics/change_category", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic_id: parseInt(topicId),
                category_id: parseInt(newCategoryId)
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log(`Successfully updated topic ${topicId} category`);
                const topicCard = document.querySelector(`[data-topic-id="${topicId}"]`);
                if (topicCard) {
                    topicCard.setAttribute('data-category-id', newCategoryId);
                }
                updateCategoryCounts();
                updateTopicOrderInCategory(newCategoryId);
                showFlashMessage('Topic category updated successfully!', 'success');

            } else {
                throw new Error(data.error || 'Unknown error');
            }
        })
        .catch(error => {
            console.error('Error changing topic category:', error);
            showFlashMessage('Error changing topic category: ' + error.message, 'error');
            revertTopicToCategory(topicId, oldCategoryId);
        });
    }

    function updateTopicOrderInCategory(categoryId) {
        const topicList = document.getElementById(`topics-list-${categoryId}`);
        const topicIds = Array.from(topicList.querySelectorAll('.topic-card'))
            .map(card => card.getAttribute('data-topic-id'));
        
        console.log(`Updating order for category ${categoryId}:`, topicIds);
        
        if (topicIds.length === 0) return;
        
        fetch("/admin/api/topics/reorder", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                category_id: parseInt(categoryId),
                order: topicIds
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log(`Successfully updated topic order for category ${categoryId}`);
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        })
        .catch(error => {
            console.error('Error reordering topics:', error);
            showFlashMessage('Error reordering topics: ' + error.message, 'error');
        });
    }

    function revertTopicToCategory(topicId, categoryId) {
        const topicCard = document.querySelector(`[data-topic-id="${topicId}"]`);
        const targetList = document.getElementById(`topics-list-${categoryId}`);
        
        if (topicCard && targetList) {
            targetList.appendChild(topicCard);
            topicCard.setAttribute('data-category-id', categoryId);
            updateCategoryCounts();
        }
    }

    function updateCategoryCounts() {
        document.querySelectorAll('.category-column').forEach(column => {
            const categoryId = column.getAttribute('data-category-id');
            const topicList = column.querySelector('.topics-list');
            const topicCount = topicList.querySelectorAll('.topic-card').length;
            const countElement = column.querySelector('.topic-count');
            
            if (countElement) {
                countElement.textContent = topicCount + ' topic' + (topicCount !== 1 ? 's' : '');
            }
        });
    }

    function showFlashMessage(message, type) {
        const flashDiv = document.createElement('div');
        flashDiv.className = `alert alert-${type}`;
        flashDiv.textContent = message;
        
        const adminHeader = document.querySelector('.admin-header');
        if (adminHeader) {
            adminHeader.parentNode.insertBefore(flashDiv, adminHeader.nextSibling);
            
            setTimeout(() => {
                flashDiv.remove();
            }, 3000);
        }
    }
    
    console.log('Drag and drop initialized successfully');
}

// Initialize when DOM is loaded
if (document.querySelector('.categories-container')) {
    document.addEventListener('DOMContentLoaded', initializeDashboardDragDrop);
}
// Sections and items management functionality
function initializeSectionsManagement() {
    const topicIdElement = document.getElementById('topic-data');
    const topicId = topicIdElement ? topicIdElement.getAttribute('data-topic-id') : null;

    if (!topicId) {
        console.error('Topic ID not found');
        return;
    }

    // Section drag & drop
    const sectionsList = document.getElementById('sections-list');
    if (sectionsList) {
        const sectionSortable = Sortable.create(sectionsList, {
            handle: '.section-handle .handle-icon',
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            onEnd: function(evt) {
                const sectionIds = Array.from(sectionsList.querySelectorAll('.section-card'))
                    .map(card => card.getAttribute('data-section-id'));
                
                fetch("/admin/api/sections/reorder", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        topic_id: parseInt(topicId),
                        order: sectionIds
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        alert('Error reordering sections: ' + (data.error || 'Unknown error'));
                        sectionSortable.sort(sectionIds);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error reordering sections. Please check the console.');
                });
            }
        });
    }

    // Item drag & drop for each section
    document.querySelectorAll('[id^="items-list-"]').forEach(itemsList => {
        const sectionId = itemsList.id.replace('items-list-', '');
        
        const itemSortable = Sortable.create(itemsList, {
            group: {
                name: 'items',
                pull: true,
                put: true
            },
            handle: '.item-handle .handle-icon',
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            filter: '[data-no-drag]',
            onEnd: function(evt) {
                const fromSectionId = evt.from.getAttribute('data-section-id');
                const toSectionId = evt.to.getAttribute('data-section-id');
                const itemId = evt.item.getAttribute('data-item-id');
                
                // If item moved to a different section, update its section_id
                if (fromSectionId !== toSectionId) {
                    updateItemSection(itemId, toSectionId, fromSectionId);
                } else {
                    // Same section, just update order
                    updateItemOrderInSection(toSectionId);
                }
                
                // Update empty state visibility for both sections
                updateEmptyState(fromSectionId);
                updateEmptyState(toSectionId);
            },
            onAdd: function(evt) {
                const toSectionId = evt.to.getAttribute('data-section-id');
                updateEmptyState(toSectionId);
            },
            onRemove: function(evt) {
                const fromSectionId = evt.from.getAttribute('data-section-id');
                updateEmptyState(fromSectionId);
            }
        });
        
        // Initialize empty state
        updateEmptyState(sectionId);
    });

    // Function to update empty state visibility
    function updateEmptyState(sectionId) {
        const itemsList = document.getElementById(`items-list-${sectionId}`);
        if (!itemsList) return;
        
        const itemCards = itemsList.querySelectorAll('.item-card');
        const emptyState = itemsList.querySelector('.empty-items');
        
        if (itemCards.length === 0) {
            // Show empty state
            if (emptyState) {
                emptyState.style.display = 'flex';
            } else {
                // Create empty state if it doesn't exist
                const newEmptyState = document.createElement('div');
                newEmptyState.className = 'empty-items';
                newEmptyState.setAttribute('data-no-drag', '');
                newEmptyState.innerHTML = '<p>No items in this section yet. Drag items here or click "Add Item".</p>';
                itemsList.appendChild(newEmptyState);
            }
        } else {
            // Hide empty state
            if (emptyState) {
                emptyState.style.display = 'none';
            }
        }
    }

    function updateItemSection(itemId, newSectionId, oldSectionId) {
        fetch("/admin/api/items/change_section", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: parseInt(itemId),
                section_id: parseInt(newSectionId)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert('Error moving item: ' + (data.error || 'Unknown error'));
            } else {
                // Update order in the new section
                updateItemOrderInSection(newSectionId);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error moving item. Please check the console.');
        });
    }

    function updateItemOrderInSection(sectionId) {
        const itemsList = document.getElementById(`items-list-${sectionId}`);
        const itemIds = Array.from(itemsList.querySelectorAll('.item-card'))
            .map(card => card.getAttribute('data-item-id'));
        
        fetch("/admin/api/items/reorder", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                section_id: parseInt(sectionId),
                order: itemIds
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('Error updating item order:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Add section functionality
    const addSectionBtn = document.getElementById('add-section-btn');
    if (addSectionBtn) {
        addSectionBtn.addEventListener('click', function () {
            const title = prompt('Enter section title:');
            if (title && title.trim()) {
                fetch("/admin/api/section/new", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        topic_id: parseInt(topicId),
                        title: title.trim()
                    })
                })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error creating section: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(function (error) {
                    console.error('Error:', error);
                    alert('Error creating section. Please check the console for details.');
                });
            }
        });
    }

    // Add item to section
    var addItemButtons = document.querySelectorAll('.add-item-btn');
    addItemButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            var sectionId = this.getAttribute('data-section-id');
            window.location.href = "/admin/section/" + sectionId + "/item/new";
        });
    });

    // Edit section
    var editButtons = document.querySelectorAll('.edit-section-btn');
    editButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            var sectionId = this.getAttribute('data-section-id');
            var sectionCard = this.closest('.section-card');
            var currentTitle = sectionCard.querySelector('h3').textContent;
            var newTitle = prompt('Edit section title:', currentTitle);

            if (newTitle && newTitle.trim() && newTitle !== currentTitle) {
                fetch("/admin/api/section/update", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        section_id: parseInt(sectionId),
                        title: newTitle.trim(),
                        display_order: 0
                    })
                })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        sectionCard.querySelector('h3').textContent = newTitle.trim();
                        alert('Section updated successfully!');
                    } else {
                        alert('Error updating section: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(function (error) {
                    console.error('Error:', error);
                    alert('Error updating section. Please check the console for details.');
                });
            }
        });
    });

    // Delete section
    var deleteButtons = document.querySelectorAll('.delete-section-btn');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            var sectionId = this.getAttribute('data-section-id');
            var sectionCard = this.closest('.section-card');
            var sectionTitle = sectionCard.querySelector('h3').textContent;

            if (confirm('Are you sure you want to delete the section "' + sectionTitle + '" and all its items? This action cannot be undone.')) {
                fetch("/admin/api/section/delete", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        section_id: parseInt(sectionId)
                    })
                })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        sectionCard.remove();

                        var sectionsList = document.querySelector('.sections-list');
                        var remainingSections = sectionsList.querySelectorAll('.section-card');
                        if (remainingSections.length === 0) {
                            sectionsList.innerHTML = `
                                <div class="empty-state">
                                    <h2>No sections yet</h2>
                                    <p>Add your first section to start building this cheat sheet.</p>
                                </div>
                            `;
                        }

                        alert('Section deleted successfully!');
                    } else {
                        alert('Error deleting section: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(function (error) {
                    console.error('Error:', error);
                    alert('Error deleting section. Please check the console for details.');
                });
            }
        });
    });
}

// Initialize when DOM is loaded
if (document.getElementById('sections-list')) {
    document.addEventListener('DOMContentLoaded', initializeSectionsManagement);
}
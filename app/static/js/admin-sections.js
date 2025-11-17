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
            filter: '.items-list, .items-grid, .item-card',
            preventOnFilter: false,
            onEnd: function(evt) {
                if (evt.to !== sectionsList) {
                    sectionSortable.sort(Array.from(sectionsList.children).map(child => child.getAttribute('data-section-id')));
                    return;
                }
                
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
                        console.error('Error reordering sections:', data.error);
                        showFlashMessage('Error reordering sections: ' + (data.error || 'Unknown error'), 'error');
                        sectionSortable.sort(sectionIds);
                    } else {
                        showFlashMessage('Sections reordered successfully!', 'success');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showFlashMessage('Error reordering sections. Please check the console.', 'error');
                });
            }
        });
    }

    // Item drag & drop for each section - FIXED CROSS-SECTION DRAGGING
    document.querySelectorAll('[id^="items-list-"]').forEach(itemsList => {
        const sectionId = itemsList.id.replace('items-list-', '');
        
        const itemsGrid = itemsList.querySelector('.items-grid');
        if (!itemsGrid) return;
        
        const itemSortable = Sortable.create(itemsGrid, {
            group: 'shared-items', // Same group name for ALL sections
            handle: '.item-handle .handle-icon',
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            draggable: '.item-card',
            onAdd: function(evt) {
                // when an item is added to a new list
                const fromSectionId = evt.from.closest('[id^="items-list-"]').id.replace('items-list-', '');
                const toSectionId = evt.to.closest('[id^="items-list-"]').id.replace('items-list-', '');
                const itemId = evt.item.getAttribute('data-item-id');
                
                console.log('Item added to new section:', { itemId, fromSectionId, toSectionId });
                
                if (fromSectionId !== toSectionId) {
                    updateItemSection(itemId, toSectionId, fromSectionId);
                }
            },
            onUpdate: function(evt) {
                // when items are reordered within the same list
                const sectionId = evt.to.closest('[id^="items-list-"]').id.replace('items-list-', '');
                console.log('Items reordered in section:', sectionId);
                updateItemOrderInSection(sectionId);
            },
            onEnd: function(evt) {
                // Cleanup and update empty states
                const fromContainer = evt.from.closest('[id^="items-list-"]');
                const toContainer = evt.to.closest('[id^="items-list-"]');
                
                if (fromContainer && toContainer) {
                    const fromSectionId = fromContainer.id.replace('items-list-', '');
                    const toSectionId = toContainer.id.replace('items-list-', '');
                    
                    updateEmptyState(fromSectionId);
                    updateEmptyState(toSectionId);
                }
            }
        });
        
        updateEmptyState(sectionId);
    });

    function updateEmptyState(sectionId) {
        const itemsList = document.getElementById(`items-list-${sectionId}`);
        if (!itemsList) return;
        
        const itemsGrid = itemsList.querySelector('.items-grid');
        if (!itemsGrid) return;
        
        const itemCards = itemsGrid.querySelectorAll('.item-card');
        const emptyState = itemsList.querySelector('.empty-items');
        
        if (itemCards.length === 0) {
            if (emptyState) {
                emptyState.style.display = 'flex';
            } else {
                const newEmptyState = document.createElement('div');
                newEmptyState.className = 'empty-items';
                newEmptyState.setAttribute('data-no-drag', '');
                newEmptyState.innerHTML = '<p>No items in this section yet. Drag items here or click "Add Item".</p>';
                itemsList.appendChild(newEmptyState);
            }
        } else {
            if (emptyState) {
                emptyState.style.display = 'none';
            }
        }
    }

    function updateItemSection(itemId, newSectionId, oldSectionId) {
        console.log('Updating item section:', { itemId, newSectionId, oldSectionId });
        
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
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Server response:', data);
            if (data.success) {
                console.log('Item section updated successfully');
                updateItemOrderInSection(newSectionId);
                showFlashMessage('Item moved to new section!', 'success');
            } else {
                throw new Error(data.error || 'Unknown server error');
            }
        })
        .catch(error => {
            console.error('Error moving item:', error);
            showFlashMessage('Error moving item: ' + error.message, 'error');
            // Revert the UI change on error
            revertItemToSection(itemId, oldSectionId);
        });
    }

    function revertItemToSection(itemId, sectionId) {
        const itemCard = document.querySelector(`[data-item-id="${itemId}"]`);
        const targetList = document.getElementById(`items-list-${sectionId}`);
        const targetGrid = targetList ? targetList.querySelector('.items-grid') : null;
        
        if (itemCard && targetGrid) {
            itemCard.remove();
            targetGrid.appendChild(itemCard);
            updateEmptyState(sectionId);
        }
    }

    function updateItemOrderInSection(sectionId) {
        const itemsList = document.getElementById(`items-list-${sectionId}`);
        if (!itemsList) return;
        
        const itemsGrid = itemsList.querySelector('.items-grid');
        if (!itemsGrid) return;
        
        const itemIds = Array.from(itemsGrid.querySelectorAll('.item-card'))
            .map(card => card.getAttribute('data-item-id'));
        
        console.log('Updating item order for section:', sectionId, itemIds);
        
        // Create form data instead of JSON
        const formData = new FormData();
        formData.append('section_id', sectionId);
        itemIds.forEach((id, index) => {
            formData.append('order[]', id);
        });
        
        fetch("/admin/api/items/reorder", {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                console.error('Error updating item order:', data.error);
                showFlashMessage('Error updating item order: ' + data.error, 'error');
            } else {
                console.log('Item order updated successfully');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showFlashMessage('Error updating item order. Please check the console.', 'error');
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
                        showFlashMessage('Section updated successfully!', 'success');
                    } else {
                        showFlashMessage('Error updating section: ' + (data.error || 'Unknown error'), 'error');
                    }
                })
                .catch(function (error) {
                    console.error('Error:', error);
                    showFlashMessage('Error updating section. Please check the console for details.', 'error');
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

                        showFlashMessage('Section deleted successfully!', 'success');
                    } else {
                        showFlashMessage('Error deleting section: ' + (data.error || 'Unknown error'), 'error');
                    }
                })
                .catch(function (error) {
                    console.error('Error:', error);
                    showFlashMessage('Error deleting section. Please check the console for details.', 'error');
                });
            }
        });
    });
    
    // Flash message utility
    function showFlashMessage(message, type) {
        // Remove any existing flash messages
        const existingFlash = document.querySelector('.flash-message');
        if (existingFlash) {
            existingFlash.remove();
        }
        
        const flashDiv = document.createElement('div');
        flashDiv.className = `alert alert-${type} flash-message`;
        flashDiv.textContent = message;
        flashDiv.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 10000;
            max-width: 300px;
        `;
        
        document.body.appendChild(flashDiv);
        
        setTimeout(() => {
            if (flashDiv.parentElement) {
                flashDiv.remove();
            }
        }, 3000);
    }
}

// Initialize when DOM is loaded
if (document.getElementById('sections-list')) {
    document.addEventListener('DOMContentLoaded', initializeSectionsManagement);
}
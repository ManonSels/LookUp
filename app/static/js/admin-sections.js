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
        
        const itemsGrid = itemsList.querySelector('.items-grid');
        if (!itemsGrid) return;
        
        const itemSortable = Sortable.create(itemsGrid, {
            group: 'items',
            handle: '.item-handle .handle-icon',
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            draggable: '.item-card',
            onEnd: function(evt) {
                const fromContainer = evt.from.closest('[id^="items-list-"]');
                const toContainer = evt.to.closest('[id^="items-list-"]');
                
                if (!fromContainer || !toContainer) return;
                
                const fromSectionId = fromContainer.id.replace('items-list-', '');
                const toSectionId = toContainer.id.replace('items-list-', '');
                const itemId = evt.item.getAttribute('data-item-id');
                
                if (fromSectionId !== toSectionId) {
                    updateItemSection(itemId, toSectionId, fromSectionId);
                } else {
                    updateItemOrderInSection(toSectionId);
                }
                
                updateEmptyState(fromSectionId);
                updateEmptyState(toSectionId);
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
        if (!itemsList) return;
        
        const itemsGrid = itemsList.querySelector('.items-grid');
        if (!itemsGrid) return;
        
        const itemIds = Array.from(itemsGrid.querySelectorAll('.item-card'))
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
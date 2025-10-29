// Categories management functionality
function initializeCategoriesDragDrop() {
    const categoriesList = document.getElementById('categories-list');
    
    if (categoriesList) {
        const sortable = Sortable.create(categoriesList, {
            handle: '.handle',
            animation: 150,
            onEnd: function(evt) {
                // Get new order
                const categoryIds = Array.from(categoriesList.querySelectorAll('.category-card'))
                    .map(card => card.getAttribute('data-category-id'));
                
                // Update order in db
                fetch("/admin/api/categories/reorder", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        order: categoryIds
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update display numbers
                        updateDisplayOrders();
                    } else {
                        alert('Error updating category order');
                    }
                });
            }
        });
        
        function updateDisplayOrders() {
            const cards = categoriesList.querySelectorAll('.category-card');
            cards.forEach((card, index) => {
                const orderSpan = card.querySelector('.display-order');
                if (orderSpan) {
                    orderSpan.textContent = `Order: ${index}`;
                }
            });
        }
    }
}

// Initialize when DOM is loaded
if (document.getElementById('categories-list')) {
    document.addEventListener('DOMContentLoaded', initializeCategoriesDragDrop);
}
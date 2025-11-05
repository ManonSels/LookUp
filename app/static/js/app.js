// Global state
let currentPage = window.location.pathname;
let isTransitioning = false;
let undoStack = [];
let redoStack = [];
let suppressAutoHashScroll = false;

// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function () {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const html = document.documentElement;

    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';

        if (typeof updateTopicColors === 'function') {
            updateTopicColors();
        }
        if (typeof updateAdminTopicColors === 'function') {
            updateAdminTopicColors();
        }
    }

    // Initialize theme
    const currentTheme = localStorage.getItem('theme') || 'light';
    setTheme(currentTheme);

    // Toggle theme on button click
    themeToggle.addEventListener('click', function () {
        const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });

    // Initialize all functionality
    initializeSearch();
    initializePageSpecificFunctionality();
    initializeUndoRedo();
    initializeBackToTop();
    initializeKeyboardNav();
    initializeImageLoading();
    initializeCodeCopy();
});

// Undo/Redo functionality
function initializeUndoRedo() {
    const undoButton = document.getElementById('undoButton');
    const undoNotification = document.getElementById('undoNotification');
    const undoMessage = document.getElementById('undoMessage');

    if (undoButton && undoNotification) {
        undoButton.addEventListener('click', function() {
            if (undoStack.length > 0) {
                const action = undoStack.pop();
                redoStack.push(action);
                
                if (action.type === 'reorder') {
                    showNotification('Changes undone', 3000);
                }
                
                if (undoStack.length === 0) {
                    undoNotification.style.display = 'none';
                }
            }
        });
    }
}

function showNotification(message, duration = 3000) {
    const undoNotification = document.getElementById('undoNotification');
    const undoMessage = document.getElementById('undoMessage');
    
    if (undoNotification && undoMessage) {
        undoMessage.textContent = message;
        undoNotification.style.display = 'block';
        
        setTimeout(() => {
            undoNotification.style.display = 'none';
        }, duration);
    }
}

// Function to reset section filters to "All"
function resetSectionFilters() {
    const sectionFilters = document.getElementById('sectionFilters');
    if (!sectionFilters) return;
    
    const allSectionsBtn = sectionFilters.querySelector('[data-section="all"]');
    const filterButtons = sectionFilters.querySelectorAll('.filter-btn');
    
    if (allSectionsBtn) {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        allSectionsBtn.classList.add('active');
        
        const sections = document.querySelectorAll('.section');
        sections.forEach(section => {
            section.style.display = 'block';
        });
    }
}

function pushToUndoStack(action) {
    undoStack.push(action);
    redoStack = [];
    showNotification('Action completed - Undo available', 3000);
}

// Show loading overlay
function showLoadingOverlay(message = 'Loading...') {
    let overlay = document.getElementById('loadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div style="text-align: center;">
                <div class="loading-spinner" style="margin: 0 auto 1rem;"></div>
                <div>${message}</div>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    overlay.style.display = 'flex';
}

// Hide loading overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Back to Top functionality
function initializeBackToTop() {
    const backBtn = document.getElementById('backToTop');
    if (backBtn) {
        window.addEventListener('scroll', () => {
            backBtn.style.display = window.scrollY > 300 ? 'block' : 'none';
        });
        backBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
}

// Keyboard navigation
function initializeKeyboardNav() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Arrow Left/Right for topic navigation
        if ((e.ctrlKey || e.metaKey) && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
            const topics = document.querySelectorAll('.topic-card');
            if (topics.length > 0) {
                const currentSlug = window.location.pathname.split('/').pop();
                const currentIndex = Array.from(topics).findIndex(topic => {
                    const topicSlug = topic.href.split('/').pop();
                    return topicSlug === currentSlug;
                });
                
                if (currentIndex !== -1) {
                    const newIndex = e.key === 'ArrowRight' 
                        ? Math.min(currentIndex + 1, topics.length - 1)
                        : Math.max(currentIndex - 1, 0);
                    
                    if (newIndex !== currentIndex) {
                        window.location.href = topics[newIndex].href;
                    }
                }
            }
        }
        
        // Escape key to close modals
        if (e.key === 'Escape') {
            closeSearchModal();
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (modal.style.display === 'block') {
                    modal.style.display = 'none';
                }
            });
        }
    });
}

// Image loading handler
function initializeImageLoading() {
    document.querySelectorAll('img').forEach(img => {
        if (img.complete) {
            img.classList.add('loaded');
        } else {
            img.addEventListener('load', () => img.classList.add('loaded'));
            img.addEventListener('error', () => {
                const placeholder = document.createElement('div');
                placeholder.className = 'image-placeholder';
                placeholder.innerHTML = '📄';
                placeholder.style.cssText = `
                    width: 100%;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: var(--bg-secondary);
                    border-radius: 6px;
                    font-size: 1.5rem;
                `;
                img.parentNode.replaceChild(placeholder, img);
            });
        }
    });
}

// Code copy functionality
function initializeCodeCopy() {
    document.querySelectorAll('pre code').forEach(block => {
        const pre = block.closest('pre');
        if (!pre.querySelector('.copy-btn')) {
            const button = document.createElement('button');
            button.className = 'copy-btn';
            button.textContent = 'Copy';
            button.title = 'Copy to clipboard';
            button.onclick = async () => {
                try {
                    await navigator.clipboard.writeText(block.textContent);
                    button.textContent = 'Copied!';
                    button.style.background = 'var(--success-bg)';
                    button.style.color = 'var(--success-text)';
                    setTimeout(() => {
                        button.textContent = 'Copy';
                        button.style.background = '';
                        button.style.color = '';
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy: ', err);
                    button.textContent = 'Failed';
                    setTimeout(() => button.textContent = 'Copy', 2000);
                }
            };
            pre.style.position = 'relative';
            pre.appendChild(button);
        }
    });
}

// Search functionality
function initializeSearch() {
    const searchModal = document.getElementById('searchModal');
    const searchTrigger = document.getElementById('searchTrigger');
    const closeSearch = document.getElementById('closeSearch');
    const searchInput = document.getElementById('searchInput');
    const topicsList = document.getElementById('topicsList');
    const searchResults = document.getElementById('searchResults');
    const topicContent = document.getElementById('topicContent');
    const searchContentEmpty = document.querySelector('.search-content-empty');

    let allTopics = [];
    let currentTopicId = null;
    let searchTimeout;

    // Open search modal
    if (searchTrigger) {
        searchTrigger.addEventListener('click', function () {
            searchModal.style.display = 'block';
            searchModal.style.opacity = '0';
            searchModal.style.transition = 'opacity 0.2s ease';
            setTimeout(() => {
                searchModal.style.opacity = '1';
            }, 10);
            
            loadAllTopics();
            setTimeout(() => {
                searchInput.focus();
            }, 100);
        });
    }

    // Close search modal
    if (closeSearch) {
        closeSearch.addEventListener('click', closeSearchModal);
    }
    if (searchModal) {
        searchModal.addEventListener('click', function (e) {
            if (e.target === searchModal) {
                closeSearchModal();
            }
        });
    }

    // Handle search input
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length > 0) {
                resetSectionFilters();
            }

            if (query.length === 0) {
                showAllTopics();
                showTopicContentEmpty();
                return;
            }

            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchModal) {
                searchModal.style.display = 'block';
                searchModal.style.opacity = '0';
                searchModal.style.transition = 'opacity 0.2s ease';
                setTimeout(() => {
                    searchModal.style.opacity = '1';
                }, 10);
                setTimeout(() => {
                    if (searchInput) searchInput.focus();
                }, 100);
            }
        }

        if (e.key === 'Escape' && searchModal && searchModal.style.display === 'block') {
            closeSearchModal();
        }
    });

    function closeSearchModal() {
        if (searchModal) {
            searchModal.style.opacity = '0';
            searchModal.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                searchModal.style.display = 'none';
            }, 300);
        }
        if (searchInput) {
            searchInput.value = '';
        }
        showAllTopics();
        showTopicContentEmpty();
        currentTopicId = null;
        
        resetSectionFilters();
    }

    function loadAllTopics() {
        fetch('/search/topics')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                allTopics = data.topics || [];
                displayAllTopics();
            })
            .catch(error => {
                console.error('Error loading topics:', error);
                if (topicsList) {
                    topicsList.innerHTML = '<div class="search-error">Error loading topics. Please try again.</div>';
                }
            });
    }

    function displayAllTopics() {
        if (!topicsList) return;

        let html = '';
        allTopics.forEach(topic => {
            html += `
                <div class="topic-item ${currentTopicId === topic.id ? 'active' : ''}" 
                     data-topic-id="${topic.id}">
                    <div class="topic-title">${topic.title}</div>
                    <div class="topic-category">${topic.category}</div>
                </div>
            `;
        });

        topicsList.innerHTML = html;

        document.querySelectorAll('.topic-item').forEach(item => {
            item.addEventListener('click', function () {
                const topicId = this.getAttribute('data-topic-id');
                selectTopic(topicId);
            });
        });
    }

    function selectTopic(topicId) {
        currentTopicId = topicId;

        document.querySelectorAll('.topic-item').forEach(item => {
            item.classList.remove('active');
        });
        const activeItem = document.querySelector(`[data-topic-id="${topicId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }

        fetch(`/search/topic/${topicId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                displayTopicContent(data);
            })
            .catch(error => {
                console.error('Error loading topic content:', error);
                if (topicContent) {
                    topicContent.innerHTML = '<div class="search-error">Error loading topic content. Please try again.</div>';
                }
            });
    }

    function displayTopicContent(data) {
        if (!topicContent || !searchResults || !searchContentEmpty) return;

        searchResults.style.display = 'none';
        searchContentEmpty.style.display = 'none';
        topicContent.style.display = 'block';

        let html = `
            <div class="topic-header">
                <h2>${data.topic.title}</h2>
                ${data.topic.description ? `<p class="topic-description">${data.topic.description}</p>` : ''}
            </div>
        `;

        if (data.sections && data.sections.length > 0) {
            data.sections.forEach(section => {
                html += `
                    <div class="content-section">
                        <h3 class="section-title">
                            <a href="/${data.topic.slug}#section-${section.id}" onclick="navigateToSection('${data.topic.slug}', 'section-${section.id}')">
                                ${section.title}
                            </a>
                        </h3>
                        <div class="section-items">
                            ${section.items.map(item => `
                                <div class="section-item">
                                    <a href="/${data.topic.slug}#item-${item.id}" onclick="navigateToSection('${data.topic.slug}', 'item-${item.id}')">
                                        ${item.title}
                                    </a>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            });
        } else {
            html += '<div class="empty-section">No sections available for this topic.</div>';
        }

        topicContent.innerHTML = html;
    }

    function performSearch(query) {
        if (!searchResults || !topicContent || !searchContentEmpty) return;

        searchResults.innerHTML = '<div class="search-loading">Searching...</div>';
        searchResults.style.display = 'block';
        topicContent.style.display = 'none';
        searchContentEmpty.style.display = 'none';

        fetch(`/search/query?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                displaySearchResults(data, query);
            })
            .catch(error => {
                console.error('Search error:', error);
                if (searchResults) {
                    searchResults.innerHTML = '<div class="search-error">Error performing search. Please try again.</div>';
                }
            });
    }

    function displaySearchResults(data, query) {
        if (!searchResults) return;

        let html = '';

        if (!data.results || data.results.length === 0) {
            html = `
                <div class="search-empty">
                    <p>No results found for "<strong>${query}</strong>"</p>
                    <p class="search-hint">Try different keywords or check spelling</p>
                </div>
            `;
        } else {
            data.results.forEach(result => {
                html += `
                    <div class="search-topic-result">
                        <h3 class="search-topic-title">
                            <a href="/${result.topic.slug}" onclick="navigateToTopic('${result.topic.slug}')">
                                ${highlightText(result.topic.title, query)}
                            </a>
                        </h3>
                        ${result.topic.description ? `<p class="search-topic-description">${highlightText(result.topic.description, query)}</p>` : ''}
                        <div class="search-topic-sections">
                `;

                if (result.sections && result.sections.length > 0) {
                    result.sections.forEach(section => {
                        html += `
                            <div class="search-section-result">
                                <h4 class="search-section-title">
                                    <a href="/${result.topic.slug}#section-${section.id}" onclick="navigateToSection('${result.topic.slug}', 'section-${section.id}')">
                                        ${highlightText(section.title, query)}
                                    </a>
                                </h4>
                                <div class="search-section-items">
                        `;

                        if (section.items && section.items.length > 0) {
                            section.items.forEach(item => {
                                html += `
                                    <div class="search-item-result">
                                        <a href="/${result.topic.slug}#item-${item.id}" onclick="navigateToSection('${result.topic.slug}', 'item-${item.id}')">
                                            ${highlightText(item.title, query)}
                                        </a>
                                    </div>
                                `;
                            });
                        }

                        html += `
                                </div>
                            </div>
                        `;
                    });
                }

                html += `
                        </div>
                    </div>
                `;
            });
        }

        searchResults.innerHTML = html;
    }

    function showAllTopics() {
        displayAllTopics();
    }

    function showTopicContentEmpty() {
        if (!searchResults || !topicContent || !searchContentEmpty) return;
        searchResults.style.display = 'none';
        topicContent.style.display = 'none';
        searchContentEmpty.style.display = 'block';
    }

    function highlightText(text, query) {
        if (!text || !query) return text;
        const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedQuery})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
}

function navigateToTopic(topicSlug) {
    closeSearchModal();
    const url = '/' + topicSlug;
    navigateToUrl(url);
}

function navigateToSection(topicSlug, elementId) {
    closeSearchModal();
    const url = '/' + topicSlug + '#' + elementId;
    window.location.href = url;
}

function navigateToUrl(url) {
    const mainContent = document.querySelector('#mainContent');
    suppressAutoHashScroll = true;

    const targetHash = window.location.hash;
    const newHash = new URL(url, window.location.origin).hash;
    const finalHash = newHash || targetHash;

    if (mainContent) {
        mainContent.style.transition = 'none';
        mainContent.style.opacity = '0';
    }

    showPageLoading();

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.text();
        })
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newContent = doc.querySelector('#mainContent');
            const newTitle = doc.title;

            if (newContent && mainContent) {
                mainContent.innerHTML = newContent.innerHTML;
                document.title = newTitle;
                window.history.pushState({}, '', url);

                initializePageSpecificFunctionality();

                window.scrollTo(0, 0);

                requestAnimationFrame(() => {
                    mainContent.style.transition = 'opacity 0.6s ease';
                    mainContent.style.opacity = '1';
                    
                    setTimeout(() => {
                        if (finalHash) {
                            const elementId = finalHash.substring(1);
                            scrollToElement(elementId, true);
                        }
                        suppressAutoHashScroll = false;
                    }, 600);
                });
            } else {
                window.location.href = url;
            }
        })
        .catch(error => {
            console.error('Navigation error:', error);
            window.location.href = url;
        })
        .finally(() => {
            setTimeout(() => {
                hidePageLoading();
            }, 600);
        });
}

function showPageLoading() {
    const loading = document.getElementById('pageLoading');
    if (loading) {
        loading.classList.add('active');
    }
}

function hidePageLoading() {
    const loading = document.getElementById('pageLoading');
    if (loading) {
        loading.classList.remove('active');
    }
}

// Global function to close search modal
function closeSearchModal() {
    const searchModal = document.getElementById('searchModal');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const topicContent = document.getElementById('topicContent');
    const searchContentEmpty = document.querySelector('.search-content-empty');

    if (searchModal) {
        searchModal.style.display = 'none';
    }
    if (searchInput) {
        searchInput.value = '';
    }
    if (searchResults) {
        searchResults.style.display = 'none';
    }
    if (topicContent) {
        topicContent.style.display = 'none';
    }
    if (searchContentEmpty) {
        searchContentEmpty.style.display = 'block';
    }
}

function initializePageSpecificFunctionality() {
    if (typeof initializeHomePage === 'function') {
        initializeHomePage();
    }

    if (typeof initializeCheatsheetPage === 'function') {
        initializeCheatsheetPage();
    }
    
    if (typeof initializeCategoryFilters === 'function') {
        initializeCategoryFilters();
    }
    
    if (typeof initializeAdminSearch === 'function') {
        initializeAdminSearch();
    }
    
    if (typeof initializeAutoSave === 'function') {
        initializeAutoSave();
    }

    if (window.location.hash && !suppressAutoHashScroll) {
        setTimeout(() => {
            const elementId = window.location.hash.substring(1);
            scrollToElement(elementId, true);
        }, 100);
    }
    
    setTimeout(initializeCodeCopy, 500);
}

function scrollToElement(elementId, smooth = true) {
    if (!elementId) return;
    
    setTimeout(() => {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`Element with id "${elementId}" not found`);
            return;
        }

        const navbarHeight = 80;
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - navbarHeight - 20;

        const scrollToPosition = (position, behavior = 'smooth') => {
            window.scrollTo({
                top: position,
                behavior: behavior
            });
        };

        if (smooth) {
            scrollToPosition(offsetPosition, 'smooth');
        } else {
            scrollToPosition(offsetPosition, 'auto');
        }

        setTimeout(() => {
            if (elementId.startsWith('section-')) {
                element.classList.add('section-highlight');
                setTimeout(() => element.classList.remove('section-highlight'), 3000);
            } else if (elementId.startsWith('item-')) {
                element.classList.add('card-highlight');
                setTimeout(() => element.classList.remove('card-highlight'), 3000);
            }
        }, smooth ? 800 : 100);
    }, 50);
}

// Home page specific functionality
function initializeHomePage() {
    function updateTopicColors() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        document.querySelectorAll('.topic-card').forEach(card => {
            const lightColor = card.getAttribute('data-color-light') || '#ffffff';
            const darkColor = card.getAttribute('data-color-dark') || '#1a1a1a';
            const color = isDark ? darkColor : lightColor;
            card.style.setProperty('--topic-color', color);
            card.style.backgroundColor = color;
        });
    }

    updateTopicColors();

    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            setTimeout(updateTopicColors, 100);
        });
    }
}

// Cheatsheet page specific functionality
function initializeCheatsheetPage() {
    if (window.location.hash && !suppressAutoHashScroll) {
        setTimeout(() => {
            scrollToElement(window.location.hash.substring(1));
        }, 300);
    }
}
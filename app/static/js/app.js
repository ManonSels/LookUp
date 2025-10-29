// static/js/app.js

// Global state
let currentPage = window.location.pathname;
let isTransitioning = false;

// prevent duplicate auto-hash scrolling when we already handled it manually
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

		// Update topic colors when theme changes
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

	// Initialize search functionality
	initializeSearch();

	// Initialize page-specific functionality
	initializePageSpecificFunctionality();
});

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
			loadAllTopics();
			setTimeout(() => searchInput.focus(), 100);
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

			if (query.length === 0) {
				showAllTopics();
				showTopicContentEmpty();
				return;
			}

			searchTimeout = setTimeout(() => {
				performSearch(query);
			}, 200);
		});
	}

	// Keyboard shortcuts
	document.addEventListener('keydown', function (e) {
		if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
			e.preventDefault();
			if (searchModal) {
				searchModal.style.display = 'block';
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
		if (searchModal) searchModal.style.display = 'none';
		if (searchInput) searchInput.value = '';
		showAllTopics();
		showTopicContentEmpty();
		currentTopicId = null;
	}

	function loadAllTopics() {
		fetch('/search/topics')
			.then(response => response.json())
			.then(data => {
				allTopics = data.topics || [];
				displayAllTopics();
			})
			.catch(error => {
				console.error('Error loading topics:', error);
				if (topicsList) {
					topicsList.innerHTML = '<div class="search-error">Error loading topics</div>';
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

		// Add click handlers
		document.querySelectorAll('.topic-item').forEach(item => {
			item.addEventListener('click', function () {
				const topicId = this.getAttribute('data-topic-id');
				selectTopic(topicId);
			});
		});
	}

	function selectTopic(topicId) {
		currentTopicId = topicId;

		// Update active state
		document.querySelectorAll('.topic-item').forEach(item => {
			item.classList.remove('active');
		});
		const activeItem = document.querySelector(`[data-topic-id="${topicId}"]`);
		if (activeItem) {
			activeItem.classList.add('active');
		}

		// Load topic content
		fetch(`/search/topic/${topicId}`)
			.then(response => response.json())
			.then(data => {
				displayTopicContent(data);
			})
			.catch(error => {
				console.error('Error loading topic content:', error);
				if (topicContent) {
					topicContent.innerHTML = '<div class="search-error">Error loading topic content</div>';
				}
			});
	}

	function displayTopicContent(data) {
		if (!topicContent || !searchResults || !searchContentEmpty) return;

		// Hide search results and empty state, show topic content
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
			.then(response => response.json())
			.then(data => {
				displaySearchResults(data, query);
			})
			.catch(error => {
				console.error('Search error:', error);
				if (searchResults) {
					searchResults.innerHTML = '<div class="search-error">Error performing search</div>';
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
	// Use client-side navigation instead of full page reload
	const url = '/' + topicSlug;
	navigateToUrl(url);
}

function navigateToSection(topicSlug, elementId) {
	closeSearchModal();
	// Use client-side navigation instead of full page reload
	const url = '/' + topicSlug + '#' + elementId;
	navigateToUrl(url);
}

function navigateToUrl(url) {
    const mainContent = document.querySelector('#mainContent');
    suppressAutoHashScroll = true;

    // Store the target hash for later scrolling
    const targetHash = window.location.hash;
    const newHash = new URL(url, window.location.origin).hash;
    const finalHash = newHash || targetHash;

    // Instantly reset opacity (no visual flash)
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

                // Remove any automatic hash scrolls
                window.scrollTo(0, 0);

                // Wait for the next frame to ensure content is rendered
                requestAnimationFrame(() => {
                    // Fade in content first
                    mainContent.style.transition = 'opacity 0.3s ease';
                    mainContent.style.opacity = '1';
                    
                    // Then scroll to target after content is visible
                    setTimeout(() => {
                        if (finalHash) {
                            const elementId = finalHash.substring(1);
                            scrollToElement(elementId, true);
                        }
                        suppressAutoHashScroll = false;
                    }, 350); // Wait for fade-in to complete
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
            }, 300);
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
    // Initialize home page functionality
    if (typeof initializeHomePage === 'function') {
        initializeHomePage();
    }

    // Initialize cheatsheet page functionality
    if (typeof initializeCheatsheetPage === 'function') {
        initializeCheatsheetPage();
    }

    // Handle hash navigation with a slight delay to ensure content is ready
    if (window.location.hash && !suppressAutoHashScroll) {
        setTimeout(() => {
            const elementId = window.location.hash.substring(1);
            // Use smooth scroll for direct page loads too
            scrollToElement(elementId, true);
        }, 100);
    }
}

function scrollToElement(elementId, smooth = true) {
    if (!elementId) return;
    
    // Small delay to ensure DOM is fully updated
    setTimeout(() => {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`Element with id "${elementId}" not found`);
            return;
        }

        const navbarHeight = 80;
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - navbarHeight - 20;

        // Use requestAnimationFrame for smoother scrolling
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

        // Highlight animation with better timing
        setTimeout(() => {
            if (elementId.startsWith('section-')) {
                element.classList.add('section-highlight');
                setTimeout(() => element.classList.remove('section-highlight'), 2000);
            } else if (elementId.startsWith('item-')) {
                element.classList.add('card-highlight');
                setTimeout(() => element.classList.remove('card-highlight'), 2000);
            }
        }, smooth ? 500 : 100);
    }, 50);
}


// Home page specific functionality
function initializeHomePage() {
	// Set topic colors based on current theme
	function updateTopicColors() {
		const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
		document.querySelectorAll('.topic-card').forEach(card => {
			const lightColor = card.getAttribute('data-color-light') || '#ffffff';
			const darkColor = card.getAttribute('data-color-dark') || '#1a1a1a';
			const color = isDark ? darkColor : lightColor;
			card.style.setProperty('--topic-color', color);
		});
	}

	// Initial update
	updateTopicColors();

	// Update when theme changes
	const themeToggle = document.getElementById('themeToggle');
	if (themeToggle) {
		themeToggle.addEventListener('click', function () {
			setTimeout(updateTopicColors, 100);
		});
	}
}

// Cheatsheet page specific functionality
function initializeCheatsheetPage() {
	// Handle hash navigation on cheatsheet pages
	if (window.location.hash && !suppressAutoHashScroll) {
		setTimeout(() => {
			scrollToElement(window.location.hash.substring(1));
		}, 300);
	}
}
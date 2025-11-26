const API_URL = '';
let currentCategory = 'Breakfast';
let allItems = [];

async function fetchMenu(query = '', forceRefresh = false) {
    const container = document.getElementById('menuContainer');

    // Show loading state if it's a new search or initial load
    if (query || forceRefresh || allItems.length === 0) {
        container.innerHTML = `
            <div class="animate-pulse space-y-4">
                <div class="h-32 bg-gray-200 rounded-2xl"></div>
                <div class="h-32 bg-gray-200 rounded-2xl"></div>
            </div>`;
    }

    // Only fetch from server if searching OR if we don't have cached data
    if (query || allItems.length === 0 || forceRefresh) {
        // Cache busting
        const timestamp = new Date().getTime();
        const endpoint = query ? `/menu/search/?q=${encodeURIComponent(query)}&t=${timestamp}` : `/menu/?t=${timestamp}`;
        try {
            const response = await fetch(`${API_URL}${endpoint}`);
            const data = await response.json();

            // Handle new response format (SearchResponse) or legacy list
            let items = [];
            let answer = null;

            if (Array.isArray(data)) {
                items = data;
            } else {
                items = data.items;
                answer = data.answer;
            }

            allItems = items; // Store for client-side filtering
            renderMenu(items, answer);
        } catch (error) {
            console.error('Error fetching menu:', error);
            container.innerHTML = `
                <div class="text-center py-12">
                    <p class="text-red-500 font-medium">Failed to load menu.</p>
                    <p class="text-xs text-gray-400 mt-2">${error.message}</p>
                    <button onclick="fetchMenu('', true)" class="mt-4 px-4 py-2 bg-brand-100 text-brand-700 rounded-lg text-sm">Try Again</button>
                </div>`;
        }
    } else {
        // Use cached data - just re-render instantly
        renderMenu(allItems);
    }
}

function renderMenu(items, answer = null) {
    const container = document.getElementById('menuContainer');
    container.innerHTML = '';

    // Show AI Answer if present
    if (answer) {
        const answerDiv = document.createElement('div');
        answerDiv.className = 'bg-brand-50 border border-brand-100 p-5 rounded-2xl mb-6 flex items-start gap-3 shadow-sm';
        answerDiv.innerHTML = `
            <div class="bg-brand-100 p-2 rounded-full flex-shrink-0">
                <svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
            </div>
            <div>
                <p class="text-brand-900 font-medium text-base">AI Suggestion</p>
                <p class="text-gray-700 text-base mt-1 leading-relaxed whitespace-pre-wrap">${answer}</p>
            </div>
        `;
        container.appendChild(answerDiv);
    }

    // Filter by category if not searching (search results should show all matches)
    const searchVal = document.getElementById('searchInput').value;
    const isSearch = searchVal.length > 0;
    const filteredItems = (currentCategory === 'All' || isSearch)
        ? items
        : items.filter(item => item.category === currentCategory);

    if (filteredItems.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12">
                <div class="inline-block p-4 rounded-full bg-gray-100 mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </div>
                <p class="text-gray-500 font-medium">No items found.</p>
            </div>`;
        return;
    }

    filteredItems.forEach(item => {
        const card = document.createElement('div');
        card.className = 'bg-white p-5 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-all duration-300 group';

        let tagsHtml = '';
        if (item.dietary_tags) {
            const tags = item.dietary_tags.split(',').map(t => t.trim());
            tagsHtml = tags.map(tag => {
                let colorClass = 'bg-gray-100 text-gray-600';
                if (tag.includes('VG')) colorClass = 'bg-emerald-100 text-emerald-700';
                else if (tag.includes('V')) colorClass = 'bg-lime-100 text-lime-700';
                else if (tag.includes('GF')) colorClass = 'bg-amber-100 text-amber-700';
                else if (tag.includes('NOT VEGAN')) colorClass = 'bg-red-100 text-red-700 font-bold border border-red-200';

                // Clean up tag text (remove parenthesis often found in raw data)
                const cleanTag = tag.replace(/[()]/g, '');
                return `<span class="text-xs uppercase tracking-wider font-bold px-2.5 py-1.5 rounded-full ${colorClass} mr-1.5">${cleanTag}</span>`;
            }).join('');
        }

        let alertHtml = '';
        if (item.safety_alerts) {
            alertHtml = `
                <div class="mt-3 p-4 bg-red-50 border border-red-100 rounded-xl flex items-start gap-2">
                    <svg class="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    <p class="text-sm text-red-700 font-medium leading-relaxed">${item.safety_alerts}</p>
                </div>`;
        }

        let mayContainHtml = '';
        if (item.may_contain) {
            mayContainHtml = `<p class="mt-2 text-sm text-amber-600 font-medium flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                May contain: ${item.may_contain}
            </p>`;
        }

        // Price formatting
        const priceDisplay = item.price > 0 ? `£${item.price.toFixed(2)}` : '';

        card.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <h3 class="font-bold text-gray-800 text-xl leading-tight group-hover:text-brand-600 transition-colors">${item.name}</h3>
                <span class="font-bold text-accent-700 bg-accent-100 px-3 py-1.5 rounded-lg ml-2 whitespace-nowrap text-lg shadow-sm">${priceDisplay}</span>
            </div>
            <p class="text-gray-600 text-base mb-3 leading-relaxed">${item.description || ''}</p>
            <div class="flex flex-wrap gap-y-2 mb-1">
                ${tagsHtml}
            </div>
            ${mayContainHtml}
            ${alertHtml}
        `;
        container.appendChild(card);
    });
}

// Search Handler
const searchInput = document.getElementById('searchInput');
const searchIcon = document.getElementById('searchIcon');
const searchBtn = document.getElementById('searchBtn');
const clearSearchBtn = document.getElementById('clearSearchBtn');

function updateSearchVisuals(query) {
    if (query.length > 0) {
        searchInput.classList.remove('bg-white/10', 'text-white', 'placeholder-white/70');
        searchInput.classList.add('bg-white', 'text-gray-900');
        searchIcon.classList.remove('text-white/70');
        searchIcon.classList.add('text-brand-500');
        clearSearchBtn.classList.remove('hidden');
    } else {
        searchInput.classList.add('bg-white/10', 'text-white', 'placeholder-white/70');
        searchInput.classList.remove('bg-white', 'text-gray-900');
        searchIcon.classList.add('text-white/70');
        searchIcon.classList.remove('text-brand-500');
        clearSearchBtn.classList.add('hidden');
    }
}

// Input handler for visuals only
searchInput.addEventListener('input', (e) => {
    updateSearchVisuals(e.target.value);
});

// Search execution
function executeSearch() {
    const query = searchInput.value.trim();
    fetchMenu(query);
}

searchBtn.addEventListener('click', executeSearch);

searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        executeSearch();
    }
});

// Clear handler
clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    updateSearchVisuals('');
    fetchMenu(); // Reset to full menu
});

// Category Handler
document.getElementById('categoryNav').addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON') {
        // Update active state
        document.querySelectorAll('#categoryNav button').forEach(btn => {
            btn.className = 'px-6 py-3 rounded-full bg-white text-gray-600 text-base font-medium border border-gray-200 shadow-sm whitespace-nowrap hover:bg-gray-50 transition-transform active:scale-95';
        });
        e.target.className = 'px-6 py-3 rounded-full bg-brand-600 text-white text-base font-medium shadow-md whitespace-nowrap transition-transform active:scale-95';

        currentCategory = e.target.getAttribute('data-category');

        // Clear search if category is clicked
        searchInput.value = '';
        searchInput.dispatchEvent(new Event('input')); // Reset styles

        // Re-render
        fetchMenu();
    }
});

// Initial load
fetchMenu();

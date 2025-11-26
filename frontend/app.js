const API_URL = '';
let currentCategory = 'Breakfast';
let fullMenu = []; // Store the complete menu
let suggestedItems = []; // Store AI-suggested items
let currentAnswer = null; // Store current AI answer

async function fetchMenu(query = '', forceRefresh = false) {
    console.log('fetchMenu called', { query, forceRefresh, fullMenuLength: fullMenu.length });
    const container = document.getElementById('menuContainer');

    // Show loading state if it's a new search or initial load
    if (query || forceRefresh || fullMenu.length === 0) {
        container.innerHTML = `
            <div class="animate-pulse space-y-4">
                <div class="h-32 bg-gray-200 rounded-2xl"></div>
                <div class="h-32 bg-gray-200 rounded-2xl"></div>
            </div>`;
    }

    // Only fetch from server if searching OR if we don't have cached data
    // If searching, we always fetch to get new suggestions
    if (query || fullMenu.length === 0 || forceRefresh) {
        // Cache busting
        const timestamp = new Date().getTime();
        const endpoint = query ? `/menu/search/?q=${encodeURIComponent(query)}&t=${timestamp}` : `/menu/?t=${timestamp}`;
        try {
            console.log('Fetching from:', endpoint);
            const response = await fetch(`${API_URL}${endpoint}`);
            const data = await response.json();
            console.log('Fetch response data:', data);

            // Handle new response format (SearchResponse) or legacy list
            let items = [];
            let answer = null;

            if (Array.isArray(data)) {
                items = data;
            } else {
                items = data.items;
                answer = data.answer;
            }

            if (query) {
                // It's a search result
                suggestedItems = items;
                currentAnswer = answer;
                console.log('Search results loaded:', suggestedItems.length);
                showYourMealCategory();
                // Automatically switch to "Your Meal"
                switchCategory('Your Meal');
            } else {
                // It's the full menu load
                fullMenu = items;
                console.log('Full menu loaded:', fullMenu.length);
                // Ensure "Your Meal" is hidden on full refresh/load
                hideYourMealCategory();
                renderMenu();
            }

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
        console.log('Using cached data');
        renderMenu();
    }
}

function showYourMealCategory() {
    const btn = document.getElementById('yourMealBtn');
    if (btn) {
        btn.classList.remove('hidden');
    }
}

function hideYourMealCategory() {
    const btn = document.getElementById('yourMealBtn');
    if (btn) {
        btn.classList.add('hidden');
    }
    // If we were on "Your Meal", switch back to default
    if (currentCategory === 'Your Meal') {
        switchCategory('Breakfast');
    }
}

async function switchCategory(category) {
    console.log('Switching category to:', category);
    currentCategory = category;

    // Update visual state of buttons
    document.querySelectorAll('#categoryNav button').forEach(btn => {
        const btnCat = btn.getAttribute('data-category');
        if (btnCat === currentCategory) {
            btn.className = 'px-6 py-3 rounded-full bg-brand-600 text-white text-base font-medium shadow-md whitespace-nowrap transition-transform active:scale-95';
            // Ensure the button is visible if it's "Your Meal"
            if (btnCat === 'Your Meal') btn.classList.remove('hidden');
        } else {
            // Keep "Your Meal" hidden if it should be hidden, otherwise standard inactive style
            if (btnCat === 'Your Meal' && suggestedItems.length === 0) {
                btn.classList.add('hidden');
            } else {
                btn.className = 'px-6 py-3 rounded-full bg-white text-gray-600 text-base font-medium border border-gray-200 shadow-sm whitespace-nowrap hover:bg-gray-50 transition-transform active:scale-95';
                if (btnCat === 'Your Meal') btn.classList.remove('hidden');
            }
        }
    });

    if (category !== 'Your Meal' && fullMenu.length === 0) {
        console.log('Full menu missing, fetching...');
        await fetchMenu(); // Fetch full menu
    } else {
        renderMenu();
    }
}

function renderMenu() {
    console.log('renderMenu called', { currentCategory, fullMenuLength: fullMenu.length, suggestedItemsLength: suggestedItems.length });
    const container = document.getElementById('menuContainer');
    container.innerHTML = '';

    // Update Debug Info
    document.getElementById('debugCount').textContent = fullMenu.length;
    const cats = [...new Set(fullMenu.map(i => i.category))].join(', ');
    document.getElementById('debugCategories').textContent = cats || 'None';

    let itemsToRender = [];
    let answerToRender = null;

    if (currentCategory === 'Your Meal') {
        itemsToRender = suggestedItems;
        answerToRender = currentAnswer;
    } else {
        // Filter from full menu
        itemsToRender = (currentCategory === 'All')
            ? fullMenu
            : fullMenu.filter(item => item.category === currentCategory);
    }

    console.log('Items to render:', itemsToRender.length);

    // Show AI Answer if present AND we are in "Your Meal" category
    if (answerToRender && currentCategory === 'Your Meal') {
        const answerDiv = document.createElement('div');
        answerDiv.className = 'bg-brand-50 border border-brand-100 p-5 rounded-2xl mb-6 flex items-start gap-3 shadow-sm';
        answerDiv.innerHTML = `
            <div class="bg-brand-100 p-2 rounded-full flex-shrink-0">
                <svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
            </div>
            <div>
                <p class="text-brand-900 font-medium text-base">AI Suggestion</p>
                <p class="text-gray-700 text-base mt-1 leading-relaxed whitespace-pre-wrap">${answerToRender}</p>
            </div>
        `;
        container.appendChild(answerDiv);
    }

    if (itemsToRender.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12">
                <div class="inline-block p-4 rounded-full bg-gray-100 mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </div>
                <p class="text-gray-500 font-medium">No items found.</p>
            </div>`;
        return;
    }

    itemsToRender.forEach(item => {
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
    if (query) {
        fetchMenu(query);
    }
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
    // Just clear the input - don't reload menu unless user wants to go back to main menu
    // But per requirements, "Your Meal" disappears on refresh, but maybe we should let user clear search to go back?
    // User said "if refresh the whole page the your meal category will disappear", implies persistence until refresh or maybe explicit action.
    // Let's just clear input for now. If they click another category, search is cleared effectively.
});

// Category Handler
document.getElementById('categoryNav').addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON') {
        const category = e.target.getAttribute('data-category');
        switchCategory(category);

        // If switching away from "Your Meal" (and not to it), we might want to clear search input visuals?
        // But we keep the "Your Meal" data populated until refresh or new search.
        if (category !== 'Your Meal') {
            // Optional: clear search input text if they navigate away?
            // searchInput.value = '';
            // updateSearchVisuals('');
        }
    }
});

// Initial load
fetchMenu();

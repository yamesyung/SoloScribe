
document.body.addEventListener("htmx:afterSwap", function(event) {
    // Add event listener for change events on .book-checkbox elements
    event.detail.elt.querySelectorAll('.quote-fav').forEach(function(checkbox) {
        checkbox.addEventListener('change', function(event) {
            var checkboxId = event.target.id;
            // Get the corresponding book link element
            var quoteContainer = document.querySelector('#quote-' + checkboxId.split('-')[1]);

            // Check if the book link element exists
            if (quoteContainer) {
                // Check if the checkbox is checked and update the class of the book link accordingly
                if (event.target.checked) {
                    quoteContainer.classList.add('favorite');
                } else {
                    quoteContainer.classList.remove('favorite');
                }
            }
        });
    });
});


function filterTags() {
    const searchTerm = document.getElementById('tag-search').value.toLowerCase();
    const tagLinks = document.querySelectorAll('.tag-link');

    tagLinks.forEach(tag => {
        const tagText = tag.textContent.toLowerCase();
        const shouldShow = tagText.includes(searchTerm);
        tag.style.display = shouldShow ? 'block' : 'none';
        if (tag.nextElementSibling?.tagName === 'BR') {
            tag.nextElementSibling.style.display = shouldShow ? 'block' : 'none';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('tag-search').addEventListener('input', filterTags);
});


document.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'tags-content') {
        filterTags();
    }
});


// Mobile filter interface
document.addEventListener('DOMContentLoaded', function() {

    // Add mobile-view class to body
    document.body.classList.add('mobile-view');

    // Get favorite count from existing button
    const favBtn = document.querySelector('#fav-btn');
    const favCount = favBtn ? (favBtn.textContent.match(/\((\d+)\)/)?.[1] || '0') : '0';

    // Create mobile header with filter buttons
    const header = document.createElement('div');
    header.className = 'mobile-filter-header';
    header.innerHTML = `
        ${favBtn ? `
        <button class="filter-icon-btn" id="mobile-fav-btn">
            <i class="fa fa-heart-o" aria-hidden="true"></i>
            <span class="btn-label">Favorites</span>

        </button>
        ` : ''}
        <button class="filter-icon-btn" id="mobile-books-btn">
            <i class="fa fa-book" aria-hidden="true"></i>
            <span class="btn-label">Books</span>
        </button>
        <button class="filter-icon-btn" id="mobile-tags-btn">
           <i class="fa fa-tags" aria-hidden="true"></i>
            <span class="btn-label">Tags</span>
        </button>
    `;

    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'filter-overlay';

    // Create books panel - move existing #book-list into it
    const booksPanel = document.createElement('div');
    booksPanel.className = 'filter-side-panel';
    booksPanel.id = 'books-panel';
    const bookListElement = document.querySelector('#book-list');
    booksPanel.innerHTML = `
        <div class="panel-header">
            <span class="panel-title">Books</span>
            <button class="panel-close" data-panel="books-panel">&times;</button>
        </div>
        <div class="panel-content"></div>
    `;

    // Create tags panel - move existing #tags-div into it
    const tagsPanel = document.createElement('div');
    tagsPanel.className = 'filter-side-panel';
    tagsPanel.id = 'tags-panel';
    const tagsDivElement = document.querySelector('#tags-div');
    tagsPanel.innerHTML = `
        <div class="panel-header">
            <span class="panel-title">Tags</span>
            <button class="panel-close" data-panel="tags-panel">&times;</button>
        </div>
        <div class="panel-content"></div>
    `;

    // Add everything to page
    document.body.insertBefore(header, document.body.firstChild);
    document.body.appendChild(overlay);
    document.body.appendChild(booksPanel);
    document.body.appendChild(tagsPanel);

    // Move actual elements into panels (preserves htmx attributes)
    booksPanel.querySelector('.panel-content').appendChild(bookListElement);
    tagsPanel.querySelector('.panel-content').appendChild(tagsDivElement);

    // Make links visible in panels
    bookListElement.querySelectorAll('a').forEach(link => link.style.display = 'block');
    tagsDivElement.querySelectorAll('a').forEach(link => link.style.display = 'block');

    // Event listeners
    if (favBtn) {
        document.getElementById('mobile-fav-btn').addEventListener('click', () => {
            const currentFavBtn = document.querySelector('#fav-btn');
            if (currentFavBtn) currentFavBtn.click();
        });
    }

    document.getElementById('mobile-books-btn').addEventListener('click', () => openPanel('books-panel'));
    document.getElementById('mobile-tags-btn').addEventListener('click', () => openPanel('tags-panel'));

    overlay.addEventListener('click', closeAllPanels);

    document.querySelectorAll('.panel-close').forEach(btn => {
        btn.addEventListener('click', () => closePanel(btn.dataset.panel));
    });

    // Close when link clicked in panel
    document.addEventListener('click', (e) => {
        if (e.target.tagName === 'A' && e.target.closest('.filter-side-panel')) {
            setTimeout(closeAllPanels, 300);
        }
    });

    // Helper functions
    function openPanel(panelId) {
        document.getElementById(panelId).classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closePanel(panelId) {
        document.getElementById(panelId).classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    function closeAllPanels() {
        document.querySelectorAll('.filter-side-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
});
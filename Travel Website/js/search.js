/* ==========================================================================
   SITE-WIDE SEARCH OVERLAY
   Triggered by the magnifier button in the nav, or Cmd/Ctrl+K from anywhere.
   Loads /search-index.json once, ranks matches client-side.
   ========================================================================== */
(function () {
    let INDEX = null;
    let indexLoading = null;

    function loadIndex() {
        if (INDEX) return Promise.resolve(INDEX);
        // Prefer the inlined window.SEARCH_INDEX (works under file:// — fetch() of local files is blocked by browsers).
        if (window.SEARCH_INDEX && Array.isArray(window.SEARCH_INDEX)) {
            INDEX = window.SEARCH_INDEX;
            return Promise.resolve(INDEX);
        }
        if (indexLoading) return indexLoading;
        indexLoading = fetch('search-index.json', { cache: 'force-cache' })
            .then(r => r.json())
            .then(json => { INDEX = json; return INDEX; })
            .catch(err => { console.error('Search index failed to load', err); return []; });
        return indexLoading;
    }

    function scoreEntry(entry, q) {
        if (!q) return 0;
        const needle = q.toLowerCase();
        const meta = (entry.title + ' ' + entry.country + ' ' + entry.city + ' ' + (entry.tags || []).join(' ') + ' ' + entry.excerpt).toLowerCase();
        const body = (entry.body || '').toLowerCase();
        const hay = meta + ' ' + body;
        if (!hay.includes(needle)) {
            const tokens = needle.split(/\s+/).filter(Boolean);
            if (tokens.length > 1 && tokens.every(t => hay.includes(t))) return 1;
            return 0;
        }
        let score = meta.includes(needle) ? 10 : 3;
        if (entry.city && entry.city.toLowerCase() === needle) score += 50;
        if (entry.country && entry.country.toLowerCase() === needle) score += 30;
        if (entry.title.toLowerCase().includes(needle)) score += 20;
        if ((entry.tags || []).some(t => t.toLowerCase() === needle)) score += 25;
        if ((entry.tags || []).some(t => t.toLowerCase().includes(needle))) score += 8;
        if (entry.excerpt && entry.excerpt.toLowerCase().includes(needle)) score += 5;
        return score;
    }

    function search(q) {
        if (!INDEX) return [];
        const trimmed = (q || '').trim();
        if (!trimmed) return INDEX.filter(e => e.type === 'diary').slice(0, 8);
        return INDEX
            .map(e => ({ entry: e, score: scoreEntry(e, trimmed) }))
            .filter(x => x.score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, 12)
            .map(x => x.entry);
    }

    function highlight(text, q) {
        if (!q) return text;
        const safe = text.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
        const escQ = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return safe.replace(new RegExp('(' + escQ + ')', 'gi'), '<mark>$1</mark>');
    }

    function render(results, q) {
        const list = document.getElementById('search-results');
        if (!list) return;
        if (!results.length) {
            list.innerHTML = `<li class="search-empty">No matches for "<strong>${q}</strong>". Try a country, city, or food.</li>`;
            return;
        }
        list.innerHTML = results.map(e => {
            const meta = [e.country, e.city].filter(Boolean).join(' · ') || (e.type === 'page' ? 'Site' : 'Article');
            return `<li>
                <a class="search-result" href="${e.url}">
                    <span class="search-result-meta">${meta}</span>
                    <span class="search-result-title">${highlight(e.title, q)}</span>
                    <span class="search-result-excerpt">${highlight(e.excerpt, q)}</span>
                </a>
            </li>`;
        }).join('');
    }

    function buildOverlay() {
        if (document.getElementById('search-overlay')) return;
        const overlay = document.createElement('div');
        overlay.id = 'search-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-label', 'Site search');
        overlay.innerHTML = `
            <div class="search-modal" role="document">
                <div class="search-input-wrap">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <input type="search" id="search-input" placeholder="Search city, country, food, or topic…" autocomplete="off" aria-label="Search query">
                    <kbd class="search-esc">ESC</kbd>
                </div>
                <ul id="search-results" class="search-results-list" role="listbox"></ul>
                <div class="search-footer">
                    <span><kbd>↑</kbd><kbd>↓</kbd> navigate</span>
                    <span><kbd>↵</kbd> open</span>
                    <span><kbd>Esc</kbd> close</span>
                </div>
            </div>`;
        document.body.appendChild(overlay);

        overlay.addEventListener('click', (e) => { if (e.target === overlay) closeOverlay(); });
        const input = overlay.querySelector('#search-input');
        input.addEventListener('input', () => render(search(input.value), input.value.trim()));
        input.addEventListener('keydown', handleKeyNav);
    }

    function handleKeyNav(e) {
        const list = document.getElementById('search-results');
        if (!list) return;
        const items = Array.from(list.querySelectorAll('a.search-result'));
        if (!items.length) return;
        const current = list.querySelector('a.search-result.active');
        const idx = current ? items.indexOf(current) : -1;
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            const next = items[Math.min(idx + 1, items.length - 1)];
            items.forEach(i => i.classList.remove('active'));
            next.classList.add('active');
            next.scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            const prev = items[Math.max(idx - 1, 0)];
            items.forEach(i => i.classList.remove('active'));
            prev.classList.add('active');
            prev.scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'Enter') {
            e.preventDefault();
            (current || items[0]).click();
        }
    }

    function openOverlay() {
        buildOverlay();
        loadIndex().then(() => {
            const overlay = document.getElementById('search-overlay');
            const input = overlay.querySelector('#search-input');
            overlay.classList.add('open');
            document.body.style.overflow = 'hidden';
            render(search(input.value), input.value.trim());
            setTimeout(() => input.focus(), 50);
        });
    }

    function closeOverlay() {
        const overlay = document.getElementById('search-overlay');
        if (!overlay) return;
        overlay.classList.remove('open');
        document.body.style.overflow = '';
    }

    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            openOverlay();
        } else if (e.key === '/' && document.activeElement && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
            e.preventDefault();
            openOverlay();
        } else if (e.key === 'Escape') {
            closeOverlay();
        }
    });

    // Wire the nav search button — the button is injected by app.js, so wait for it.
    function wireSearchButton() {
        const btn = document.getElementById('search-toggle-btn');
        if (btn && !btn.dataset.wired) {
            btn.dataset.wired = '1';
            btn.addEventListener('click', openOverlay);
        }
    }
    document.addEventListener('DOMContentLoaded', wireSearchButton);
    setTimeout(wireSearchButton, 100);
    setTimeout(wireSearchButton, 500);
})();

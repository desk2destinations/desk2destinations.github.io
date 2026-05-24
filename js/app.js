document.addEventListener('DOMContentLoaded', () => {

    /* ==========================================================================
       0. SHARED NAV — EDIT THIS HTML TO UPDATE THE MENU ON EVERY PAGE
       ========================================================================== */
    const NAV_HTML = `
<header class="site-nav">
    <div class="container nav-container">
        <a href="index.html" class="logo" style="display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--text-primary);">
            <svg width="40" height="40" viewBox="0 0 64 64" fill="none" aria-label="Desk2Destinations Logo">
                <defs><linearGradient id="navPlaneGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff5e3a"/><stop offset="1" stop-color="#feb47b"/></linearGradient></defs>
                <path d="M14 36 H44 L41 54 Q40 58 36 58 H22 Q18 58 17 54 Z" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"/>
                <path d="M44 40 Q52 40 52 46 Q52 52 46 52" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>
                <path d="M22 32 Q24 24 30 22" fill="none" stroke="url(#navPlaneGrad)" stroke-width="2" stroke-linecap="round" opacity="0.6"/>
                <path d="M30 30 Q34 22 40 20" fill="none" stroke="url(#navPlaneGrad)" stroke-width="2" stroke-linecap="round" opacity="0.45"/>
                <path d="M50 6 L26 18 L36 22 L40 32 Z" fill="url(#navPlaneGrad)"/>
            </svg>
            <span style="font-family:var(--font-heading);font-weight:700;color:var(--text-primary);font-size:1.15rem;">Desk2Destinations</span>
        </a>
        <nav class="nav-links">
            <a href="index.html">Home</a>
            <div class="nav-item-dropdown">
                <a href="destinations.html">Destinations <span style="font-size:0.65rem;vertical-align:middle;margin-left:2px;">&#9660;</span></a>
                <div class="dropdown-menu">
                    <div class="dropdown-col"><div class="dropdown-category">Spain</div><a href="barcelona.html" class="dropdown-item">Barcelona</a><a href="spain-madrid.html" class="dropdown-item">Madrid</a><a href="spain-toledo.html" class="dropdown-item">Toledo</a><a href="spain-seville.html" class="dropdown-item">Seville</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">Italy</div><a href="italy-rome.html" class="dropdown-item">Rome</a><a href="italy-amalfi.html" class="dropdown-item">Amalfi Coast</a><a href="italy-venice.html" class="dropdown-item">Venice</a><a href="italy-florence.html" class="dropdown-item">Florence &amp; Pisa</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">Portugal</div><a href="portugal-porto.html" class="dropdown-item">Porto</a><a href="portugal-lisbon.html" class="dropdown-item">Lisbon &amp; Sintra</a><a href="portugal-faro.html" class="dropdown-item">Faro &amp; Carvoeiro</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">Germany</div><a href="germany-berlin.html" class="dropdown-item">Berlin</a><a href="germany-hamburg.html" class="dropdown-item">Hamburg</a><a href="germany-stuttgart.html" class="dropdown-item">Stuttgart</a><a href="germany-blackforest.html" class="dropdown-item">Black Forest</a><a href="germany-munich.html" class="dropdown-item">Munich</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">France</div><a href="france-paris.html" class="dropdown-item">Paris</a><a href="france-paris-2025.html" class="dropdown-item">Paris 2025</a><a href="france-strasbourg.html" class="dropdown-item">Strasbourg</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">Japan</div><a href="japan-tokyo.html" class="dropdown-item">Tokyo</a><a href="japan-kyoto.html" class="dropdown-item">Kyoto</a><a href="japan-osaka.html" class="dropdown-item">Osaka</a><a href="japan-hiroshima.html" class="dropdown-item">Hiroshima</a><a href="japan-sapporo.html" class="dropdown-item">Sapporo</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">New Zealand</div><a href="nz-south.html" class="dropdown-item">South Island</a><a href="nz-north.html" class="dropdown-item">North Island</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">Austria</div><a href="austria-vienna.html" class="dropdown-item">Vienna</a><a href="austria-salzburg.html" class="dropdown-item">Salzburg</a><a href="austria-hallstatt.html" class="dropdown-item">Hallstatt</a><a href="austria-werfen.html" class="dropdown-item">Werfen</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">Switzerland</div><a href="switzerland-zurich.html" class="dropdown-item">Zurich</a><a href="switzerland-interlaken.html" class="dropdown-item">Interlaken</a><a href="switzerland-lucerne.html" class="dropdown-item">Lucerne</a><a href="switzerland-bern.html" class="dropdown-item">Bern</a><a href="switzerland-montreux.html" class="dropdown-item">Montreux</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">India</div><a href="india-westbengal-kolkata.html" class="dropdown-item">West Bengal (Kolkata)</a><a href="india-maharashtra.html" class="dropdown-item">Maharashtra</a><a href="india-karnataka.html" class="dropdown-item">Karnataka</a><a href="india-telangana-hyderabad.html" class="dropdown-item">Telangana (Hyderabad)</a><a href="india-andamans.html" class="dropdown-item">Andamans</a><a href="india-southroadtrip-2025.html" class="dropdown-item">South Road Trip 2025</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">Netherlands &amp; Belgium</div><a href="netherlands-amsterdam.html" class="dropdown-item">Amsterdam</a><a href="netherlands-rotterdam.html" class="dropdown-item">Rotterdam</a><a href="belgium-bruges.html" class="dropdown-item">Bruges</a></div>
                    <div class="dropdown-col"><div class="dropdown-category">More</div><a href="sweden-malmo.html" class="dropdown-item">Sweden (Malm&ouml; &amp; Lund)</a><a href="denmark-copenhagen.html" class="dropdown-item">Denmark (Copenhagen)</a><a href="czech-prague.html" class="dropdown-item">Czech Republic (Prague)</a></div>
                </div>
            </div>
            <a href="food.html">Food Around the World</a>
            <a href="books.html">Books</a>
            <a href="about.html">About Us</a>
            <a href="contact.html">Contact Us</a>
        </nav>
        <div class="nav-actions">
            <button class="theme-toggle" id="theme-toggle-btn" aria-label="Toggle dark/light theme"><svg viewBox="0 0 24 24"></svg></button>
            <button class="search-toggle" id="search-toggle-btn" aria-label="Search the site">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </button>
            <button class="nav-toggle" id="nav-toggle-btn" aria-label="Open mobile menu">&#9776;</button>
        </div>
    </div>
</header>`;

    const navMount = document.getElementById('site-nav');
    if (navMount) {
        navMount.outerHTML = NAV_HTML;
    }

    // --- Mark active link based on current page filename ---
    const currentPage = (window.location.pathname.split('/').pop() || 'index.html').toLowerCase() || 'index.html';
    document.querySelectorAll('.site-nav a[href]').forEach(a => {
        const href = (a.getAttribute('href') || '').toLowerCase();
        if (href === currentPage) {
            a.classList.add('active');
            const dropdown = a.closest('.nav-item-dropdown');
            if (dropdown) {
                const parentLink = dropdown.querySelector(':scope > a');
                if (parentLink) parentLink.classList.add('active');
            }
        }
    });

    /* ==========================================================================
       1. STICKY GLASSMORPHIC HEADER ON SCROLL
       ========================================================================== */
    const navbar = document.querySelector('.site-nav');
    if (navbar) {
        const handleScroll = () => {
            if (window.scrollY > 20) navbar.classList.add('scrolled');
            else navbar.classList.remove('scrolled');
        };
        window.addEventListener('scroll', handleScroll);
        handleScroll();
    }

    /* ==========================================================================
       2. LIGHT/DARK THEME TOGGLE (PERSISTED)
       ========================================================================== */
    {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const rootEl = document.documentElement;
    
    // Check local storage or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    const activeTheme = savedTheme || systemTheme;
    
    // Apply active theme
    rootEl.setAttribute('data-theme', activeTheme);
    updateThemeIcon(activeTheme);
    
    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = rootEl.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        rootEl.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
    
    function updateThemeIcon(theme) {
        // We'll update the SVG inside the button based on active theme
        const iconPath = theme === 'dark' 
            ? '<path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41l-1.06-1.06zm1.06-12.37c-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.38.39-1.03 0-1.41zm-12.37 12.37c-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.38.39-1.03 0-1.41z"/>' // Sun icon
            : '<path d="M12.3 22h-.1c-5.5 0-10-4.5-10-10C2.2 6.8 6.4 2.5 11.7 2c.6-.1 1.2.4 1.1 1.1-.1.5-.5.9-1 1-3.7.8-6.3 4.2-5.9 8.1.3 3.5 3.1 6.3 6.6 6.6 3.9.3 7.3-2.3 8.1-5.9.1-.5.6-.9 1.1-1 .7-.1 1.2.5 1.1 1.1-.5 5.3-4.8 9.5-10.1 9.7z"/>'; // Moon icon
        
        themeToggleBtn.querySelector('svg').innerHTML = iconPath;
    }
    } // end wireThemeToggle

    /* ==========================================================================
       3. INTERSECTION OBSERVER FOR FADE-IN REVEALS
       ========================================================================== */
    const reveals = document.querySelectorAll('.reveal');
    
    if ('IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    revealObserver.unobserve(entry.target); // Trigger only once
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -50px 0px'
        });
        
        reveals.forEach(reveal => revealObserver.observe(reveal));
    } else {
        // Fallback for older browsers
        reveals.forEach(reveal => reveal.classList.add('active'));
    }

    /* ==========================================================================
       4. INTERACTIVE BAR GRAPHS (DEMOGRAPHICS) ANIMATOR
       ========================================================================== */
    const demoSection = document.querySelector('.demographics-wrapper');
    const demoBars = document.querySelectorAll('.demo-bar');
    
    if (demoSection && demoBars.length > 0) {
        const demoObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    demoBars.forEach(bar => {
                        const targetWidth = bar.getAttribute('data-width');
                        bar.style.width = targetWidth;
                    });
                    demoObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });
        
        demoObserver.observe(demoSection);
    }

    /* ==========================================================================
       5. TRAVEL SEARCH & FILTER ENGINE FOR DESTINATION CARDS
       ========================================================================== */
    const filterTabs = document.querySelectorAll('.filter-tab');
    const searchInput = document.getElementById('dest-search');
    const destCards = document.querySelectorAll('.dest-card');
    
    if (destCards.length > 0) {
        let activeFilter = 'all';
        let searchQuery = '';
        
        const filterCards = () => {
            let visibleCount = 0;
            destCards.forEach(card => {
                const category = card.getAttribute('data-category').toLowerCase();
                const title = card.querySelector('h3').textContent.toLowerCase();
                const desc = card.querySelector('p').textContent.toLowerCase();
                
                const matchesCategory = activeFilter === 'all' || category === activeFilter;
                const matchesSearch = title.includes(searchQuery) || desc.includes(searchQuery);
                
                if (matchesCategory && matchesSearch) {
                    card.style.display = 'flex';
                    // Trigger dynamic reveal animation
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 50);
                    visibleCount++;
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
            
            // Handle "No results found" container if visibleCount === 0
            const noResults = document.getElementById('no-results-msg');
            if (noResults) {
                noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            }
        };
        
        // Tab clicks
        filterTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                filterTabs.forEach(t => {
                    t.classList.remove('active');
                    t.setAttribute('aria-selected', 'false');
                });
                tab.classList.add('active');
                tab.setAttribute('aria-selected', 'true');

                activeFilter = tab.getAttribute('data-filter').toLowerCase();
                filterCards();
            });
        });
        
        // Search Input
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                searchQuery = e.target.value.toLowerCase().trim();
                filterCards();
            });
        }
    }

    /* ==========================================================================
       6. COLLABORATION FORM INTAKE HANDLER (Formspree-backed)
       Submits via fetch() to whatever URL the form's action="" points at.
       To activate: replace YOUR_FORM_ID in contact.html with your real
       Formspree form ID. Until then, submissions will visibly fail —
       which is intentional, so you know it's not wired yet.
       ========================================================================== */
    const collabForm = document.getElementById('collab-form');

    if (collabForm) {
        collabForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(collabForm);
            const name = formData.get('name') || 'friend';
            const brand = formData.get('brand') || 'your brand';
            const email = formData.get('email') || '';
            const formContainer = collabForm.parentElement;
            const submitBtn = collabForm.querySelector('button[type="submit"]');
            if (collabForm.action.includes('YOUR_FORM_ID')) {
                if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Submit Proposal'; }
                alert("Our form isn't connected yet — please email hello@desk2destinations.com directly with your proposal.");
                return;
            }
            if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Sending…'; }

            try {
                const res = await fetch(collabForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'Accept': 'application/json' }
                });

                if (!res.ok) throw new Error('Formspree returned ' + res.status);

                formContainer.innerHTML = `
                    <div class="glass-card" style="padding: 40px; text-align: center; border-color: var(--accent-gold); max-width: 500px; margin: 0 auto; animation: fadeInUp 0.6s ease-out forwards;">
                        <div style="width: 60px; height: 60px; border-radius: 50%; background: rgba(255, 126, 95, 0.12); color: var(--accent-forest); display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto;">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>
                        </div>
                        <h3 style="font-size: 1.8rem; margin-bottom: 12px; color: var(--text-primary);">Proposal Received!</h3>
                        <p style="font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 24px; line-height: 1.6;">
                            Thank you, <strong>${name}</strong>. We're thrilled about the opportunity to partner with <strong>${brand}</strong>.
                            We'll reply to <strong>${email}</strong> within 24 hours.
                        </p>
                    </div>
                `;
            } catch (err) {
                if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Submit Proposal'; }
                alert("Couldn't send the message — the contact form isn't fully connected yet. Please email hello@desk2destinations.com directly.");
                console.error(err);
            }
        });
    }

    /* ==========================================================================
       6b. NEWSLETTER FORM (Formspree-backed)
       ========================================================================== */
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = newsletterForm.querySelector('button[type="submit"]');
            const originalText = submitBtn ? submitBtn.textContent : '';
            if (newsletterForm.action.includes('YOUR_FORM_ID')) {
                newsletterForm.innerHTML = '<p style="color: var(--accent-forest); font-weight: 600; padding: 16px;">✓ Thanks — please email hello@desk2destinations.com and we\'ll add you manually until our newsletter system is live.</p>';
                return;
            }
            if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Sending…'; }
            try {
                const res = await fetch(newsletterForm.action, {
                    method: 'POST',
                    body: new FormData(newsletterForm),
                    headers: { 'Accept': 'application/json' }
                });
                if (!res.ok) throw new Error('Formspree returned ' + res.status);
                newsletterForm.innerHTML = '<p style="color: var(--accent-forest); font-weight: 600; padding: 16px;">✓ You\'re in. Welcome to the Desk2Destinations family.</p>';
            } catch (err) {
                if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = originalText; }
                alert("Couldn't subscribe right now — newsletter isn't fully connected yet. Please email hello@desk2destinations.com to be added manually.");
                console.error(err);
            }
        });
    }

    /* ==========================================================================
       7. MOBILE MENU BAR MOBILE TOGGLER
       ========================================================================== */
    {
    const navToggle = document.getElementById('nav-toggle-btn');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            const isVisible = navLinks.style.display === 'flex';
            if (isVisible) {
                navLinks.style.display = 'none';
                navToggle.innerHTML = '&#9776;'; // Hamburger
            } else {
                navLinks.style.display = 'flex';
                navLinks.style.flexDirection = 'column';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '100%';
                navLinks.style.left = '0';
                navLinks.style.width = '100%';
                navLinks.style.background = 'var(--bg-glass)';
                navLinks.style.backdropFilter = 'blur(16px)';
                navLinks.style.padding = '24px';
                navLinks.style.borderBottom = '1px solid var(--border-color)';
                navLinks.style.boxShadow = 'var(--shadow-md)';
                navLinks.style.gap = '20px';
                navToggle.innerHTML = '&times;'; // Cross
            }
        });

        // Mobile: tap parent dropdown link to toggle its menu instead of navigating
        document.querySelectorAll('.nav-item-dropdown > a').forEach(parentLink => {
            parentLink.addEventListener('click', (e) => {
                if (window.matchMedia('(max-width: 768px)').matches) {
                    e.preventDefault();
                    parentLink.parentElement.classList.toggle('open');
                }
            });
        });
    }
    }

    const chHeroImg = document.getElementById('ch-hero-img');
    if (chHeroImg) {
        const onScroll = () => {
            const y = window.scrollY;
            if (y < window.innerHeight) {
                chHeroImg.style.transform = `translateY(${y * 0.4}px) scale(1.05)`;
            }
        };
        window.addEventListener('scroll', onScroll, { passive: true });
    }
});

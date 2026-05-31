import os

files = sorted(os.listdir("assets/food-gallery"))
items = []
for f in files:
    items.append(f'        <a href="assets/food-gallery/{f}" class="gallery-item" data-full="assets/food-gallery/{f}"><img src="assets/food-gallery/{f}" alt="Food photo" loading="lazy"></a>')
grid = "\n".join(items)

TPL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Food Photo Gallery | Desk2Destinations</title>
    <link rel="icon" href="assets/logo.svg" type="image/svg+xml">
    <meta name="description" content="A scrolling photo gallery of vegetarian and vegan food from our travels around the world.">
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/search.css">
    <style>
        .gallery-hero { padding: 130px 0 40px 0; background: var(--bg-secondary); border-bottom: 1px solid var(--border-color); text-align: center; }
        .gallery-hero h1 { font-family: var(--font-heading); font-size: 2.8rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.02em; margin-bottom: 12px; }
        .gallery-hero .kicker { font-family: var(--font-heading); font-style: italic; color: var(--accent-terracotta); font-size: 0.95rem; letter-spacing: 0.18em; text-transform: uppercase; display: block; margin-bottom: 12px; }
        .gallery-hero p { color: var(--text-secondary); max-width: 640px; margin: 0 auto 14px auto; line-height: 1.6; }
        .gallery-hero .meta { font-size: 0.85rem; color: var(--text-muted); }
        .gallery-hero a { color: var(--accent-terracotta); text-decoration: none; font-weight: 600; }
        .gallery-section { padding: 50px 0 80px 0; }
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 6px; max-width: 1400px; margin: 0 auto; padding: 0 14px;
        }
        .gallery-item {
            position: relative; aspect-ratio: 1 / 1; overflow: hidden;
            border-radius: 6px; background: var(--bg-secondary);
            cursor: zoom-in; transition: transform 0.18s ease;
        }
        .gallery-item:hover { transform: scale(1.03); z-index: 2; }
        .gallery-item img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .lightbox {
            position: fixed; inset: 0; background: rgba(10,5,10,0.94);
            display: none; align-items: center; justify-content: center;
            z-index: 9999; cursor: zoom-out; padding: 30px;
        }
        .lightbox.open { display: flex; }
        .lightbox img { max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 6px; box-shadow: 0 20px 60px rgba(0,0,0,0.6); }
        .lightbox-close {
            position: absolute; top: 20px; right: 24px;
            background: none; border: none; color: #fff;
            font-size: 2rem; cursor: pointer; line-height: 1;
        }
        .lightbox-nav {
            position: absolute; top: 50%; transform: translateY(-50%);
            background: rgba(255,255,255,0.1); border: none; color: #fff;
            width: 48px; height: 48px; border-radius: 50%;
            font-size: 1.4rem; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
        }
        .lightbox-nav:hover { background: rgba(255,255,255,0.2); }
        .lightbox-prev { left: 18px; }
        .lightbox-next { right: 18px; }
        .lightbox-counter {
            position: absolute; bottom: 18px; left: 50%; transform: translateX(-50%);
            color: rgba(255,255,255,0.7); font-size: 0.85rem; letter-spacing: 0.05em;
        }
        @media (max-width: 700px) {
            .gallery-hero h1 { font-size: 2rem; }
            .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 4px; }
        }
    </style>
</head>
<body>
    <div id="site-nav"></div>

    <section class="gallery-hero">
        <div class="container">
            <span class="kicker">Snapshots from the table</span>
            <h1>Food Photo Gallery</h1>
            <p>Real plates, real meals, real travel days. Mostly vegetarian, occasionally vegan, frequently dessert. Click any photo to zoom &mdash; use arrows or swipe to browse.</p>
            <p class="meta">__COUNT__ photos &middot; from <a href="food.html">our restaurant list &rarr;</a></p>
        </div>
    </section>

    <section class="gallery-section">
        <div class="gallery-grid">
__GRID__
        </div>
    </section>

    <div class="lightbox" id="lightbox" role="dialog" aria-label="Photo viewer">
        <button class="lightbox-close" aria-label="Close">&times;</button>
        <button class="lightbox-nav lightbox-prev" aria-label="Previous">&#8249;</button>
        <img src="" alt="">
        <button class="lightbox-nav lightbox-next" aria-label="Next">&#8250;</button>
        <div class="lightbox-counter"></div>
    </div>

    <footer class="site-footer">
        <div class="container footer-grid">
            <div class="footer-col footer-about">
                <a href="index.html" class="logo" style="display:flex; align-items:center; gap:10px; text-decoration:none; margin-bottom:16px;">
                    <svg width="32" height="32" viewBox="0 0 64 64" fill="none" style="color:var(--text-primary);" aria-label="Logo"><defs><linearGradient id="footPlaneGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff5e3a"/><stop offset="1" stop-color="#feb47b"/></linearGradient></defs><path d="M14 36 H44 L41 54 Q40 58 36 58 H22 Q18 58 17 54 Z" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"/><path d="M44 40 Q52 40 52 46 Q52 52 46 52" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><path d="M50 6 L26 18 L36 22 L40 32 Z" fill="url(#footPlaneGrad)"/></svg>
                    <span style="font-family:var(--font-heading); font-weight:700; color:var(--text-primary); font-size:1rem;">Desk2Destinations</span>
                </a>
                <p>An Indian couple balancing full-time corporate jobs and part-time wanderlust.</p>
            </div>
            <div class="footer-col">
                <h4>Quick Navigation</h4>
                <div class="footer-links-grid">
                    <a href="index.html">Home</a>
                    <a href="destinations.html">Destinations</a>
                    <a href="food.html">Food Around the World</a>
                    <a href="gallery.html">Gallery</a>
                    <a href="about.html">About Us</a>
                    <a href="contact.html">Contact Us</a>
                </div>
            </div>
        </div>
        <div class="container footer-bottom">
            <p>&copy; 2026 Desk2Destinations.</p>
            <div class="footer-legal">
                <a href="privacy.html">Privacy</a><span>&middot;</span>
                <a href="terms.html">Terms</a><span>&middot;</span>
                <a href="cookies.html">Cookies</a><span>&middot;</span>
                <a href="disclaimer.html">Disclaimer</a>
            </div>
        </div>
    </footer>

    <script src="js/app.js"></script>
    <script src="search-index.js"></script>
    <script src="js/search.js"></script>
    <script>
    (function() {
        var items = Array.from(document.querySelectorAll('.gallery-item'));
        var lb = document.getElementById('lightbox');
        var img = lb.querySelector('img');
        var counter = lb.querySelector('.lightbox-counter');
        var closeBtn = lb.querySelector('.lightbox-close');
        var prevBtn = lb.querySelector('.lightbox-prev');
        var nextBtn = lb.querySelector('.lightbox-next');
        var idx = 0;
        function show(i) {
            idx = (i + items.length) % items.length;
            img.src = items[idx].dataset.full;
            counter.textContent = (idx + 1) + ' / ' + items.length;
        }
        function openLB(i) { show(i); lb.classList.add('open'); document.body.style.overflow = 'hidden'; }
        function closeLB() { lb.classList.remove('open'); document.body.style.overflow = ''; img.src = ''; }
        items.forEach(function(el, i) {
            el.addEventListener('click', function(e) { e.preventDefault(); openLB(i); });
        });
        closeBtn.addEventListener('click', function(e) { e.stopPropagation(); closeLB(); });
        prevBtn.addEventListener('click', function(e) { e.stopPropagation(); show(idx - 1); });
        nextBtn.addEventListener('click', function(e) { e.stopPropagation(); show(idx + 1); });
        lb.addEventListener('click', function(e) { if (e.target === lb) closeLB(); });
        document.addEventListener('keydown', function(e) {
            if (!lb.classList.contains('open')) return;
            if (e.key === 'Escape') closeLB();
            else if (e.key === 'ArrowLeft') show(idx - 1);
            else if (e.key === 'ArrowRight') show(idx + 1);
        });
        var tx = 0;
        lb.addEventListener('touchstart', function(e) { tx = e.touches[0].clientX; }, {passive:true});
        lb.addEventListener('touchend', function(e) {
            var dx = e.changedTouches[0].clientX - tx;
            if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
        }, {passive:true});
    })();
    </script>
</body>
</html>
"""

out = TPL.replace("__GRID__", grid).replace("__COUNT__", str(len(files)))
with open("gallery.html", "w", encoding="utf-8", newline="") as f:
    f.write(out)
print(f"gallery.html: {len(out)} bytes, {len(files)} tiles")

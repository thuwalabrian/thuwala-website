// enhancements.js - Minimal version (no image interference)

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Back to Top Button
    const backToTop = document.createElement('a');
    backToTop.href = '#top';
    backToTop.className = 'back-to-top';
    backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(backToTop);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });
    
    // 2. Smooth scroll for anchor links ONLY
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            if (href.startsWith('#') && document.querySelector(href)) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // 3. Ad navigation functionality - 2 SECOND ROTATION
    function setupAdNavigation() {
        const adsContainer = document.querySelector('.hero-ads-container');
        if (!adsContainer) return;
        
        const ads = adsContainer.querySelectorAll('.hero-ad');
        if (ads.length <= 1) return;
        
        const prevBtn = adsContainer.querySelector('.ad-nav-btn.prev-btn');
        const nextBtn = adsContainer.querySelector('.ad-nav-btn.next-btn');
        const dots = adsContainer.querySelectorAll('.ad-dot');
        const playBtn = adsContainer.querySelector('.ad-play-btn');
        
        let currentAd = 0;
        let autoPlay = true;
        let slideInterval;
        
        // Set rotation interval to 2 seconds (2000ms)
        const ROTATION_INTERVAL = 2000;
        
        function showAd(index) {
            // Hide all ads
            ads.forEach(ad => {
                ad.classList.remove('active');
            });
            
            // Update dots
            dots.forEach(dot => dot.classList.remove('active'));
            
            // Show selected ad
            currentAd = index;
            ads[currentAd].classList.add('active');
            
            if (dots[currentAd]) {
                dots[currentAd].classList.add('active');
            }
        }
        
        // Set up navigation buttons
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                let newIndex = currentAd - 1;
                if (newIndex < 0) newIndex = ads.length - 1;
                showAd(newIndex);
                resetAutoPlay();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                let newIndex = (currentAd + 1) % ads.length;
                showAd(newIndex);
                resetAutoPlay();
            });
        }
        
        // Set up dot navigation
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                showAd(index);
                resetAutoPlay();
            });
        });
        
        // Set up play/pause button
        if (playBtn) {
            playBtn.addEventListener('click', () => {
                autoPlay = !autoPlay;
                playBtn.innerHTML = autoPlay ? 
                    '<i class="fas fa-pause"></i>' : 
                    '<i class="fas fa-play"></i>';
                
                if (autoPlay) {
                    startAutoPlay();
                } else {
                    clearInterval(slideInterval);
                }
            });
        }
        
        function startAutoPlay() {
            if (ads.length <= 1) return;
            
            clearInterval(slideInterval);
            
            // Change ad every 2 seconds
            slideInterval = setInterval(() => {
                if (autoPlay) {
                    let nextIndex = (currentAd + 1) % ads.length;
                    showAd(nextIndex);
                }
            }, ROTATION_INTERVAL);
        }
        
        function resetAutoPlay() {
            if (autoPlay) {
                clearInterval(slideInterval);
                startAutoPlay();
            }
        }
        
        // Initialize
        if (ads.length > 0) {
            showAd(0);
            startAutoPlay();
        }
    }
    
    // Initialize ad navigation
    setTimeout(setupAdNavigation, 500);
    
    // 4. Toast notification system
    window.showToast = function(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    };
    
    // 5. Counter animation for stats
    function animateCounter(element, target, duration = 4000) {
        let start = 0;
        const increment = target / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start);
            }
        }, 16);
    }
    
    // 6. Initialize counters when in viewport
    const counters = document.querySelectorAll('.counter');
    if (counters.length > 0) {
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = parseInt(entry.target.getAttribute('data-target'));
                    animateCounter(entry.target, target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => counterObserver.observe(counter));
    }
    
    // 7. Dynamic year in footer
    const yearElement = document.querySelector('#current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
    
    // 8. Form field validation styling
    const formInputs = document.querySelectorAll('.form-control');
    formInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim() !== '') {
                this.classList.add('filled');
            } else {
                this.classList.remove('filled');
            }
        });
        
        if (input.value.trim() !== '') {
            input.classList.add('filled');
        }
    });
});
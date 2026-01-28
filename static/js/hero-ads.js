// ============================================
// MODERN HERO SECTION - INTERACTIVE AD CAROUSEL
// ============================================

class HeroAdCarousel {
    constructor() {
        this.ads = document.querySelectorAll('.hero-ad');
        this.dotsContainer = document.getElementById('adNavDots');
        this.playBtn = document.getElementById('adPlayBtn');
        this.playIcon = document.getElementById('adPlayIcon');
        this.prevBtn = document.getElementById('prevAdBtn');
        this.nextBtn = document.getElementById('nextAdBtn');
        
        this.currentIndex = 0;
        this.interval = null;
        this.intervalTime = 6000; // 6 seconds per ad
        this.isPlaying = true;
        
        if (this.ads.length > 0) {
            this.initialize();
        }
    }
    
    initialize() {
        this.setupAdStyles();
        
        // Only setup carousel if multiple ads
        if (this.ads.length > 1) {
            this.createDots();
            this.startAutoPlay();
            this.setupEventListeners();
        } else {
            this.hideNavigation();
        }
    }
    
    setupAdStyles() {
        this.ads.forEach(ad => {
            const bgColor = ad.dataset.backgroundColor || '#2563eb';
            const textColor = ad.dataset.textColor || '#ffffff';
            const imageUrl = ad.dataset.imageUrl;
            
            // Darken color for gradient effect
            const darkColor = this.darkenColor(bgColor, 20);
            
            // Set background with gradient and optional image
            if (imageUrl) {
                ad.style.background = `
                    linear-gradient(135deg, ${bgColor}e6, ${darkColor}e6),
                    url('${imageUrl}')
                `;
                ad.style.backgroundSize = 'cover';
                ad.style.backgroundPosition = 'center';
                ad.style.backgroundBlendMode = 'overlay';
            } else {
                ad.style.background = `linear-gradient(135deg, ${bgColor}, ${darkColor})`;
            }
            
            // Set text color
            ad.style.color = textColor;
            
            // Style buttons
            const primaryButtons = ad.querySelectorAll('.btn-ad');
            primaryButtons.forEach(btn => {
                btn.style.backgroundColor = textColor;
                btn.style.color = bgColor;
            });
            
            const outlineButtons = ad.querySelectorAll('.btn-ad-outline');
            outlineButtons.forEach(btn => {
                btn.style.borderColor = textColor;
                btn.style.color = textColor;
                btn.style.backgroundColor = 'transparent';
            });
        });
    }
    
    darkenColor(hex, percent) {
        // Remove # if present
        hex = hex.replace('#', '');
        
        // Parse to RGB
        let r = parseInt(hex.substring(0, 2), 16);
        let g = parseInt(hex.substring(2, 4), 16);
        let b = parseInt(hex.substring(4, 6), 16);
        
        // Darken
        r = Math.max(0, Math.floor(r * (100 - percent) / 100));
        g = Math.max(0, Math.floor(g * (100 - percent) / 100));
        b = Math.max(0, Math.floor(b * (100 - percent) / 100));
        
        // Convert back to hex
        r = r.toString(16).padStart(2, '0');
        g = g.toString(16).padStart(2, '0');
        b = b.toString(16).padStart(2, '0');
        
        return `#${r}${g}${b}`;
    }
    
    hideNavigation() {
        const elements = [this.dotsContainer, this.playBtn, this.prevBtn, this.nextBtn];
        elements.forEach(el => {
            if (el) el.style.display = 'none';
        });
    }
    
    createDots() {
        if (!this.dotsContainer) return;
        
        this.ads.forEach((_, index) => {
            const dot = document.createElement('button');
            dot.className = `ad-dot ${index === 0 ? 'active' : ''}`;
            dot.setAttribute('aria-label', `View advertisement ${index + 1} of ${this.ads.length}`);
            
            dot.addEventListener('click', () => {
                this.goToAd(index);
                this.resetAutoPlay();
            });
            
            this.dotsContainer.appendChild(dot);
        });
    }
    
    goToAd(index) {
        // Validate index
        if (index < 0 || index >= this.ads.length) return;
        
        // Hide current ad with fade out
        this.ads[this.currentIndex].classList.remove('active');
        this.updateDot(this.currentIndex, false);
        
        // Update index and show new ad with fade in
        this.currentIndex = index;
        this.ads[this.currentIndex].classList.add('active');
        this.updateDot(this.currentIndex, true);
        
        // Update any ad stats that show current position
        this.updateAdStats();
    }
    
    updateDot(index, isActive) {
        const dots = document.querySelectorAll('.ad-dot');
        if (dots[index]) {
            dots[index].classList.toggle('active', isActive);
            
            // Reset animation for active dot
            if (isActive) {
                dots[index].style.animation = 'none';
                void dots[index].offsetWidth; // Trigger reflow
                dots[index].style.animation = 'dotProgress 6s linear forwards';
            }
        }
    }
    
    updateAdStats() {
        // Update position indicators if they exist
        const positionElements = document.querySelectorAll('.ad-stat:nth-child(1) span');
        positionElements.forEach(el => {
            el.textContent = `${this.currentIndex + 1}/${this.ads.length}`;
        });
    }
    
    nextAd() {
        const nextIndex = (this.currentIndex + 1) % this.ads.length;
        this.goToAd(nextIndex);
    }
    
    prevAd() {
        const prevIndex = this.currentIndex === 0 ? this.ads.length - 1 : this.currentIndex - 1;
        this.goToAd(prevIndex);
    }
    
    startAutoPlay() {
        // Clear any existing interval
        if (this.interval) {
            clearInterval(this.interval);
        }
        
        // Start new interval
        this.interval = setInterval(() => {
            this.nextAd();
        }, this.intervalTime);
        
        // Update play button state
        this.isPlaying = true;
        if (this.playIcon) {
            this.playIcon.className = 'fas fa-pause';
        }
        
        // Start dot animation
        this.startDotAnimation();
    }
    
    startDotAnimation() {
        const activeDot = document.querySelector('.ad-dot.active');
        if (activeDot) {
            activeDot.style.animation = 'dotProgress 6s linear forwards';
        }
    }
    
    pauseAutoPlay() {
        // Clear interval
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        
        // Update play button state
        this.isPlaying = false;
        if (this.playIcon) {
            this.playIcon.className = 'fas fa-play';
        }
        
        // Pause dot animation
        const activeDot = document.querySelector('.ad-dot.active');
        if (activeDot) {
            activeDot.style.animationPlayState = 'paused';
        }
    }
    
    resetAutoPlay() {
        if (this.isPlaying) {
            this.pauseAutoPlay();
            this.startAutoPlay();
        }
    }
    
    togglePlay() {
        if (this.isPlaying) {
            this.pauseAutoPlay();
        } else {
            this.startAutoPlay();
        }
    }
    
    setupEventListeners() {
        // Play/Pause button
        if (this.playBtn) {
            this.playBtn.addEventListener('click', () => this.togglePlay());
        }
        
        // Previous button
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => {
                this.prevAd();
                this.resetAutoPlay();
            });
        }
        
        // Next button
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => {
                this.nextAd();
                this.resetAutoPlay();
            });
        }
        
        // Skip buttons
        document.querySelectorAll('.skip-ad-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.nextAd();
                this.resetAutoPlay();
            });
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Only respond if hero section is in view
            const heroSection = document.getElementById('heroSection');
            if (!this.isElementInViewport(heroSection)) return;
            
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                this.prevAd();
                this.resetAutoPlay();
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                this.nextAd();
                this.resetAutoPlay();
            } else if (e.key === ' ' || e.key === 'Spacebar') {
                e.preventDefault();
                this.togglePlay();
            }
        });
        
        // Pause on hover (for better UX)
        const heroSection = document.getElementById('heroSection');
        if (heroSection) {
            heroSection.addEventListener('mouseenter', () => {
                if (this.isPlaying) {
                    this.pauseAutoPlay();
                }
            });
            
            heroSection.addEventListener('mouseleave', () => {
                if (this.isPlaying) {
                    this.startAutoPlay();
                }
            });
            
            // Touch events for mobile
            heroSection.addEventListener('touchstart', () => {
                if (this.isPlaying) {
                    this.pauseAutoPlay();
                }
            });
            
            heroSection.addEventListener('touchend', () => {
                if (this.isPlaying) {
                    this.startAutoPlay();
                }
            });
        }
        
        // Swipe support for mobile
        this.setupSwipeSupport();
    }
    
    setupSwipeSupport() {
        const heroSection = document.getElementById('heroSection');
        if (!heroSection) return;
        
        let touchStartX = 0;
        let touchEndX = 0;
        
        heroSection.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        heroSection.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe(touchStartX, touchEndX);
        });
    }
    
    handleSwipe(startX, endX) {
        const minSwipeDistance = 50;
        const distance = startX - endX;
        
        if (Math.abs(distance) < minSwipeDistance) return;
        
        if (distance > 0) {
            // Swipe left - next ad
            this.nextAd();
        } else {
            // Swipe right - previous ad
            this.prevAd();
        }
        
        this.resetAutoPlay();
    }
    
    isElementInViewport(el) {
        if (!el) return false;
        
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if hero section exists
    const heroSection = document.getElementById('heroSection');
    if (!heroSection) return;
    
    // Check if there are ads
    const ads = document.querySelectorAll('.hero-ad');
    if (ads.length === 0) return;
    
    // Initialize carousel
    window.heroAdCarousel = new HeroAdCarousel();
    
    // Add loading animation for stats
    const statNumbers = document.querySelectorAll('.stat-number');
    if (statNumbers.length > 0) {
        statNumbers.forEach(stat => {
            const target = parseInt(stat.getAttribute('data-target'));
            if (isNaN(target)) return;
            
            let current = 0;
            const increment = target / 50; // 50 steps
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    stat.textContent = target;
                    clearInterval(timer);
                } else {
                    stat.textContent = Math.floor(current);
                }
            }, 30);
        });
    }
});

// Export for potential manual control
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HeroAdCarousel;
}
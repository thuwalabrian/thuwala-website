/**
 * Alpine.js Components & Utilities
 * Reusable interactive components powered by Alpine.js
 */

// Global Alpine Component Library
window.AlpineComponents = {
  
  /**
   * Modal Component
   * Usage: x-data="AlpineComponents.modal()"
   */
  modal() {
    return {
      open: false,
      toggle() { this.open = !this.open; },
      close() { this.open = false; },
      show() { this.open = true; },
    };
  },

  /**
   * Accordion/Collapsible Component
   * Usage: x-data="AlpineComponents.accordion()"
   */
  accordion() {
    return {
      items: [],
      activeId: null,
      toggle(id) {
        this.activeId = this.activeId === id ? null : id;
      },
      isActive(id) {
        return this.activeId === id;
      },
    };
  },

  /**
   * Tab Component
   * Usage: x-data="AlpineComponents.tabs()"
   */
  tabs(defaultTab = 'tab-1') {
    return {
      activeTab: defaultTab,
      setTab(tabId) { this.activeTab = tabId; },
      isActive(tabId) { return this.activeTab === tabId; },
    };
  },

  /**
   * Filter Component
   * Usage: x-data="AlpineComponents.filter()"
   */
  filter(items = []) {
    return {
      items: items,
      activeFilter: 'all',
      filteredItems: items,
      setFilter(category) {
        this.activeFilter = category;
        this.applyFilter();
      },
      applyFilter() {
        if (this.activeFilter === 'all') {
          this.filteredItems = this.items;
        } else {
          this.filteredItems = this.items.filter(item => 
            item.category === this.activeFilter
          );
        }
      },
      init() {
        this.applyFilter();
      }
    };
  },

  /**
   * Search Component
   * Usage: x-data="AlpineComponents.search(items)"
   */
  search(items = []) {
    return {
      items: items,
      query: '',
      get results() {
        if (!this.query) return this.items;
        const q = this.query.toLowerCase();
        return this.items.filter(item => 
          item.title?.toLowerCase().includes(q) ||
          item.description?.toLowerCase().includes(q) ||
          item.tags?.some(tag => tag.toLowerCase().includes(q))
        );
      }
    };
  },

  /**
   * Dropdown Component
   * Usage: x-data="AlpineComponents.dropdown()"
   */
  dropdown() {
    return {
      open: false,
      toggle() { this.open = !this.open; },
      close() { this.open = false; },
      @click.away: () => { this.open = false; }
    };
  },

  /**
   * Counter/Number Animation
   * Usage: x-data="AlpineComponents.counter(target)"
   */
  counter(target = 100, duration = 2000) {
    return {
      current: 0,
      target: target,
      init() {
        const increment = this.target / (duration / 16);
        const interval = setInterval(() => {
          if (this.current < this.target) {
            this.current = Math.min(this.current + increment, this.target);
          } else {
            clearInterval(interval);
          }
        }, 16);
      }
    };
  },

  /**
   * Form Component
   * Usage: x-data="AlpineComponents.form()"
   */
  form(fields = {}) {
    return {
      fields: fields,
      errors: {},
      submitted: false,
      isValid() {
        return Object.values(this.errors).every(err => !err);
      },
      validate(fieldName, rules = []) {
        // Simple validation
        const value = this.fields[fieldName];
        this.errors[fieldName] = '';
        
        rules.forEach(rule => {
          if (rule.type === 'required' && !value) {
            this.errors[fieldName] = rule.message || 'This field is required';
          } else if (rule.type === 'email' && value && !value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
            this.errors[fieldName] = rule.message || 'Invalid email format';
          } else if (rule.type === 'minLength' && value && value.length < rule.value) {
            this.errors[fieldName] = rule.message || `Minimum ${rule.value} characters`;
          }
        });
      },
      reset() {
        Object.keys(this.fields).forEach(key => this.fields[key] = '');
        this.errors = {};
        this.submitted = false;
      }
    };
  },

  /**
   * Admin Form Validator
   * Usage: x-data="AlpineComponents.formValidator({ fields: {...}, rules: {...} })"
   */
  formValidator({ fields = {}, rules = {} } = {}) {
    return {
      fields: fields,
      rules: rules,
      errors: {},
      touched: {},
      validateField(name) {
        const value = this.fields[name];
        const fieldRules = this.rules[name] || [];
        let error = '';

        fieldRules.forEach(rule => {
          if (error) return;
          if (rule.type === 'required' && (!value || String(value).trim() === '')) {
            error = rule.message || 'This field is required.';
          }
          if (rule.type === 'email' && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            error = rule.message || 'Enter a valid email address.';
          }
          if (rule.type === 'minLength' && value && String(value).length < rule.value) {
            error = rule.message || `Minimum ${rule.value} characters.`;
          }
          if (rule.type === 'url' && value && !/^(https?:\/\/|\/).+/.test(value)) {
            error = rule.message || 'Enter a valid URL.';
          }
          if (rule.type === 'hex' && value && !/^#[0-9A-Fa-f]{6}$/.test(value)) {
            error = rule.message || 'Enter a valid hex color (e.g., #2563eb).';
          }
          if (rule.type === 'match' && value !== this.fields[rule.field]) {
            error = rule.message || 'Values do not match.';
          }
        });

        this.errors[name] = error;
        return !error;
      },
      touch(name) {
        this.touched[name] = true;
        this.validateField(name);
      },
      validateAll() {
        return Object.keys(this.rules).every(name => this.validateField(name));
      },
      isValid() {
        return Object.values(this.errors).every(err => !err);
      }
    };
  },

  /**
   * Notification/Toast Component
   * Usage: x-data="AlpineComponents.toast()"
   */
  toast() {
    return {
      notifications: [],
      show(message, type = 'info', duration = 3000) {
        const id = Date.now();
        this.notifications.push({ id, message, type });
        setTimeout(() => {
          this.notifications = this.notifications.filter(n => n.id !== id);
        }, duration);
      },
      success(message, duration = 3000) { this.show(message, 'success', duration); },
      error(message, duration = 3000) { this.show(message, 'error', duration); },
      warning(message, duration = 3000) { this.show(message, 'warning', duration); },
      remove(id) {
        this.notifications = this.notifications.filter(n => n.id !== id);
      }
    };
  },

  /**
   * Loading State Component
   * Usage: x-data="AlpineComponents.loading()"
   */
  loading() {
    return {
      isLoading: false,
      start() { this.isLoading = true; },
      stop() { this.isLoading = false; },
      async load(asyncFn) {
        this.start();
        try {
          return await asyncFn();
        } finally {
          this.stop();
        }
      }
    };
  },

  /**
   * Pagination Component
   * Usage: x-data="AlpineComponents.pagination(items, perPage)"
   */
  pagination(items = [], perPage = 10) {
    return {
      items: items,
      perPage: perPage,
      currentPage: 1,
      get totalPages() {
        return Math.ceil(this.items.length / this.perPage);
      },
      get paginatedItems() {
        const start = (this.currentPage - 1) * this.perPage;
        return this.items.slice(start, start + this.perPage);
      },
      nextPage() {
        if (this.currentPage < this.totalPages) this.currentPage++;
      },
      prevPage() {
        if (this.currentPage > 1) this.currentPage--;
      },
      goToPage(page) {
        this.currentPage = Math.max(1, Math.min(page, this.totalPages));
      }
    };
  },

  /**
   * Toggle/Switch Component
   * Usage: x-data="AlpineComponents.toggle()"
   */
  toggle(initialState = false) {
    return {
      enabled: initialState,
      toggle() { this.enabled = !this.enabled; },
      enable() { this.enabled = true; },
      disable() { this.enabled = false; },
    };
  },

  /**
   * Menu Component
   * Usage: x-data="AlpineComponents.menu()"
   */
  menu() {
    return {
      open: false,
      toggle() { this.open = !this.open; },
      close() { this.open = false; },
      onClickAway() { this.open = false; }
    };
  },

  /**
   * Smooth Scroll Component
   * Usage: x-data="AlpineComponents.smoothScroll()"
   */
  smoothScroll() {
    return {
      scrollToElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      },
      scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      },
      scrollToBottom() {
        window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
      }
    };
  }
};

/**
 * Initialize AOS (Animate On Scroll) - runs immediately and also after Alpine init
 */
function initAOS() {
  if (window.AOS) {
    AOS.init({
      duration: 800,
      easing: 'ease-out-cubic',
      once: true,
      mirror: false,
      offset: 100,
      disable: false
    });
  }
}

// Initialize AOS immediately
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAOS);
} else {
  initAOS();
}

// Also initialize when Alpine is ready
if (document.addEventListener) {
  document.addEventListener('alpine:initialized', initAOS);
}

/**
 * Counter Animation for Stats
 */
function animateCounters() {
  const counters = document.querySelectorAll('[x-data*="counter"]');
  counters.forEach(counter => {
    const target = parseInt(counter.dataset.target) || 100;
    const element = counter.querySelector('[x-text]');
    
    if (!element) return;

    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      element.textContent = Math.floor(current);
    }, 30);
  });
}

// Auto-animate counters on page load
document.addEventListener('DOMContentLoaded', animateCounters);

/**
 * Utility: Smooth transitions for Alpine
 */
if (typeof Alpine !== 'undefined') {
  Alpine.magic('transition', () => {
    return {
      fadeIn: 'transition duration-300 opacity-0',
      slideDown: 'transition duration-300 translate-y-4 opacity-0',
      scaleIn: 'transition duration-300 scale-95 opacity-0'
    };
  });
} else {
  // If Alpine hasn't loaded yet, wait for it
  document.addEventListener('alpine:init', () => {
    Alpine.magic('transition', () => {
      return {
        fadeIn: 'transition duration-300 opacity-0',
        slideDown: 'transition duration-300 translate-y-4 opacity-0',
        scaleIn: 'transition duration-300 scale-95 opacity-0'
      };
    });
  });
}

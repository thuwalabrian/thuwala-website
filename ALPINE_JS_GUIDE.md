# Alpine.js Integration - Complete Guide

## Overview
Alpine.js has been integrated into your Thuwala website for smooth, lightweight interactivity without the overhead of larger frameworks.

## What's Implemented

### 1. **Navigation Menu** (base.html)
- Alpine-powered mobile menu toggle
- Smooth open/close animations with `x-show` transitions
- Click-away detection to close menu when clicking outside

```html
<nav x-data="{ open: false }" x-cloak>
  <button @click="open = !open">Menu</button>
  <div :class="open ? 'active' : ''" @click.away="open = false">
    <!-- Menu items -->
  </div>
</nav>
```

### 2. **Contact Form** (contact.html)
- Real-time form state management
- Service selection tracking
- Inquiry type radio buttons with reactive styling
- Form validation

```html
<form x-data="AlpineComponents.form({ ... })">
  <select x-model="fields.service" @change="activeService = $el.value">
  <input x-model="fields.name" @blur="validate('name', [...])">
  <!-- Validation messages shown via x-text="errors.name" -->
</form>
```

### 3. **FAQ Accordions** (contact.html & services.html)
- Smooth expand/collapse animations
- Single-item active state management
- Icon rotation on open/close
- Touch-friendly interactions

```html
<div x-data="{ activeId: null }">
  <button @click="activeId = activeId === 'faq-1' ? null : 'faq-1'">
    Question
    <i :class="activeId === 'faq-1' ? 'rotate-180' : ''"></i>
  </button>
  <div x-show="activeId === 'faq-1'" x-transition>
    Answer content
  </div>
</div>
```

### 4. **Animated Counters** (portfolio.html)
- Alpine-powered number animation
- Smooth count-up effect
- No additional dependencies needed

```html
<div x-data="{ count: 0, target: 50, init() { 
  setInterval(() => { 
    if (this.count < this.target) 
      this.count += Math.ceil(this.target / 30); 
  }, 50); 
} }" x-init="init()">
  <span x-text="count">0</span>+
</div>
```

## Alpine Component Library

All reusable components are in `static/js/alpine-components.js`:

### Available Components

#### `AlpineComponents.modal()`
```html
<div x-data="AlpineComponents.modal()">
  <button @click="toggle()">Toggle Modal</button>
  <div x-show="open" x-transition>Modal Content</div>
</div>
```

#### `AlpineComponents.accordion()`
```html
<div x-data="AlpineComponents.accordion()">
  <button @click="toggle('item-1')" :class="{ 'active': isActive('item-1') }">
    Item 1
  </button>
  <div x-show="isActive('item-1')">Content</div>
</div>
```

#### `AlpineComponents.tabs()`
```html
<div x-data="AlpineComponents.tabs('tab-1')">
  <button @click="setTab('tab-1')" :class="{ 'active': isActive('tab-1') }">Tab 1</button>
  <div x-show="isActive('tab-1')">Tab 1 Content</div>
</div>
```

#### `AlpineComponents.filter(items)`
```html
<div x-data="AlpineComponents.filter([...items])">
  <button @click="setFilter('category')" :class="{ 'active': activeFilter === 'category' }">
    Filter
  </button>
  <template x-for="item in filteredItems">
    <div x-text="item.title"></div>
  </template>
</div>
```

#### `AlpineComponents.form(fields)`
```html
<form x-data="AlpineComponents.form({ name: '', email: '' })">
  <input x-model="fields.name">
  <span x-text="errors.name" x-show="errors.name"></span>
  <button @click="isValid() && submit()">Submit</button>
</form>
```

#### `AlpineComponents.toast()`
```html
<div x-data="AlpineComponents.toast()">
  <button @click="success('Success!')">Show Toast</button>
  <template x-for="notification in notifications">
    <div x-text="notification.message"></div>
  </template>
</div>
```

## Best Practices

### 1. Use `x-cloak` for Initial Load
Already in base.html. Prevents flash of unstyled content:
```html
<style>[x-cloak] { display: none !important; }</style>
<div x-cloak x-data="...">Content</div>
```

### 2. Lazy Initialize Data
Use `x-init` for any setup:
```html
<div x-data="{ init() { /* setup */ } }" x-init="init()">
```

### 3. Debounce Search/Filter
```html
<input x-model.debounce-500ms="query">
```

### 4. Use `@click.away` for Dropdowns
```html
<div x-data="{ open: false }" @click.away="open = false">
```

### 5. Leverage `x-transition` for Smooth Animations
```html
<div x-show="open" x-transition>
  <!-- Fades in/out over 300ms by default -->
</div>
```

Customize with duration:
```html
<div x-show="open" x-transition.duration.500ms>
```

## Performance Tips

1. **Keep State Local** - Alpine excels at component-level state
2. **Don't Over-Use** - For complex apps, consider moving to a full framework
3. **Use Data Binding Wisely** - `x-model` on large lists can be slow
4. **Leverage Tailwind Transitions** - Let CSS handle animations, Alpine handles logic

## File Structure

```
static/js/
├── alpine-components.js     (Component library)
├── main.js                  (Global utilities)
└── modern-main.js           (GSAP animations)

templates/
├── base.html                (Navigation with Alpine)
├── contact.html             (Form + FAQ with Alpine)
├── services.html            (FAQ with Alpine)
├── portfolio.html           (Counters + Stats with Alpine)
└── ...
```

## Migration Guide (If Adding More Features)

### Converting from jQuery to Alpine

**Before (jQuery):**
```javascript
$('.filter-btn').click(function() {
  $(this).addClass('active');
  var category = $(this).data('category');
  filterItems(category);
});
```

**After (Alpine):**
```html
<button 
  @click="activeFilter = 'category'"
  :class="activeFilter === 'category' ? 'bg-primary text-white' : ''"
>
  Filter
</button>
```

### Converting from CSS to Alpine

**Before (CSS-only):**
```html
<div class="accordion">
  <button class="toggle">Item</button>
  <div class="content">Content</div>
</div>
```

```css
.accordion .content { display: none; }
.accordion .toggle.active ~ .content { display: block; }
```

**After (Alpine + Tailwind):**
```html
<div x-data="{ open: false }">
  <button @click="open = !open">Item</button>
  <div x-show="open" x-transition>Content</div>
</div>
```

## CDN Version
Currently using Alpine.js 3.13.3 from unpkg CDN:
```html
<script src="https://unpkg.com/alpinejs@3.13.3/dist/cdn.min.js" defer></script>
```

## Debugging

### Enable Alpine Devtools
Alpine works great with Vue DevTools browser extension for debugging component state.

### Console Logging
```html
<div x-data="{ count: 0 }" @change="console.log('Count:', count)">
```

### Inspect State
In browser console:
```javascript
Alpine.$store('storeName') // if using Alpine stores
```

## Next Steps

To expand Alpine usage:

1. **Add More Components** - Use `AlpineComponents.*` for new interactive features
2. **Create Global Store** - Use Alpine.store() for app-wide state
3. **Add Validation Library** - Pair with Zod or Yup for form validation
4. **Create Custom Directives** - Extend Alpine for project-specific needs

## Resources

- [Alpine.js Official Docs](https://alpinejs.dev)
- [Tailwind + Alpine Integration](https://tailwindcss.com)
- [Component Examples](https://alpinejs.dev/examples)
- [Interactive API Reference](https://alpinejs.dev/essentials/alpine-magics)

---

**Your website now has:**
✅ Lightweight interactivity (15kb Alpine.js)
✅ Smooth transitions and animations (Tailwind + GSAP)
✅ Reusable component library
✅ Zero build step required
✅ Production-ready performance

**Total JS Overhead:** ~40kb (Alpine + GSAP)
**Award-Worthy Speed:** Optimized for core web vitals

UX Improvement Plan - Thuwala Co.

Overview
- Goal: transform the site into a modern, accessible, performant, and polished web experience.
- Approach: iterative phases: design system, homepage polish, components, accessibility, performance/image pipeline, admin UX, testing.

Phase details
1. Design system & tokens (complete)
   - Centralize colors, spacing, type scale, motion tokens.
   - Implemented in `static/css/style.css` and `components.css`.

2. Homepage revamp (in progress)
   - Polished hero, fluid layout, responsive images, micro-interactions.
   - Changes in `templates/index.html`, `static/css/*`, `static/js/*`.

3. Components library (in progress)
   - `static/css/components.css` contains primitives for cards, buttons, inputs, modals, toasts.
   - Consider extracting into a build step for large projects.

4. Accessibility improvements (in progress)
   - Skip link, ARIA, modal focus management, prefers-reduced-motion support added.

5. Performance & image pipeline (next)
   - Add WebP fallbacks, picture/picture macro implemented in `templates/_components.html`.
   - Recommend generating WebP variants using `cwebp` or Pillow.
   - Suggest automating via a small Python script or build pipeline.

6. Polished interactions (complete)
   - `static/js/ui-enhancements.js` for smooth scroll, page fade; CSS motion tokens for consistent timing.

7. Admin UX improvements (started)
   - `static/js/admin-enhancements.js` added for validation and submit states.
   - Next: refine admin templates, style forms, and add inline validation messages.

8. Testing & QA (in progress)
   - `scripts/smoke_test.py` added for basic page availability checks.
   - Recommend Playwright for E2E and Lighthouse for performance checks.

Next recommended tasks (short-term)
- Generate WebP assets and store alongside originals (or add build step to generate on deploy).
- Replace remaining hard-coded images with `responsive_picture` macro.
- Add visual regression tests (Playwright + Percy) and a CI job.
- Improve admin forms (server-side validation echoes) and add unit tests for backend routes.

How to generate WebP locally (examples)
- Using `cwebp` commandline tool:
  cwebp -q 80 static/images/hero/hero-default.jpg -o static/images/hero/hero-default.webp

- Using Python Pillow:
  from PIL import Image
  img = Image.open('static/images/hero/hero-default.jpg')
  img.save('static/images/hero/hero-default.webp', 'WEBP', quality=80)

If you want, I can:
- (A) Generate WebP files here (I can create a Pillow script and run it if you give permission to run Python in workspace).
- (B) Continue with the full homepage redesign (layout + micro-interactions + visual polish).
- (C) Create Playwright + Lighthouse checks and a CI workflow.

Pick next action or I can proceed with (A) and generate WebP assets for existing images.

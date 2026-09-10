# 1. Monograph & Broadside Design System

Date: 2026-09-06
Status: Accepted

## Context
Personal websites frequently alternate between overly generic CMS themes or modern corporate flat designs that feel sterile. redbrogdon.dev houses a unique mixture of long-form technical essays, software architecture deep dives, media appearances, and published poetry. 

The site requires an aesthetic that conveys literary gravitas, craftsmanship, and legibility while maintaining rock-solid responsive engineering and dark mode ergonomics.

## Decision
We adopted the **Monograph & Broadside** design system:
1. **Typography**: Paired classical renaissance serif *EB Garamond* for all reading prose and titles with technical monospaced *JetBrains Mono* for code, navigation, labels, and timestamps.
2. **Layout Structure**: A two-column broadside layout inspired by traditional broadsheet pamphlets. A fixed/sticky 280px sidebar anchors identity and navigation on the left, while reading content flows through a centered 708px column (`max-width: 1060px; margin: 0 auto; gap: 4.5rem;`).
3. **Dual Palette**:
   - **Light Mode**: Warm unbleached paper background (`#fbf9f4`), dark charcoal ink (`#1c1917`), and terracotta/crimson accents (`#991b1b`).
   - **Dark Mode**: Deep charcoal night background (`#151413`), warm ivory ink (`#ede7dc`), and warm amber accents (`#d99b43`).
4. **Layout Stabilization**: To eliminate the horizontal layout shift (jitter) caused by the appearance of vertical scrollbars between short pages (Home, Poetry) and long pages (Blog, Media), `scrollbar-gutter: stable;` is enforced on the `html` element.
5. **Self-Hosting**: All webfonts, icons, and stylesheets are locally hosted under `public/static/` with long-lived immutable cache headers in `firebase.json`—zero reliance on third-party CDNs.

## Consequences
- **Positive**: Cohesive, distinguished identity across poetry and deep technical essays; zero external network dependencies; instant font rendering without third-party privacy concerns or layout shifts.
- **Negative**: All font subsets and icon files must be maintained locally in the repository.

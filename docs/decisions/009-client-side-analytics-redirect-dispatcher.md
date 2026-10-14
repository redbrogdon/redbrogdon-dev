# 009: Client-Side Analytics Redirect Dispatcher

* **Date:** 2026-10-14
* **Status:** Accepted

---

## Context

`redbrogdon.dev` is a pure static site deployed via Firebase Hosting with zero server-side application runtimes. A mechanism was required to provide branded shortlinks (e.g., `https://redbrogdon.dev/go/<slug>`) that forward visitors to external resources (such as GitHub Gists, presentations, or project repositories) while tracking engagement in Google Analytics (GA4 property `G-K7H22E9BGS`).

Standard HTTP redirects configured in `firebase.json` (`redirects` block) return HTTP 301 or 302 responses directly from the CDN edge. While fast, server-side HTTP redirects terminate before downloading the document body or executing JavaScript. Consequently, client-side tracking tags like `gtag.js` never run, making it impossible to measure link clicks in GA4 using native hosting redirects alone.

---

## Decision

1. **Wildcard Rewrite in Firebase Hosting**
   A wildcard rewrite rule is added to `firebase.json`:
   ```json
   "rewrites": [
     {
       "source": "/go/**",
       "destination": "/go/index.html"
     }
   ]
   ```
   All requests under the `/go/` path are routed to a single static dispatcher page (`public/go/index.html`) without altering the browser's address bar.

2. **Centralized Shortlink Registry**
   `public/go/index.html` maintains a centralized dictionary mapping lowercase URL slugs to target URLs (e.g., `graphicizer-prompt -> https://gist.github.com/...`). Adding a new shortlink requires only adding a single entry to this dictionary.

3. **Client-Side Telemetry & Beacon Redirection**
   When a valid slug is matched:
   - GA4 records the page view for `/go/<slug>` automatically.
   - A dedicated `share_link_redirect` event is dispatched containing `slug` and `destination_url`.
   - The event specifies `transport_type: 'beacon'` and hooks `event_callback` to execute `window.location.replace(destination)`.
   - A safety timeout of 300ms triggers the redirect if network latency or ad blockers prevent the `event_callback` from firing.

4. **Standard 404 Fallback for Unknown Slugs**
   If an unrecognized slug is visited (or `/go/` is visited directly without a slug), the dispatcher immediately executes `window.location.replace('/404.html')`. This preserves the site's canonical 404 error experience rather than maintaining a bespoke error interface inside the dispatcher.

5. **Search Engine & Cache Controls**
   - The dispatcher includes `<meta name="robots" content="noindex, nofollow">` to prevent search crawlers from indexing redirect endpoints.
   - HTML files retain `Cache-Control: no-cache` per existing site hosting rules, ensuring updates to the redirect dictionary take effect immediately without stale edge caches.

---

## Consequences

* **Positive:**
  - Full analytics tracking for inbound shortlinks directly inside the GA4 dashboard.
  - Zero server-side compute, Cloud Functions, or external URL shortening services required.
  - Adding or modifying shortlinks is declarative and committed directly to version control.
  - Sub-300ms redirect time with fallback links and zero back-button pollution (`window.location.replace`).
* **Negative:**
  - Introduces a minor 200–300ms delay compared to raw HTTP 301 edge redirects while analytics beacons are dispatched.
  - Requires JavaScript execution in the client browser.

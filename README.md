# The Perimeter — perimeterdesk.com

Static site for The Perimeter, a weekly markets research publication with three desks:
Energy, Metals, and Pre-IPO. Built to run on GitHub Pages with no backend.

> **Deploying for the first time?** Follow `SETUP.md` — it covers GitHub, DNS, and the
> GoHighLevel forms end to end, in order. This README is the day-to-day reference.

## Structure

```
index.html              home — hero, this week's numbers, desks, issues, signup
energy.html             Energy Desk landing + signup
metals.html             Metals Desk landing + signup
preipo.html             Pre-IPO Desk landing + signup
about.html              editorial policy — what we publish and don't
disclosure.html         full disclosure, risk, and subscriber data policy
issues/                 generated issue pages
issues-src/             markdown source for each issue
assets/style.css        all styling
assets/logo.svg         logo mark
build.py                regenerates all HTML from the markdown sources
CNAME                   custom domain for GitHub Pages
```

## Publishing a new issue

1. Drop the markdown into `issues-src/` named `YYYY-MM-DD-desk.md`
   (desk is `energy`, `metals`, or `preipo`). Keep the same 8-line masthead block
   at the top as the existing files — the builder strips it.
2. Add the issue to the `ISSUES` list near the top of `build.py`, newest first.
3. Run `python3 build.py`.
4. Commit and push. Pages redeploys automatically.

Requires Python 3 and the markdown package: `pip install markdown`

## Deploying to GitHub Pages

1. Create a repository and push this folder to the `main` branch.
2. Settings → Pages → Source: "Deploy from a branch", branch `main`, folder `/ (root)`.
3. Settings → Pages → Custom domain: enter `perimeterdesk.com`.
4. Tick "Enforce HTTPS" once the certificate is issued (can take up to an hour).

### DNS records at your registrar

For the apex domain, four A records pointing at GitHub Pages:

```
A   @   185.199.108.153
A   @   185.199.109.153
A   @   185.199.110.153
A   @   185.199.111.153
```

And one for the www subdomain:

```
CNAME   www   webmasterihi22-sudo.github.io
```

Verify these against GitHub's current documentation before entering them — the IPs
have changed historically. Search "GitHub Pages apex domain IP addresses".

Point the typo domains you registered at the same place with a 301 redirect at the
registrar, not here.

## Wiring the signup form to GoHighLevel

The form markup is native so it matches the design, but it has to submit somewhere.
Two options:

**Option A — form endpoint (keeps the design).** In `build.py`, set:

```python
GHL_FORM_ID = "your-actual-form-id"
```

Then rebuild. Get the form ID from GoHighLevel: Sites → Forms → open your form →
Integrate → the embed code contains the ID. Confirm the current submit endpoint in
GHL's docs; if it differs from the value in `GHL_FORM_ACTION`, update that too.
Test one live submission and confirm the contact lands in GHL with the tags you expect.

**Option B — iframe embed (guaranteed to work, less control).** Replace the
`<form>` block inside the `signup()` function in `build.py` with the iframe snippet
GHL gives you. You lose the styling but you inherit GHL's validation, spam handling,
and consent capture.

Start with B if you want to launch today, move to A once it's proven.

### Field mapping

The form posts these names — map them in GHL:

| Field | Purpose |
|---|---|
| `email` | required |
| `phone` | only populated if SMS box is ticked |
| `desk` | which desk (desk pages only) |
| `desk_energy` / `desk_metals` / `desk_preipo` | multi-select on the home page |
| `consent_email` | required checkbox — this is your email consent record |
| `consent_sms` | optional checkbox — this is your TCPA written consent record |

**Store `consent_sms` with a timestamp and the IP address.** That record is the
evidence you rely on if an SMS consent complaint is ever made. GHL can capture both;
make sure the fields exist before you send traffic.

Do not text anyone whose `consent_sms` is unchecked, and do not treat the email
checkbox as covering SMS. They are separate consents by design.

## Before launch

- [ ] Replace `GHL_FORM_ID` and test a real submission end to end
- [ ] Confirm consent timestamp + IP are being stored
- [ ] Set up a sending subdomain (`mail.perimeterdesk.com`) with SPF, DKIM, DMARC
- [ ] Keep this sending domain separate from any other publication you run
- [ ] 10DLC campaign registration before any SMS goes out
- [ ] Have counsel review `disclosure.html` and `about.html`

---

## Legal pages — placeholders you must fill

Search the repo for these strings and replace every occurrence before launch:

All placeholders are filled:

| Field | Value |
|---|---|
| Legal entity | Darkflow.AI Inc. |
| Business address | 640 Fulton Street, Suite 9, Farmingdale, NY 11735 |
| Venue county | Nassau County, New York |
| Contact mailbox | support@perimeterdesk.com (single address across all pages) |
| GitHub account | webmasterihi22-sudo |

**Verify the entity name against your certificate of incorporation** before launch. It is
rendered as `Darkflow.AI Inc.` — if the registered name differs in punctuation or suffix,
correct it in `build.py` and rebuild. The name in your terms of service should match the
entity that can actually be sued or sue.

`support@perimeterdesk.com` must exist and be monitored before launch. It is the published
contact for privacy requests, legal notices, and SMS support, and privacy statutes carry
response deadlines — 45 days in most states.

## The data-sharing decision

`privacy.html` currently states, as a commitment to readers, that subscriber records are
**not** appended, enriched, scored, or moved into any lead-generation or client-facing data
product operated by Darkflow.AI or an affiliate.

That is the strict position, and it is the one that makes the publication defensible. It is
also a promise that binds you. A privacy policy that says one thing while the business does
another is an FTC Act Section 5 deceptive practice claim, and state attorneys general bring
these.

**If Darkflow does intend to use subscriber data across the business, this policy must be
rewritten before launch, not after.** That version has to disclose the sharing plainly, and it
pulls in obligations the current version avoids:

- Under California's CPRA, moving personal information to an affiliate for its own commercial
  use is likely "sharing" or "selling" — which requires a "Do Not Sell or Share My Personal
  Information" link in the site footer and an opt-out mechanism
- Several state privacy laws require opt-in consent for targeted advertising uses
- The disclosure has to appear at the point of collection, not just in the policy

Pick the position deliberately. Do not launch with the strict language as a placeholder and
sort the practice out later — the language is what you are held to.

## Cookie note

The site loads typefaces from Google Fonts, which transmits reader IP addresses to Google.
`cookies.html` discloses this. Self-hosting the font files removes the disclosure and the
issue: download the Newsreader and IBM Plex Mono woff2 files into `assets/fonts/`, replace the
`@import` at the top of `assets/style.css` with local `@font-face` rules, and delete the "note
on fonts" section from `cookies.html`.

## These are drafts, not legal advice

I am not a lawyer and these documents have not been reviewed by one. They are a solid starting
draft that covers the standard ground, but a securities and privacy attorney should review all
five legal pages before launch — particularly `disclosure.html` and `terms.html`, where the
publisher-exemption posture is doing real work for you.

---

## The homepage slider

Three slides, defined inline in `build.py` in the `index` block. Slide 1 is an image;
slides 2 and 3 are typographic and need no artwork.

- Autoplays every 7 seconds, pauses on hover and on keyboard focus
- Arrow keys move between slides when the slider has focus
- Respects `prefers-reduced-motion` — autoplay is disabled entirely for those users
- The gold SUBSCRIBE button baked into the slide-1 artwork is covered by a transparent
  link (`.hotspot`) that jumps to `#subscribe` on the same page. Its position is set in
  `assets/style.css` under `.hotspot` as percentages — if you swap the artwork, adjust
  `left`, `top`, `width`, `height` to sit over the new button.

### Adding a slide

Copy one of the `<div class="slide">` blocks in `build.py`, add a matching dot button,
update the `aria-label` counts, and rebuild. Images go in `assets/img/` — export at
1600x900 and save both `.webp` and `.jpg`.

### Image sizes

The uploaded artwork was 1672x941 at 2.2 MB. It is now 1600x900, 190 KB as WebP with a
275 KB JPEG fallback. Keep new slides under about 250 KB or the homepage gets slow on
mobile.

---

## The report gate

Issue pages show the headline, the dateline, and the "week in one line" summary, then
stop. Everything after the first horizontal rule is behind a registration card.

The split is automatic: `build.py` cuts the converted markdown at the first `<hr />`,
which corresponds to the `---` after the opening summary in each issue's markdown. Keep
that rule in place when writing new issues, or the split point moves.

### Read this before you rely on it

**This is a soft gate, not protection.** GitHub Pages serves static files with no server,
so the full report is present in the page source. Anyone who opens View Source, uses
Reader Mode, or disables JavaScript reads the whole thing without registering.

That is the correct trade for lead capture — friction converts casual readers, and search
engines index the full text so the reports can still rank. It is the wrong trade if the
content genuinely must be restricted. For that you need a server: GoHighLevel's membership
feature, a paid tier on beehiiv or Substack, or a service like Memberstack or Outseta
layered over this site.

### How unlocking works

- Submitting the registration form sets `localStorage.pd_reader = '1'` and the reader sees
  full reports from then on, on that device and browser
- "Unlock on this device" does the same without a submission, for readers who already
  subscribed elsewhere. It is an honesty check, not authentication
- Clearing site data re-locks it
- The flag is disclosed in `cookies.html` — if you change the key name or add anything
  else to storage, update that page in the same commit

### SEO

Each issue page carries `NewsArticle` JSON-LD with `isAccessibleForFree: False` and a
`hasPart` block pointing at `.gate-body`. That is Google's documented way to declare gated
content so that serving the full text to crawlers is not treated as cloaking. Do not
remove it while the gate is on.

### Turning the gate off

Delete the `.gate-card` block and change `.gate-body { display: none }` to `display: block`
in `assets/style.css`. Also remove the JSON-LD, or flip `isAccessibleForFree` to `True`.

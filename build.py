#!/usr/bin/env python3
"""Static site builder for The Perimeter. Run: python3 build.py"""

import os
import re
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "issues-src")

GHL_FORM_ACTION = "https://backend.leadconnectorhq.com/forms/submit"
GHL_FORM_ID = "REPLACE_WITH_YOUR_GHL_FORM_ID"

MARK = """<svg width="30" height="30" viewBox="0 0 48 48" aria-hidden="true">
<g fill="none" stroke="#16191C" stroke-width="2.4" stroke-linecap="square">
<path d="M2,16 L2,2 L16,2"/><path d="M32,2 L46,2 L46,16"/>
<path d="M46,32 L46,46 L32,46"/><path d="M16,46 L2,46 L2,32"/></g></svg>"""

DESKS = [
    ("energy", "Energy Desk", "Crude, natural gas, rig counts, and the majors.",
     "Weekly coverage of oil and gas markets: benchmark pricing, EIA inventories, Baker Hughes drilling activity, and the equities that track them."),
    ("metals", "Metals Desk", "Gold, silver, and the real-yield mechanism that moves them.",
     "Weekly coverage of precious metals: spot pricing, the gold-silver ratio, central bank demand, industrial consumption, and Fed policy."),
    ("preipo", "Pre-IPO Desk", "Pricings, filings, lock-ups, and the private-market pipeline.",
     "Weekly coverage of new issues and private markets: what priced, what filed, what the terms say, and which lock-ups are coming due."),
]

ISSUES = [
    ("2026-07-27", "energy", "Crude's biggest week of the year, and an inventory build that argues against it"),
    ("2026-07-27", "metals", "Rates beat geopolitics, until Friday's physical bid"),
    ("2026-07-27", "preipo", "One pricing, a 44% debut, and a pipeline that finally looks balanced"),
]

GATE_JS = """<script>
(function () {
  var art = document.getElementById('report');
  if (!art) return;
  var KEY = 'pd_reader';

  function open_() {
    art.classList.add('is-open');
    var fade = art.querySelector('.gate-fade');
    if (fade) fade.remove();
  }
  function remember() {
    try { localStorage.setItem(KEY, '1'); } catch (e) {}
  }

  try { if (localStorage.getItem(KEY) === '1') open_(); } catch (e) {}

  if (!art.classList.contains('is-open')) {
    var teaser = art.querySelector('.gate-teaser');
    if (teaser) {
      var fade = document.createElement('div');
      fade.className = 'gate-fade';
      teaser.insertAdjacentElement('afterend', fade);
    }
  }

  var form = art.querySelector('form[data-gate]');
  if (form) {
    form.addEventListener('submit', function () { remember(); });
  }
  var back = art.querySelector('[data-unlock]');
  if (back) {
    back.addEventListener('click', function () { remember(); open_(); });
  }
})();
</script>"""

SLIDER_JS = """<script>
(function () {
  var root = document.querySelector('.slider');
  if (!root) return;
  var slides = Array.prototype.slice.call(root.querySelectorAll('.slide'));
  var dots = Array.prototype.slice.call(root.querySelectorAll('.slider-dots button'));
  var i = 0, timer = null;
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function show(n) {
    i = (n + slides.length) % slides.length;
    slides.forEach(function (s, k) { s.classList.toggle('is-on', k === i); });
    dots.forEach(function (d, k) {
      if (k === i) { d.setAttribute('aria-current', 'true'); }
      else { d.removeAttribute('aria-current'); }
    });
  }
  function start() { if (still) return; stop(); timer = setInterval(function () { show(i + 1); }, 7000); }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  root.querySelector('[data-nav="next"]').addEventListener('click', function () { show(i + 1); start(); });
  root.querySelector('[data-nav="prev"]').addEventListener('click', function () { show(i - 1); start(); });
  dots.forEach(function (d) {
    d.addEventListener('click', function () { show(parseInt(d.dataset.go, 10)); start(); });
  });

  root.addEventListener('mouseenter', stop);
  root.addEventListener('mouseleave', start);
  root.addEventListener('focusin', stop);
  root.addEventListener('focusout', start);
  root.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { show(i + 1); start(); }
    if (e.key === 'ArrowLeft') { show(i - 1); start(); }
  });

  start();
})();
</script>"""


def head(title, desc, depth=0):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{up}assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
"""


def header(current="", depth=0):
    up = "../" * depth
    items = [("energy.html", "Energy"), ("metals.html", "Metals"),
             ("preipo.html", "Pre-IPO"), ("about.html", "About")]
    nav = "".join(
        f'<a href="{up}{h}"{" aria-current=\"page\"" if current == h else ""}>{t}</a>'
        for h, t in items)
    return f"""<div class="shell">
<header class="masthead">
<a class="brand" href="{up}index.html">{MARK}<span class="brand-name">The Perimeter</span></a>
<nav class="nav">{nav}</nav>
</header>
</div>
"""


def footer(depth=0, extra=""):
    up = "../" * depth
    return f"""<div class="shell">
<footer>
<div class="foot-grid">
<div>
<p><strong>The Perimeter</strong><br>Markets outside the index.</p>
<p>A publication of Darkflow.AI.<br>perimeterdesk.com</p>
</div>
<div>
<ul>
<li><a href="{up}energy.html">Energy Desk</a></li>
<li><a href="{up}metals.html">Metals Desk</a></li>
<li><a href="{up}preipo.html">Pre-IPO Desk</a></li>
<li><a href="{up}about.html">About</a></li>
</ul>
</div>
<div>
<ul>
<li><a href="{up}disclosure.html">Disclosure</a></li>
<li><a href="{up}privacy.html">Privacy policy</a></li>
<li><a href="{up}cookies.html">Cookie policy</a></li>
<li><a href="{up}terms.html">Terms of service</a></li>
<li><a href="{up}sms.html">SMS terms</a></li>
</ul>
</div>
</div>
<div class="legal">
<p>The Perimeter publishes market analysis for informational purposes only. Nothing here is investment
advice, and nothing here is a recommendation to buy or sell any security or commodity. The Perimeter is
not a registered investment adviser and does not provide personalized advice. Consult a licensed
financial professional before making investment decisions. See our
<a href="{up}disclosure.html">full disclosure</a>.</p>
<p>&copy; 2026 Darkflow.AI Inc. All rights reserved.</p>
</div>
</footer>
</div>
{extra}
</body>
</html>
"""


def signup(desk_key=None, heading="Get the desks in your inbox", sub=None):
    if sub is None:
        sub = ("One issue per desk per week. Data and analysis, no trade alerts. "
               "Unsubscribe from any issue.")
    if desk_key:
        boxes = f'<input type="hidden" name="desk" value="{desk_key}">'
        desk_field = ""
    else:
        boxes = ""
        desk_field = """<div class="field">
<label for="desks">Desks</label>
<div class="check"><input type="checkbox" id="d1" name="desk_energy" value="yes"><span>Energy Desk</span></div>
<div class="check"><input type="checkbox" id="d2" name="desk_metals" value="yes"><span>Metals Desk</span></div>
<div class="check"><input type="checkbox" id="d3" name="desk_preipo" value="yes"><span>Pre-IPO Desk</span></div>
</div>"""
    return f"""<div class="signup">
<h2>{heading}</h2>
<p class="lede">{sub}</p>
<form action="{GHL_FORM_ACTION}" method="POST">
<input type="hidden" name="formId" value="{GHL_FORM_ID}">
{boxes}
<div class="field">
<label for="email">Email address</label>
<input type="email" id="email" name="email" placeholder="name@company.com" required>
</div>
{desk_field}
<div class="checks">
<div class="check">
<input type="checkbox" id="consent_email" name="consent_email" value="yes" required>
<span><strong>Send me the newsletter.</strong> I agree to receive weekly issues from The Perimeter
at the address above.</span>
</div>
<div class="check">
<input type="checkbox" id="consent_sms" name="consent_sms" value="yes">
<span><strong>Text me too</strong> (optional). I agree to receive recurring marketing text messages
from The Perimeter at the number I provide. Consent is not a condition of purchase. Message and data
rates may apply. Message frequency varies. Reply STOP to cancel, HELP for help.</span>
</div>
<div class="field">
<label for="phone">Mobile number (only if you checked the box above)</label>
<input type="tel" id="phone" name="phone" placeholder="+1 555 555 5555">
</div>
</div>
<button type="submit">Subscribe</button>
<p class="fineprint">We do not sell or rent subscriber data, and subscriber records are not used as
sales leads for any other business.</p>
</form>
</div>"""


def issue_list(filter_desk=None):
    rows = []
    for date, desk, title in ISSUES:
        if filter_desk and desk != filter_desk:
            continue
        name = dict((d[0], d[1]) for d in DESKS)[desk]
        pretty = "July 27, 2026"
        rows.append(f"""<li><a href="issues/{date}-{desk}.html">
<span class="issue-date">{pretty}</span>
<span class="issue-title">{title}</span>
<span class="issue-desk">{name}</span></a></li>""")
    return '<ul class="issues">' + "".join(rows) + "</ul>"


# ---------------- index ----------------

desk_cards = "".join(
    f"""<a class="desk" href="{k}.html">
<span class="desk-tag">{n}</span>
<h3>{tag}</h3>
<p>{blurb}</p>
<span class="desk-go">Read the desk &rarr;</span></a>"""
    for k, n, tag, blurb in DESKS)

index = head("The Perimeter — markets outside the index",
             "Weekly research on energy, precious metals, and pre-IPO markets. Three desks, one issue each per week.")
index += header("index.html")
index += f"""<div class="shell">

<div class="slider" role="region" aria-roledescription="carousel" aria-label="Featured">
<div class="slides">

<div class="slide is-on" role="group" aria-roledescription="slide" aria-label="1 of 3: Market intelligence">
<picture>
<source srcset="assets/img/slide-market-intelligence.webp" type="image/webp">
<img src="assets/img/slide-market-intelligence.jpg" width="1600" height="878"
alt="Market intelligence: oil and gas, gold and silver, and pre-IPO coverage, every Monday." fetchpriority="high">
</picture>
<a class="hotspot" href="#subscribe">Subscribe</a>
</div>

<div class="slide" role="group" aria-roledescription="slide" aria-label="2 of 3: This week">
<div class="slide-type">
<p class="eyebrow">Week of July 20&ndash;24</p>
<h2>Brent broke $100, then gave a third of it back.</h2>
<p>The rally was a risk premium, not a shortage &mdash; inventories built while prices ran.
The Energy Desk has the rig counts and the inventory math.</p>
<a class="slide-cta" href="energy.html">Read the Energy Desk</a>
</div>
</div>

<div class="slide" role="group" aria-roledescription="slide" aria-label="3 of 3: How we publish">
<div class="slide-type">
<p class="eyebrow">How we publish</p>
<h2>Numbers, sourced. No alerts, no picks.</h2>
<p>Every issue is built from primary data &mdash; exchange settlements, EIA and Baker Hughes
releases, SEC filings. We take no payment from any company we cover.</p>
<a class="slide-cta" href="about.html">What we publish</a>
</div>
</div>

</div>
<div class="slider-dots">
<button type="button" data-go="0" aria-current="true" aria-label="Show slide 1"></button>
<button type="button" data-go="1" aria-label="Show slide 2"></button>
<button type="button" data-go="2" aria-label="Show slide 3"></button>
</div>
<div class="slider-nav">
<button type="button" data-nav="prev" aria-label="Previous slide">&larr;</button>
<button type="button" data-nav="next" aria-label="Next slide">&rarr;</button>
</div>
</div>

<div class="perimeter">
<span class="c-bl"></span><span class="c-br"></span><span class="dot-out"></span>
<h1>Markets outside the index.</h1>
<p class="lede">Three desks covering the exposures a standard portfolio leaves out — energy,
precious metals, and private markets. One issue each, every Monday, built from the week's
primary data rather than the week's narrative.</p>

<div class="strip">
<div class="stat">
<span class="stat-label">Brent, week</span>
<span class="stat-fig up">+12%</span>
<span class="stat-note">Broke $100, then gave back 4% on Friday</span>
</div>
<div class="stat">
<span class="stat-label">Gold / silver ratio</span>
<span class="stat-fig">69.5</span>
<span class="stat-note">Compressed from 70.72 as silver outran gold</span>
</div>
<div class="stat">
<span class="stat-label">IPOs priced</span>
<span class="stat-fig">1</span>
<span class="stat-note">Scribe Therapeutics closed 44% above offer</span>
</div>
</div>
</div>

<section>
<p class="eyebrow">The desks</p>
<div class="desks">{desk_cards}</div>
</section>

<section>
<p class="eyebrow">Latest issues</p>
<h2>Week of July 20&ndash;24, 2026</h2>
{issue_list()}
</section>

<section id="subscribe">
{signup()}
</section>
</div>
"""
index += footer(extra=SLIDER_JS)

# ---------------- desk pages ----------------

pages = {"index.html": index}

for k, n, tag, blurb in DESKS:
    p = head(f"{n} — The Perimeter", blurb)
    p += header(f"{k}.html")
    p += f"""<div class="shell">
<div class="perimeter">
<span class="c-bl"></span><span class="c-br"></span><span class="dot-out"></span>
<p class="eyebrow">{n}</p>
<h1>{tag}</h1>
<p class="lede">{blurb}</p>
</div>

<section>
<p class="eyebrow">Issues</p>
{issue_list(k)}
</section>

<section>
{signup(desk_key=k, heading=f"Subscribe to the {n}", sub="One issue a week, Monday morning. Data and analysis, no trade alerts.")}
</section>
</div>
"""
    p += footer()
    pages[f"{k}.html"] = p

# ---------------- about ----------------

about = head("About — The Perimeter", "What The Perimeter publishes, how it is funded, and what it is not.")
about += header("about.html")
about += """<div class="shell">
<div class="issue-head">
<p class="eyebrow">About</p>
<h1>What this publication is, and what it isn't.</h1>
</div>
<div class="prose">
<p>The Perimeter publishes three weekly research letters covering markets that sit outside a standard
index portfolio: energy, precious metals, and private and newly public companies.</p>

<p>Each issue is built from primary sources — exchange settlement data, EIA and Baker Hughes releases,
SEC filings, central bank disclosures, and industry surveys. Where an issue relies on reporting rather
than a primary document, the source is named in the text and listed at the end.</p>

<h2>What we publish</h2>
<p>Analysis of what happened and why, with the numbers attached. Every issue closes with the week ahead
and a short set of takeaways.</p>

<h2>What we don't publish</h2>
<p>We do not publish buy or sell recommendations, price targets, model portfolios, or trade alerts.
We do not accept payment from any company in exchange for coverage, and we do not participate in
investor-relations or promotional programs. If that ever changes for a specific piece, the compensation
and its amount will be disclosed at the top of that piece, as securities law requires.</p>

<h2>How we handle your data</h2>
<p>Subscriber records stay inside the subscription. They are not sold, rented, appended, or used as
sales leads for any other business, including affiliated companies. Email and SMS consent are collected
separately, and neither implies the other.</p>

<h2>Who publishes it</h2>
<p>The Perimeter is an independent publication. It is editorially separate from any news organization
or data business its publisher is otherwise involved with, and no reporting relationship runs in either
direction.</p>

<h2>Corrections</h2>
<p>Errors are corrected in place, with a dated correction note at the foot of the issue. If you find
one, write to us and it will be fixed.</p>
</div>
</div>
"""
about += footer()
pages["about.html"] = about

# ---------------- disclosure ----------------

disc = head("Disclosure and policy — The Perimeter", "Full disclosure, risk language, and subscriber data policy.")
disc += header("disclosure.html")
disc += """<div class="shell">
<div class="issue-head">
<p class="eyebrow">Disclosure</p>
<h1>Disclosure, risk, and data policy</h1>
</div>
<div class="prose">
<h2>Not investment advice</h2>
<p>The Perimeter is a publisher. It is not a registered investment adviser, broker-dealer, or financial
planner, and it does not provide personalized investment advice. Nothing in any issue is a
recommendation to buy, sell, or hold any security, commodity, or other instrument. Content is general
in nature, is impersonal, and does not account for any individual's objectives, circumstances, or risk
tolerance.</p>

<h2>No compensated coverage</h2>
<p>The Perimeter does not accept cash, securities, or other consideration from any issuer, promoter, or
affiliate in exchange for coverage. Should any piece ever be compensated, Section 17(b) of the
Securities Act of 1933 requires that the compensation and its amount be disclosed, and that disclosure
will appear at the top of the piece.</p>

<h2>Risk</h2>
<p>All investing involves risk, including loss of principal. Past performance does not predict future
results. Commodity and precious metals markets are volatile and can be affected by factors that are
difficult to anticipate. Newly public and pre-IPO companies carry elevated risk, including limited
operating history, incomplete disclosure, concentrated ownership, restricted liquidity, and lock-up
expirations that can affect price.</p>

<h2>Accuracy</h2>
<p>Issues are built from sources believed reliable at the time of publication. Market data is as of the
date noted and goes stale quickly. The Perimeter does not warrant the accuracy or completeness of any
information and has no obligation to update an issue after publication, except to correct an error.</p>

<h2>Subscriber data</h2>
<p>We collect the email address you provide, and a mobile number only if you separately opt in to text
messages. Email consent and SMS consent are captured independently; agreeing to one does not enroll you
in the other.</p>
<p>Subscriber records are not sold, rented, licensed, or transferred to third parties. They are not
appended, enriched, or used as sales leads for any other business, including businesses under common
ownership with this publication.</p>
<p>Text messages are recurring marketing messages. Message and data rates may apply, and frequency
varies. Reply STOP to any message to cancel and HELP for help. Carriers are not liable for delayed or
undelivered messages.</p>
<p>You can unsubscribe from email at any time using the link in any issue. To have your record deleted
entirely, write to us and we will remove it.</p>

<h2>Forward-looking statements</h2>
<p>Issues may contain forward-looking observations about markets, policy, or companies. These are
opinions about uncertain events, not predictions, and actual outcomes routinely differ.</p>
</div>
</div>
"""
disc += footer()
pages["disclosure.html"] = disc

# ---------------- privacy ----------------

priv = head("Privacy policy — The Perimeter", "What The Perimeter collects, why, who it is shared with, and your rights.")
priv += header("privacy.html")
priv += """<div class="shell">
<div class="issue-head">
<p class="eyebrow">Privacy policy</p>
<h1>Privacy policy</h1>
<p class="dateline">Effective July 27, 2026 &middot; Last updated July 27, 2026</p>
</div>
<div class="prose">
<p>The Perimeter is a publication of Darkflow.AI Inc. ("we," "us").
This policy explains what personal information we collect through perimeterdesk.com and our
newsletters, why we collect it, who we share it with, and what you can ask us to do with it.</p>

<h2>Information we collect</h2>
<p><strong>Information you give us.</strong> Your email address when you subscribe. Your mobile
number, but only if you separately opt in to text messages. Your desk selections. Anything you send
us by email.</p>
<p><strong>Consent records.</strong> When you tick a consent box we store which box, the date and
time, and the IP address the submission came from. We keep these because we are required to be able
to demonstrate consent, particularly for text messages.</p>
<p><strong>Email engagement.</strong> Our email platform records whether a message was delivered,
opened, and whether links were clicked. You can stop this by disabling remote image loading in your
mail client.</p>
<p><strong>Server and technical data.</strong> The site is hosted on GitHub Pages, which logs IP
addresses and request data for security and abuse prevention under its own policies. Our web fonts
are requested from Google Fonts, which receives your IP address as part of that request.</p>
<p>We do not collect financial account information, government identifiers, or investment holdings.
Do not send them to us.</p>

<h2>Why we use it</h2>
<p>To send you the issues you asked for. To operate and secure the site. To keep records proving you
consented. To answer you when you write to us. To comply with law.</p>
<p>Where a legal basis is required, we rely on your consent for marketing communications, and on our
legitimate interest in operating a publication and keeping it secure for everything else.</p>

<h2>Who we share it with</h2>
<p>We share personal information only with service providers who process it on our instructions and
are contractually restricted from using it for their own purposes. Currently these are our email and
SMS platform (GoHighLevel), our website host (GitHub Pages), and our font provider (Google Fonts).</p>
<p>We may also disclose information if compelled by law, and in connection with a sale or transfer of
the publication, in which case this policy travels with the data.</p>

<h2>What we do not do</h2>
<p><strong>We do not sell or share your personal information as those terms are defined under
California law.</strong> We do not rent, license, or trade subscriber lists.</p>
<p><strong>Subscriber records are not used as sales leads.</strong> They are not appended, enriched,
scored, or transferred into any lead-generation, prospecting, or client-facing data product operated
by Darkflow.AI or any affiliated business. The subscriber list exists to deliver the newsletter and
nothing else.</p>
<p>We do not serve behavioural advertising, and we do not run advertising or analytics trackers. See
our <a href="cookies.html">cookie policy</a>.</p>

<h2>Email and text are separate</h2>
<p>Subscribing by email does not enroll you in text messages, and consenting to text messages does not
enroll you in email. Each requires its own opt-in, and each can be withdrawn independently. See our
<a href="sms.html">SMS terms</a>.</p>

<h2>How long we keep it</h2>
<p>We keep subscriber records while you are subscribed and for 24 months afterward, so that we can
honour suppression requests and demonstrate prior consent if a complaint is made. Consent records are
kept for at least four years, which is the practical window for text-message claims. You can ask us to
delete everything sooner.</p>

<h2>Your rights</h2>
<p>Wherever you live, you can ask us to: tell you what we hold about you, correct it, delete it, give
you a copy, or stop contacting you. Residents of California, Colorado, Connecticut, Virginia, Texas,
and other states with comprehensive privacy laws have these rights by statute, along with the right not
to be discriminated against for exercising them. Residents of the EEA and UK have equivalent rights,
including the right to complain to a supervisory authority.</p>
<p>To make a request, email <a href="mailto:support@perimeterdesk.com">support@perimeterdesk.com</a>.
We will respond within 45 days. We may need to confirm your identity, which we do by verifying control
of the subscribed address or number — we will not ask you for additional identity documents.</p>
<p>You may use an authorised agent. We will ask for written proof of authorisation.</p>

<h2>Unsubscribing</h2>
<p>Every email has an unsubscribe link at the bottom, and it works immediately. For text messages,
reply STOP. Unsubscribing removes you from mailings but leaves a suppression record so that we do not
contact you again by mistake.</p>

<h2>Security</h2>
<p>The site is served over HTTPS. Subscriber data is held in our email platform under its access
controls. No system is perfectly secure, and we cannot guarantee against every form of compromise.</p>

<h2>Children</h2>
<p>This publication is for adults. We do not knowingly collect information from anyone under 18. If
you believe a minor has subscribed, write to us and we will remove the record.</p>

<h2>International readers</h2>
<p>We operate from the United States and your information is processed there. Privacy protections in
the United States differ from those in your country.</p>

<h2>Changes</h2>
<p>If we change this policy materially we will update the date above and notify subscribers by email
before the change takes effect.</p>

<h2>Contact</h2>
<p>Darkflow.AI Inc.<br>640 Fulton Street, Suite 9<br>Farmingdale, NY 11735<br>
<a href="mailto:support@perimeterdesk.com">support@perimeterdesk.com</a></p>
</div>
</div>
"""
priv += footer()
pages["privacy.html"] = priv

# ---------------- cookies ----------------

cook = head("Cookie policy — The Perimeter", "What this site stores on your device, and what it does not.")
cook += header("cookies.html")
cook += """<div class="shell">
<div class="issue-head">
<p class="eyebrow">Cookie policy</p>
<h1>Cookie policy</h1>
<p class="dateline">Effective July 27, 2026</p>
</div>
<div class="prose">
<p>Short version: this site sets no cookies, runs no analytics, and shows no advertising. It stores
one item on your device to remember that you have registered, described below.</p>

<h2>What a cookie is</h2>
<p>A small file a website stores in your browser so it can recognise you later. Similar technologies
include local storage, pixels, and tracking scripts. This policy covers all of them.</p>

<h2>What we store</h2>
<p><strong>No cookies.</strong> perimeterdesk.com is a static site with no login and no session, so it
sets no first-party cookies.</p>
<p><strong>One local storage item.</strong> When you register to read a full report, we store a single
value in your browser's local storage, named <code>pd_reader</code>, with the value <code>1</code>. Its
only purpose is to remember that you registered so the sign-up prompt does not reappear on every
report you open.</p>
<p>It contains no personal information, no identifier, and nothing that can be linked back to you. It
is not sent to us or to anyone else — it never leaves your browser. It is strictly necessary for the
feature you asked for, so it does not require consent, but you can remove it at any time by clearing
site data in your browser. Doing so simply brings the registration prompt back.</p>

<h2>What third parties may set</h2>
<p><strong>GitHub Pages (hosting).</strong> Serves the site's files. GitHub logs request data including
IP address for security and abuse prevention. It does not set advertising cookies on Pages sites.</p>
<p><strong>Google Fonts.</strong> Our typefaces are requested from Google's font servers. This does not
set a cookie, but the request does transmit your IP address to Google. If you would rather it did not,
we can self-host the fonts — see the note below.</p>
<p><strong>GoHighLevel (signup form).</strong> When you submit the subscription form, our email platform
receives the data you entered and may set a cookie in the process of handling that submission. This only
happens if you submit the form.</p>

<h2>What we do not use</h2>
<p>No Google Analytics or equivalent. No advertising or retargeting pixels. No social media trackers.
No fingerprinting. No cross-site tracking of any kind. We do not sell or share personal information, so
there is nothing for a "Do Not Sell or Share My Personal Information" link to turn off — but if you want
to make a request anyway, see our <a href="privacy.html">privacy policy</a>.</p>

<h2>Email tracking</h2>
<p>Our newsletters contain a tracking pixel that tells us whether a message was opened, and links that
record clicks. This tells us whether the publication is being read. To switch it off, disable automatic
image loading in your mail client — the issue will still arrive and still be readable.</p>

<h2>Controlling this yourself</h2>
<p>Every major browser lets you block or delete cookies in its settings, and most offer a setting to
block third-party requests. Blocking Google's font servers will change how this site looks but will not
break it.</p>

<h2>A note on fonts</h2>
<p>Loading fonts from Google transmits reader IP addresses to a third party, which some European
regulators have treated as a data transfer requiring a legal basis. Self-hosting the font files removes
that entirely and is a small change. If you are reading this and it still says we use Google Fonts, we
have not made that change yet.</p>

<h2>Changes</h2>
<p>If we add anything that stores data on your device, this page changes first, and a consent mechanism
appears alongside it.</p>

<h2>Contact</h2>
<p><a href="mailto:support@perimeterdesk.com">support@perimeterdesk.com</a></p>
</div>
</div>
"""
cook += footer()
pages["cookies.html"] = cook

# ---------------- terms ----------------

terms = head("Terms of service — The Perimeter", "The agreement governing use of perimeterdesk.com and The Perimeter newsletters.")
terms += header("terms.html")
terms += """<div class="shell">
<div class="issue-head">
<p class="eyebrow">Terms of service</p>
<h1>Terms of service</h1>
<p class="dateline">Effective July 27, 2026</p>
</div>
<div class="prose">
<p>These terms govern your use of perimeterdesk.com and The Perimeter newsletters, published by
Darkflow.AI Inc. ("we," "us"). By using the site or subscribing, you agree
to them. If you do not agree, do not use the site.</p>

<h2>1. Eligibility</h2>
<p>You must be at least 18 and capable of forming a binding contract. The publication is intended for
readers in the United States. If you access it elsewhere, you are responsible for compliance with your
local law.</p>

<h2>2. We are a publisher, not an adviser</h2>
<p>This is the most important term here. The Perimeter publishes general market commentary and
analysis. It is impersonal, is not tailored to anyone's circumstances, and is not investment advice.</p>
<p>We are not a registered investment adviser, broker-dealer, or financial planner. We do not have a
fiduciary relationship with you. Nothing we publish is an offer or solicitation to buy or sell any
security or commodity, or a recommendation that any transaction is suitable for you.</p>
<p>You are solely responsible for your investment decisions and their consequences. Consult a licensed
professional who knows your situation before acting on anything you read here. See our
<a href="disclosure.html">disclosure</a>.</p>

<h2>3. No performance promises</h2>
<p>We make no representation that any information will lead to a profit or protect against loss. Past
performance does not predict future results. All investing involves risk of loss, including total loss
of principal.</p>

<h2>4. Accuracy and timeliness</h2>
<p>Issues are prepared from sources we believe reliable at the time of publication, and market data is
as of the date stated. Information goes stale quickly and may be superseded within hours. We do not
warrant accuracy or completeness, and we have no obligation to update an issue after publication except
to correct an error.</p>

<h2>5. Subscriptions</h2>
<p>Subscription is currently free. If we introduce paid tiers, pricing, billing, renewal, and
cancellation terms will be presented at the point of purchase and will govern that transaction. We may
change, suspend, or discontinue any part of the publication at any time. We may terminate a subscription
at our discretion, including for abuse of these terms.</p>

<h2>6. Intellectual property</h2>
<p>The issues, the site, the name The Perimeter, and the associated logo are our property or licensed to
us. You may read, print, and share individual issues for personal, non-commercial use with attribution
intact. You may not republish, resell, redistribute at scale, scrape, or use our content to train
machine learning models without written permission. Quoting a reasonable excerpt with attribution and a
link is fine.</p>

<h2>7. Acceptable use</h2>
<p>Do not attempt to breach or probe the site's security, submit another person's contact details
without their permission, use the site to distribute malware, or misrepresent your affiliation with us.</p>

<h2>8. Third-party links</h2>
<p>Issues cite and link to outside sources. We do not control those sites, do not endorse them, and are
not responsible for their content or their privacy practices.</p>

<h2>9. Disclaimer of warranties</h2>
<p>The site and the newsletters are provided "as is" and "as available," without warranties of any kind,
express or implied, including merchantability, fitness for a particular purpose, non-infringement, and
uninterrupted or error-free operation. Some jurisdictions do not allow these exclusions, in which case
they apply to the fullest extent permitted.</p>

<h2>10. Limitation of liability</h2>
<p>To the fullest extent permitted by law, we are not liable for any indirect, incidental, special,
consequential, or punitive damages, or for lost profits, lost data, or trading losses, arising from your
use of the site or the newsletters — whether the claim sounds in contract, tort, or otherwise, and even
if we were advised such damages were possible. Our total aggregate liability for any claim will not
exceed the greater of the amount you paid us in the twelve months before the claim, or one hundred
United States dollars.</p>
<p>Nothing here limits liability that cannot lawfully be limited, including for fraud.</p>

<h2>11. Indemnification</h2>
<p>You agree to indemnify and hold us harmless from claims arising out of your breach of these terms or
your misuse of the site or the content.</p>

<h2>12. Governing law and disputes</h2>
<p>These terms are governed by the laws of the State of New York, without regard to its conflict of laws
rules. Any dispute will be brought exclusively in the state or federal courts located in Nassau
County, New York, and you consent to their jurisdiction.</p>

<h2>13. Changes</h2>
<p>We may revise these terms. The date above will change, and continued use after a revision means you
accept it. For material changes affecting subscribers, we will send notice by email.</p>

<h2>14. Severability and entire agreement</h2>
<p>If a provision is held unenforceable, the rest survives. These terms, together with the
<a href="privacy.html">privacy policy</a>, <a href="cookies.html">cookie policy</a>,
<a href="sms.html">SMS terms</a>, and <a href="disclosure.html">disclosure</a>, are the entire agreement
between us regarding the publication.</p>

<h2>Contact</h2>
<p>Darkflow.AI Inc.<br>640 Fulton Street, Suite 9<br>Farmingdale, NY 11735<br>
<a href="mailto:support@perimeterdesk.com">support@perimeterdesk.com</a></p>
</div>
</div>
"""
terms += footer()
pages["terms.html"] = terms

# ---------------- sms ----------------

sms = head("SMS terms — The Perimeter", "Terms and conditions for The Perimeter text message program.")
sms += header("sms.html")
sms += """<div class="shell">
<div class="issue-head">
<p class="eyebrow">SMS terms</p>
<h1>Text message terms and conditions</h1>
<p class="dateline">Effective July 27, 2026</p>
</div>
<div class="prose">
<p>These terms govern The Perimeter text message program, operated by Darkflow.AI Inc. They apply in addition to our <a href="terms.html">terms of service</a> and
<a href="privacy.html">privacy policy</a>.</p>

<h2>Program description</h2>
<p>The Perimeter sends recurring marketing and informational text messages about our Energy, Metals,
and Pre-IPO desks: new issue notifications, market notes, and occasional subscription offers. We do not
send trade alerts, price targets, or recommendations by text.</p>

<h2>How you join</h2>
<p>You join only by giving express written consent — ticking the SMS box on our signup form and
providing your mobile number, or texting a keyword we publish to our number. Consent is not a condition
of purchasing anything, and it is separate from your email subscription. Subscribing by email does not
enroll you in texts.</p>
<p>You may only enroll a number you own or are authorised to use. Do not enroll someone else.</p>

<h2>Message frequency</h2>
<p>Message frequency varies. Expect roughly two to four messages per month per desk you follow.</p>

<h2>Cost</h2>
<p>We charge nothing for the program. <strong>Message and data rates may apply.</strong> Charges depend
on your plan and your carrier. Check with your carrier if you are unsure.</p>

<h2>How to stop</h2>
<p><strong>Reply STOP to any message.</strong> You will receive one confirmation that you have been
unsubscribed, and then no further messages. STOPALL, UNSUBSCRIBE, CANCEL, END, and QUIT work the same
way. To rejoin later, sign up again — we will not re-add you on our own.</p>

<h2>How to get help</h2>
<p><strong>Reply HELP to any message</strong> for support information, or email
<a href="mailto:support@perimeterdesk.com">support@perimeterdesk.com</a>.</p>

<h2>Carriers</h2>
<p>Supported on major U.S. carriers including AT&amp;T, Verizon Wireless, T-Mobile, and others.
<strong>Carriers are not liable for delayed or undelivered messages.</strong> Delivery is subject to
transmission limits and carrier filtering, and we cannot guarantee any message arrives.</p>

<h2>Changing your number</h2>
<p>Tell us if your mobile number changes or is reassigned, so that messages intended for you do not go
to someone else. Email <a href="mailto:support@perimeterdesk.com">support@perimeterdesk.com</a>.</p>

<h2>Eligibility</h2>
<p>You must be at least 18 and the account holder or an authorised user of the number you enroll.</p>

<h2>Privacy</h2>
<p>Your mobile number is used to send you the messages you consented to. It is not sold, rented, or
shared for anyone else's marketing, and it is not used as a sales lead by Darkflow.AI or any affiliated
business. We retain your consent record — including the date, time, and IP address of your opt-in — as
proof that you agreed to receive messages. Full detail is in our
<a href="privacy.html">privacy policy</a>.</p>

<h2>Changes</h2>
<p>We may change these terms. The date above will change, and material changes will be sent to
enrolled numbers before they take effect.</p>

<h2>Contact</h2>
<p>Darkflow.AI Inc.<br>640 Fulton Street, Suite 9<br>Farmingdale, NY 11735<br>
<a href="mailto:support@perimeterdesk.com">support@perimeterdesk.com</a></p>
</div>
</div>
"""
sms += footer()
pages["sms.html"] = sms

# ---------------- write root pages ----------------

for name, html in pages.items():
    with open(os.path.join(ROOT, name), "w") as f:
        f.write(html)

# ---------------- issues ----------------

md = markdown.Markdown(extensions=["extra", "sane_lists"])

for date, desk, title in ISSUES:
    src = os.path.join(SRC, f"{date}-{desk}.md")
    if not os.path.exists(src):
        print(f"  missing source: {src}")
        continue
    raw = open(src).read()
    lines = raw.split("\n")
    body = "\n".join(lines[9:])  # drop the markdown masthead block
    md.reset()
    desk_name = dict((d[0], d[1]) for d in DESKS)[desk]
    full = md.convert(body)

    # split at the first horizontal rule: teaser is the one-line summary,
    # everything after it is gated behind registration
    if "<hr />" in full:
        teaser, gated = full.split("<hr />", 1)
    else:
        parts = full.split("</p>", 1)
        teaser, gated = (parts[0] + "</p>", parts[1]) if len(parts) > 1 else (full, "")

    p = head(f"{title} — {desk_name} — The Perimeter",
             f"{desk_name} weekly recap, week of July 20-24, 2026.", depth=1)
    p += f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"NewsArticle",
"headline":"{title}",
"datePublished":"2026-07-27",
"isAccessibleForFree":"False",
"publisher":{{"@type":"Organization","name":"The Perimeter"}},
"hasPart":{{"@type":"WebPageElement","isAccessibleForFree":"False","cssSelector":".gate-body"}}}}
</script>
"""
    p += header(f"{desk}.html", depth=1)
    p += f"""<div class="shell">
<div class="issue-head">
<p class="eyebrow">{desk_name} &middot; Weekly recap</p>
<h1>{title}</h1>
<p class="dateline">Week of July 20&ndash;24, 2026 &middot; Published Monday, July 27</p>
</div>
<article class="prose" id="report">
<div class="gate-teaser">
{teaser}
</div>

<div class="gate-card">
<p class="eyebrow">Continue reading</p>
<h2>Register to read the full report</h2>
<p>Free. One email address gets you every issue of the {desk_name}, plus access to the archive.</p>
<form action="{GHL_FORM_ACTION}" method="POST" data-gate="1">
<input type="hidden" name="formId" value="{GHL_FORM_ID}">
<input type="hidden" name="desk" value="{desk}">
<input type="hidden" name="source" value="gate:{date}-{desk}">
<div class="field">
<label for="g-email">Email address</label>
<input type="email" id="g-email" name="email" placeholder="name@company.com" required>
</div>
<div class="checks">
<div class="check">
<input type="checkbox" id="g-consent" name="consent_email" value="yes" required>
<span><strong>Send me the {desk_name}.</strong> I agree to receive weekly issues from
The Perimeter at the address above. Unsubscribe from any issue.</span>
</div>
</div>
<button type="submit">Read the full report</button>
<p class="fineprint">We do not sell or rent subscriber data, and subscriber records are not used
as sales leads for any other business.</p>
</form>
<p class="gate-meta">Already subscribed?
<button type="button" class="gate-back" data-unlock="1">Unlock on this device</button></p>
</div>

<div class="gate-body">
<hr />
{gated}
</div>
</article>
<section>
{signup(desk_key=desk, heading=f"Get the {desk_name} every Monday", sub="One issue a week. Data and analysis, no trade alerts.")}
</section>
</div>
"""
    p += footer(depth=1, extra=GATE_JS)
    with open(os.path.join(ROOT, "issues", f"{date}-{desk}.html"), "w") as f:
        f.write(p)

print("built:", len(pages), "pages +", len(ISSUES), "issues")

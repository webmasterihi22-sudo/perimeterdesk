# SETUP — perimeterdesk.com

Everything needed to get The Perimeter live, in the order it should be done.

**Reference values used throughout:**

| | |
|---|---|
| Domain | perimeterdesk.com |
| GitHub account | webmasterihi22-sudo |
| Repository | perimeterdesk |
| Entity | Darkflow.AI Inc. |
| Contact mailbox | support@perimeterdesk.com |
| Sending subdomain | mail.perimeterdesk.com |

---

# Part 1 — GitHub

## 1.1 Before you push

Entity details are confirmed against the NY certificate of incorporation and filing
receipt. No changes needed:

| | |
|---|---|
| Registered name | Darkflow.AI Inc. (capital D, lowercase f) |
| Entity type | Domestic Business Corporation, New York |
| County | Nassau |
| Service of process address | 640 Fulton Street, Suite 9, Farmingdale, NY 11735 |

The name is styled `Darkflow.AI` throughout the site to match the certificate. If you use
`DarkFlow.AI` with a capital F as a trade style elsewhere, that is fine for marketing, but
do not change it on the legal pages — those must carry the registered form.

## 1.2 Create the repository

Pick one of these three.

### Option A — Claude Code (fastest)

```
cd path/to/perimeterdesk
claude
```

Then: *"Initialize a git repo here, create a public GitHub repo called perimeterdesk under
my account, and push it to main."*

### Option B — GitHub CLI

```
cd path/to/perimeterdesk
gh auth status                # confirm you're logged in as webmasterihi22-sudo
gh repo create perimeterdesk --public --source=. --remote=origin --push
```

### Option C — Web + git

Create the repo at **github.com/new**:
- Owner: `webmasterihi22-sudo`
- Name: `perimeterdesk`
- Public
- **Do not** initialize with a README, .gitignore, or license — you already have files,
  and initializing creates a conflicting commit

Then:

```
cd path/to/perimeterdesk
git init
git add .
git commit -m "The Perimeter — initial site"
git branch -M main
git remote add origin https://github.com/webmasterihi22-sudo/perimeterdesk.git
git push -u origin main
```

If prompted for a password, GitHub no longer accepts account passwords over HTTPS. Use a
personal access token (Settings → Developer settings → Personal access tokens → Fine-grained,
with Contents: Read and write on this repo) as the password, or switch the remote to SSH.

## 1.3 Enable Pages

Repository → **Settings** → **Pages**

- Source: **Deploy from a branch**
- Branch: `main`
- Folder: `/ (root)`
- Save

Wait 1–2 minutes, then open:

```
https://webmasterihi22-sudo.github.io/perimeterdesk/
```

**Check before going further:**

- [ ] Homepage loads with the slider running
- [ ] Slider arrows, dots, and autoplay all work
- [ ] The SUBSCRIBE button on the banner jumps to the signup form
- [ ] All four nav links work
- [ ] An issue page shows only the summary, then the registration card
- [ ] Fonts render (serif headlines, mono figures) — if not, the Google Fonts request is blocked
- [ ] All five legal pages load from the footer

If images 404, confirm `.nojekyll` is present in the repo root. Jekyll ignores some paths
without it.

## 1.4 Attach the custom domain

Do this **after** DNS in Part 2 is entered and propagating.

Repository → **Settings** → **Pages** → **Custom domain**

- Enter `perimeterdesk.com`, Save
- It should auto-populate from the `CNAME` file already in the repo
- Wait for the DNS check to pass (green)
- Tick **Enforce HTTPS** — this only becomes available after the certificate issues, which
  can take up to an hour

## 1.5 Publishing changes later

```
python3 build.py          # only if you changed build.py or added an issue
git add .
git commit -m "what changed"
git push
```

Pages redeploys in about a minute. Hard-refresh to bypass cache.

---

# Part 2 — DNS

Enter all of these in one sitting. Splitting the work across days is how the MX conflict
below happens.

## 2.1 Website — GitHub Pages

| Type | Host | Value | TTL |
|---|---|---|---|
| A | @ | 185.199.108.153 | 3600 |
| A | @ | 185.199.109.153 | 3600 |
| A | @ | 185.199.110.153 | 3600 |
| A | @ | 185.199.111.153 | 3600 |
| CNAME | www | webmasterihi22-sudo.github.io | 3600 |

**Verify those four IPs against GitHub's current documentation before entering them.**
Search "GitHub Pages apex domain IP addresses". They have changed historically.

Optionally add the AAAA records GitHub lists for IPv6.

## 2.2 Mail — Microsoft 365 (already configured — do not touch)

Your mail runs on Microsoft 365 through GoDaddy. These records are live and working.
Nothing in this list affects the website. Leave every one of them alone:

| Type | Host | Purpose |
|---|---|---|
| MX | @ | perimeterdesk-com.mail.protection.outlook.com (priority 0) |
| TXT | @ | NETORGFT20969887.onmicrosoft.com — M365 domain verification |
| TXT | @ | v=spf1 include:secureserver.net -all |
| TXT | _dmarc | v=DMARC1; p=quarantine; adkim=r; aspf=r; rua=... |
| CNAME | selector1._domainkey | M365 DKIM |
| CNAME | selector2._domainkey | M365 DKIM |
| CNAME | autodiscover | Outlook client autoconfiguration |
| CNAME | email | GoDaddy webmail |
| CNAME | sip / lyncdiscover / msoid | Teams / Skype for Business |
| SRV | _sip._tls / _sipfederationtls._tcp | Teams |

## 2.3 Sending — GoHighLevel

GHL generates these per account. Copy them from **Settings → Email Services → Dedicated
Domain** after you add `mail.perimeterdesk.com`. They take this shape:

| Type | Host | Value |
|---|---|---|
| MX | mail | mxa.mailgun.org (priority 10) |
| MX | mail | mxb.mailgun.org (priority 10) |
| TXT | (key)._domainkey.mail | (DKIM value from GHL) |
| CNAME | email.mail | mailgun.org |

**All of these sit on the `mail` subdomain, not the root.** When GHL asks for a sending
domain, enter `mail.perimeterdesk.com`. If its MX lands on the root it overwrites the
Microsoft 365 MX and support@ stops receiving.

## 2.4 SPF — merge, never add

Your existing record is:

```
v=spf1 include:secureserver.net -all
```

Note the `-all`. That is a **hard fail** — anything not listed is rejected outright, not
just flagged. When you add GHL sending, edit this single record to:

```
v=spf1 include:secureserver.net include:mailgun.org -all
```

A domain may have exactly one SPF record. Adding a second breaks the one that works today
and takes Microsoft 365 mail down with it.

## 2.5 DMARC — already enforcing

Your existing record is at `p=quarantine`, not `p=none`:

```
v=DMARC1; p=quarantine; adkim=r; aspf=r; rua=mailto:dmarc_rua@onsecureserver.net;
```

This means newsletters that fail alignment go to spam rather than being delivered with a
warning. Before your first real send, verify GHL mail passes both SPF and DKIM alignment —
send a test to a Gmail address and check the message headers, or watch the DMARC aggregate
reports. Do not relax this to `p=none`; fix alignment instead.

## 2.6 Website — GitHub Pages (done)

Entered and verified on 27 July 2026:

| Type | Host | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | webmasterihi22-sudo.github.io |

The GoDaddy default `A @ Parked` record was replaced by the first of these, per GitHub's
instruction to remove any provider-set default record.

Optionally add GitHub's four AAAA records for IPv6: 2606:50c0:8000::153,
2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153

## 2.7 Typo domains

Point the misspellings you registered at the registrar with a 301 redirect to
perimeterdesk.com. Do this at the registrar, not in this repo.

---

# Part 3 — The forms

There are two forms on the site. Both post to the same GHL endpoint and both must capture
consent.

| Form | Where | Purpose |
|---|---|---|
| Subscribe | homepage `#subscribe`, all three desk pages, foot of every issue | Full signup, email + optional SMS |
| Gate | inside each issue, between summary and full report | Email only, unlocks the report |

## 3.1 Create the custom fields FIRST

Before building anything, create these in GHL under **Settings → Custom Fields**. If a
field does not exist when a submission arrives, the value is discarded silently.

| Field name | Type | Why it matters |
|---|---|---|
| `consent_email` | Checkbox / Text | Your record that they agreed to email |
| `consent_sms` | Checkbox / Text | **Your TCPA written consent record** |
| `consent_timestamp` | Date/Time | When they agreed |
| `consent_ip` | Text | Where from |
| `desk` | Text or Dropdown | energy / metals / preipo |
| `source` | Text | Which page converted them |

`consent_sms` with a timestamp and IP is the evidence you produce if a text-message
complaint is ever made. Statutory damages under the TCPA run per message. Do not launch
without it.

## 3.2 Build the form

**Sites → Forms → Builder → New Form.**

Fields:

| Field | Type | Required |
|---|---|---|
| Email | Email | Yes |
| Phone | Phone | No |
| Consent — email | Checkbox | **Yes** |
| Consent — SMS | Checkbox | No |

**Email consent checkbox label:**

> Send me the newsletter. I agree to receive weekly issues from The Perimeter at the
> address above.

**SMS consent checkbox label** — use this wording, it contains the required elements:

> Text me too (optional). I agree to receive recurring marketing text messages from The
> Perimeter at the number I provide. Consent is not a condition of purchase. Message and
> data rates may apply. Message frequency varies. Reply STOP to cancel, HELP for help.

Below the fields, add links to `/terms.html`, `/privacy.html`, and `/sms.html`. Carriers
check for these during 10DLC vetting.

In form settings, enable **capture IP address** and **capture submission timestamp**, and
map them to `consent_ip` and `consent_timestamp`.

## 3.3 Get the form ID

**Sites → Forms →** open your form **→ Integrate.** The embed code contains the ID. It
looks like a long alphanumeric string.

## 3.4 Wire it in

Open `build.py`, near the top:

```python
GHL_FORM_ACTION = "https://backend.leadconnectorhq.com/forms/submit"
GHL_FORM_ID = "REPLACE_WITH_YOUR_GHL_FORM_ID"
```

Replace the ID. Confirm the endpoint matches what GHL's current docs show — if it differs,
update `GHL_FORM_ACTION` too. Then:

```
python3 build.py
git add . && git commit -m "wire signup form to GHL" && git push
```

## 3.5 If the native form does not post

The styled form is nicer but depends on GHL's endpoint accepting a plain POST. If it does
not, switch to the iframe embed — guaranteed to work, less control over appearance.

In `build.py`, inside the `signup()` function, replace everything between `<form ...>` and
`</form>` with the iframe snippet from GHL's Integrate tab. Do the same in the gate form
block inside the issue loop. Rebuild.

Launch with the iframe if you are short on time. Move to the native form later.

## 3.6 Field mapping reference

What the site posts, for mapping in GHL:

| Posted name | Contents |
|---|---|
| `email` | Required on both forms |
| `phone` | Only populated when SMS box ticked |
| `desk` | `energy`, `metals`, or `preipo` — desk pages and gate forms |
| `desk_energy` / `desk_metals` / `desk_preipo` | `yes` — homepage multi-select |
| `consent_email` | `yes` — required |
| `consent_sms` | `yes` — optional |
| `source` | `gate:2026-07-27-energy` on gate forms |
| `formId` | Hidden, your GHL form ID |

## 3.7 Automation to build in GHL

1. **Trigger:** form submitted
2. **Condition:** `consent_email` = yes → add tag `subscriber`
3. **Condition:** `desk` = energy → tag `desk-energy` (repeat for each desk)
4. **Condition:** `consent_sms` = yes → tag `sms-consent`; if not, **do not** add the number
   to any SMS list
5. **Action:** send confirmation email
6. **Action:** stamp `consent_timestamp` and `consent_ip`

Step 4 is the one that matters. An email subscriber is not an SMS subscriber, and treating
them as one is the single most expensive mistake available here.

---

# Part 4 — Test before announcing

Submit a real signup and verify each of these:

- [ ] Contact appears in GHL within a minute
- [ ] `consent_email` recorded as yes
- [ ] `consent_timestamp` populated
- [ ] `consent_ip` populated
- [ ] `desk` correct for the page used
- [ ] Confirmation email arrives, and lands in inbox rather than spam
- [ ] Reply to the confirmation — does it reach support@perimeterdesk.com?
- [ ] Submit a second signup **without** ticking SMS — confirm no `sms-consent` tag
- [ ] Submit through a gate form — confirm the report unlocks and `source` is recorded
- [ ] Clear browser data, reload an issue — confirm the gate returns

Send a test to a Gmail address, an Outlook address, and one on a corporate domain. They
filter very differently.

---

# Part 5 — When something breaks

| Symptom | Cause |
|---|---|
| Custom domain shows "DNS check unsuccessful" | Records still propagating, or A records point somewhere else. Give it an hour |
| Site loads but has no styling | `assets/style.css` did not push, or the path broke. Check the repo file list |
| Images 404 | `.nojekyll` missing from the repo root |
| Mail to support@ bounces | GHL took MX on the root. See 2.4 |
| Newsletter lands in spam | SPF, DKIM, or DMARC failing, or the domain is not warmed. Check Google Postmaster Tools |
| Form submits but no contact appears | Wrong form ID, or the endpoint changed. Switch to the iframe embed to isolate |
| Contact appears without consent fields | Custom fields were not created before the submission. See 3.1 |
| Gate does not unlock after submit | JavaScript blocked, or local storage disabled |

---

# Order of operations

1. Verify entity name → push to GitHub → enable Pages → test on github.io
2. Create support@ mailbox
3. Enter all DNS in one pass — Pages, mailbox MX, GHL subdomain, SPF, DMARC
4. Attach custom domain, enforce HTTPS
5. Create GHL custom fields → build form → get ID → wire in → rebuild → push
6. Run the Part 4 checklist
7. Only then announce
8. 10DLC registration before any SMS

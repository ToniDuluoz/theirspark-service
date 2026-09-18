# Their Spark — delivery service (deploy guide)

This little service does the whole money + delivery cycle:

**Website → `/checkout`** (creates a Stripe checkout that carries the child's quiz
answers) → **buyer pays** → **Stripe → `/webhook`** → generates the personalised
PDF(s) with your existing generator → **emails them to the buyer** (via Resend).

No database: the answers travel inside Stripe's session metadata.

For now everything points to **toniserna.com/spark**. When theirspark.com is
fixed, migrating = change three URLs (below) and re-upload the page.

---

## What you'll create (all free)
1. **Render** account — to host this service. https://render.com
2. **Resend** account — to send the email with the PDF. https://resend.com

You already have **Stripe** (live).

---

## Step 1 — Get your 3 Stripe Price IDs (live)
Stripe Dashboard → **Product catalogue** → open each product → copy its **Price ID**
(looks like `price_1AbC...`):
- `PRICE_PROFILE` → Their Spark - Strengths Profile ($19)
- `PRICE_PACK`    → Everyday Pack ($9)
- `PRICE_PLAN`    → Nurture Plan ($29)

## Step 2 — Deploy to Render
1. Put this `theirspark-service` folder in a GitHub repo (or use Render's
   "Deploy an existing image / from a repo"). Render → **New → Web Service**.
2. Runtime: Python. Build: `pip install -r requirements.txt`.
   Start: `gunicorn app:app --timeout 120 --workers 1` (already in `render.yaml`).
3. Plan: **Free**.
4. Add the **Environment Variables** (Step 3), then Deploy.
5. When it's live you'll get a URL like `https://theirspark-service.onrender.com`.
   Test it: open `<url>/health` → should say `{"ok": true...}`.

## Step 3 — Environment variables (paste on Render → Environment)
| Key | Value |
|---|---|
| `STRIPE_SECRET_KEY` | your **live** secret key `sk_live_...` (Stripe → Developers → API keys) |
| `STRIPE_WEBHOOK_SECRET` | from Step 4 (`whsec_...`) |
| `RESEND_API_KEY` | from Resend (`re_...`) |
| `FROM_EMAIL` | e.g. `Their Spark <hello@theirspark.com>` (needs a verified domain in Resend; while testing you can use `onboarding@resend.dev`) |
| `PRICE_PROFILE` | `price_...` ($19) |
| `PRICE_PACK` | `price_...` ($9) |
| `PRICE_PLAN` | `price_...` ($29) |
| `SUCCESS_URL` | `https://toniserna.com/spark/?paid=1` |
| `CANCEL_URL` | `https://toniserna.com/spark/` |
| `ALLOW_ORIGIN` | `https://toniserna.com` |

> ⚠️ You paste your own keys directly into Render. Claude never handles secret keys.

## Step 4 — Stripe webhook
Stripe Dashboard → **Developers → Webhooks → Add endpoint**:
- Endpoint URL: `https://<your-render-url>/webhook`
- Event: **`checkout.session.completed`**
- Create it, then copy the **Signing secret** (`whsec_...`) into `STRIPE_WEBHOOK_SECRET` on Render and redeploy.

## Step 5 — Point the website at the service
In `site/index.html` (the page on toniserna.com/spark), set in `CONFIG`:
```js
CHECKOUT_API: "https://<your-render-url>",
```
Re-upload `index.html` to `toniserna.com/spark`.

## Step 6 — Test end-to-end (use test mode first!)
Best to test with **test keys** first: use `sk_test_...`, a test webhook, and the
test Price IDs; then do a checkout with card `4242 4242 4242 4242`. Confirm the
email with the PDF arrives. Then switch the env vars to live.

---

## Migrating to theirspark.com later
When theirspark.com serves correctly, just change on Render:
`SUCCESS_URL`, `CANCEL_URL` → `https://theirspark.com/...` and
`ALLOW_ORIGIN` → `https://theirspark.com`; set `CHECKOUT_API` in the page and
upload `index.html` to theirspark.com. Done.

## Notes
- Render's free tier sleeps after ~15 min idle; the first request wakes it
  (a few seconds). Stripe retries webhooks, so delivery is safe.
- The generator falls back to DejaVu fonts. To use Fraunces/Inter, drop the
  `.ttf` files in a `fonts/` folder next to `app.py` before deploying.

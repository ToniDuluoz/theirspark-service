#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Their Spark — delivery service.

One tiny web service that does the whole money+delivery cycle:

  1. POST /checkout   the website sends the child's quiz answers + parent email.
                      We create a Stripe Checkout Session (with the $19 profile
                      required and the $9 Everyday Pack / $29 Nurture Plan as
                      optional add-ons), stash the answers in the session
                      metadata, and return the Stripe checkout URL.

  2. POST /webhook    Stripe calls this after a successful payment. We read the
                      answers back from the session metadata, generate the
                      personalised PDF(s) with the existing generator, and email
                      them to the buyer via Resend.

Nothing is stored in a database: the quiz answers ride inside Stripe's own
session metadata, so a payment always carries everything we need to fulfil it.

Environment variables (set these on the host — see README):
  STRIPE_SECRET_KEY     sk_live_...   (or sk_test_... while testing)
  STRIPE_WEBHOOK_SECRET whsec_...     (from the Stripe webhook you create)
  RESEND_API_KEY        re_...        (Resend, for sending the email)
  FROM_EMAIL            e.g. "Their Spark <hello@theirspark.com>"
  PRICE_PROFILE         price_...     ($19 Strengths Profile)
  PRICE_PACK            price_...     ($9 Everyday Pack)      [optional]
  PRICE_PLAN            price_...     ($29 Nurture Plan)      [optional]
  SUCCESS_URL           where to send the buyer after paying
  CANCEL_URL            where to send the buyer if they cancel
  ALLOW_ORIGIN          the site origin allowed to call /checkout (CORS)
"""
import os, json, base64, tempfile, traceback
from flask import Flask, request, jsonify, abort, make_response
import requests
import stripe
import theirspark_generator as G

# ---- config from environment ------------------------------------------------
stripe.api_key       = os.environ.get("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET       = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
RESEND_API_KEY       = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL           = os.environ.get("FROM_EMAIL", "Their Spark <onboarding@resend.dev>")
PRICE_PROFILE        = os.environ.get("PRICE_PROFILE", "")
PRICE_PACK           = os.environ.get("PRICE_PACK", "")
PRICE_PLAN           = os.environ.get("PRICE_PLAN", "")
SUCCESS_URL          = os.environ.get("SUCCESS_URL", "https://theirspark.com/?paid=1")
CANCEL_URL           = os.environ.get("CANCEL_URL", "https://theirspark.com/")
ALLOW_ORIGIN         = os.environ.get("ALLOW_ORIGIN", "*")

app = Flask(__name__)
print("Their Spark service — fonts:", G.setup_fonts())

# ---- small helpers ----------------------------------------------------------
def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"]  = ALLOW_ORIGIN
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp

def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def _clean_answers(d):
    return {
        "name":   (d.get("name") or "").strip() or "your child",
        "age":    str(d.get("age") or ""),
        "gender": str(d.get("gender") or ""),
        "scores": d.get("scores") or {},
    }

def send_email(to_email, child, attachments):
    """attachments: list of (filename, base64_content)."""
    first = child if child and child != "your child" else "your child"
    html = f"""
      <div style="font-family:Inter,Arial,sans-serif;color:#23303A;line-height:1.6">
        <h2 style="font-family:Georgia,serif;color:#23303A">Here is {first}'s Strengths Profile ✨</h2>
        <p>Thank you — your personalised profile is attached as a PDF.</p>
        <p>Inside you'll find {first}'s signature strength, the blend that shapes
           how they think, feel &amp; connect, and simple ways to nurture it at home.</p>
        <p style="color:#6B7680;font-size:13px">Their Spark · a guidance tool for parents,
           not a diagnostic or medical assessment.</p>
      </div>"""
    payload = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": f"{first}'s Strengths Profile is ready ✨",
        "html": html,
        "attachments": [{"filename": n, "content": c} for n, c in attachments],
    }
    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        json=payload, timeout=30,
    )
    print("Resend status", r.status_code, r.text[:300])
    r.raise_for_status()

# ---- routes -----------------------------------------------------------------
@app.get("/health")
def health():
    return jsonify(ok=True, service="theirspark", fonts=bool(PRICE_PROFILE))

@app.route("/checkout", methods=["POST", "OPTIONS"])
def checkout():
    if request.method == "OPTIONS":
        return _cors(make_response("", 204))
    data = request.get_json(force=True, silent=True) or {}
    ans = _clean_answers(data)
    email = (data.get("email") or "").strip()

    metadata = {
        "child":  ans["name"][:100],
        "age":    ans["age"][:20],
        "gender": ans["gender"][:20],
        "scores": json.dumps(ans["scores"])[:490],
    }
    line_items = [{"price": PRICE_PROFILE, "quantity": 1}]
    optional_items = []
    for pid in (PRICE_PACK, PRICE_PLAN):
        if pid:
            optional_items.append({"price": pid, "quantity": 1})

    kwargs = dict(
        mode="payment",
        line_items=line_items,
        metadata=metadata,
        payment_intent_data={"metadata": metadata},
        success_url=SUCCESS_URL,
        cancel_url=CANCEL_URL,
        allow_promotion_codes=True,
    )
    if email:
        kwargs["customer_email"] = email
    if optional_items:
        kwargs["optional_items"] = optional_items

    try:
        session = stripe.checkout.Session.create(**kwargs)
    except TypeError:
        # older Stripe lib without optional_items support -> retry without extras
        kwargs.pop("optional_items", None)
        session = stripe.checkout.Session.create(**kwargs)
    return _cors(jsonify(url=session.url))

@app.post("/webhook")
def webhook():
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except Exception as e:
        print("Webhook signature error:", e)
        abort(400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        try:
            _fulfil(session)
        except Exception:
            traceback.print_exc()
            # Return 200 anyway so Stripe doesn't hammer retries; we log the error.
    return "", 200

def _fulfil(session):
    email = ((session.get("customer_details") or {}).get("email")
             or session.get("customer_email") or "")
    meta = session.get("metadata") or {}
    ans = {
        "name":   meta.get("child", "") or "your child",
        "age":    meta.get("age", ""),
        "gender": meta.get("gender", ""),
        "scores": json.loads(meta.get("scores") or "{}"),
    }
    # Did they add the Everyday Pack?
    bought_pack = False
    try:
        items = stripe.checkout.Session.list_line_items(session["id"], limit=20)
        for it in items.get("data", []):
            price = (it.get("price") or {}).get("id")
            if PRICE_PACK and price == PRICE_PACK:
                bought_pack = True
    except Exception:
        traceback.print_exc()

    outdir = tempfile.mkdtemp()
    attachments = []
    prof = G.generate(ans, out_dir=outdir)
    attachments.append((os.path.basename(prof["pdf"]), _b64(prof["pdf"])))
    if bought_pack:
        pack = G.generate_pack(ans, out_dir=outdir)
        attachments.append((os.path.basename(pack["pdf"]), _b64(pack["pdf"])))

    if email:
        send_email(email, ans["name"], attachments)
        print(f"Delivered {len(attachments)} PDF(s) to {email} (signature={prof.get('signature')})")
    else:
        print("No email on session; generated but not sent.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)

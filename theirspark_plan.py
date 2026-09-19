# -*- coding: utf-8 -*-
"""Their Spark — The Nurture Plan ($29).

A 30-day, strengths-matched roadmap of tiny daily moves, personalised to the
child's signature strength. Reuses the layout engine (build_profiles) and the
per-archetype content, and adds a small set of bespoke daily "moves" per
strength so every one of the 30 days is concrete and on-brand.

Public API:
    generate_plan(answers, out_dir=".") -> {"pdf": path, "signature": key}

`answers` is the same dict used by theirspark_generator:
    {"name","age","gender","scores"|"strengths"}
"""
import os, re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

import build_profiles as E           # layout engine + 5 archetypes' content
import theirspark_generator as G     # adds Maker to E.CONTENT + scoring/pronouns

HX = E.HexColor

# ---------------------------------------------------------------- bespoke daily moves
# ~8 concrete, tiny, at-home actions per archetype. Tokens: {N}{s}{S}{p}{o}{noun}
MOVES = {
 "Maker": [
  "Before {N} wakes, leave a small ‘invitation to build’ on the table — three or four odd materials, no instructions. See what {s} makes of them.",
  "Give {N} a real (safe) tool today — a kid screwdriver, a whisk, a trowel — and a genuine job to use it on.",
  "Find one thing at home that’s broken or boring and ask {N}: ‘How could we fix or improve this?’ Then build the idea together.",
  "Declare one ‘no-tidying’ spot so {N} can leave a project out overnight and come back to improve it.",
  "Cook or bake something together and let {N} run a whole step start to finish — measuring, mixing, deciding.",
  "Take apart something safe and dead together — an old torch, a pen — just to see what’s inside.",
  "Photograph one thing {N} made this week and put it somewhere the family can see it.",
  "Hand {N} a cardboard box and one challenge: ‘Make this into something you could actually use.’ Then use it.",
 ],
 "Storyteller": [
  "Ask {N} for a role in {p} pretend world today — ‘What’s my name? What do I do?’ — and play it seriously for five minutes.",
  "Write down one of {N}’s made-up stories word for word, and read it back to {o} at bedtime.",
  "Read a book a notch above {p} level and stop before the end: ‘What do you think happens next?’",
  "Make a tiny book together — fold paper, {s} dictates, you staple it into a real, keepable thing.",
  "Turn a boring chore into a story: ‘These socks are on a quest to find their pairs.’",
  "Let {N} put on a two-minute ‘show’ after dinner, with the family as a patient audience.",
  "Draw a picture together and ask {N} to tell you the whole story behind it.",
  "At bedtime, start a story with one sentence and take turns adding the next.",
 ],
 "Connector": [
  "At dinner, name one feeling you noticed in someone today, and ask {N} what {s} saw in {p} friends.",
  "Give {N} one real, needed job framed as helping the family — and thank {o} for it out loud.",
  "Build in ten minutes of quiet ‘refill’ time and name it kindly: ‘Even loving people need to fill back up.’",
  "Help {N} do one small act of kindness — a card, a welcome, a share — and let it be {p} idea.",
  "After a busy day, offer a decompression ritual: a snack, a cuddle, low light, no questions.",
  "Practise kind honesty together: ‘It’s okay to want something different — let’s say it nicely.’",
  "Ask {N} who was left out today, and what {s} did — or could do next time — about it.",
  "Give {N} a small person to look after for a bit — a younger sibling, a pet, a plant — and notice the pride.",
 ],
 "Thinker": [
  "When {N} asks ‘why’ today, answer with ‘What do you think?’ and follow {p} reasoning wherever it goes.",
  "Take {p} current obsession one level deeper — a library book, a documentary, a real expert if you can.",
  "Pose a puzzle with no obvious answer at dinner, and test {p} theory together.",
  "Let {N} struggle productively with something today — resist solving it; ask ‘what have you tried?’",
  "Reframe one mistake as data: ‘That didn’t work — so now we know what?’",
  "Give a worry somewhere to go: write the question down together and pick a time to think about it.",
  "Explain the reason behind one rule or change today, instead of ‘because I said so.’",
  "Start a small collection {N} can sort and classify — rocks, cards, stickers, facts.",
 ],
 "Leader": [
  "Hand {N} real ownership of one thing today — plan the walk, run the tidy-up, lead the game.",
  "When {s} steamrolls, pause and coach: ‘A great leader checks — does everyone else want to play it this way?’",
  "Give a genuine choice with real consequences, and let {o} live with the result.",
  "Channel the fairness radar: make {N} the ‘fairness monitor’ for a family activity.",
  "Hold one calm, firm limit today and stay steady when {s} pushes — that steadiness is a gift.",
  "Set a small goal with a clear finish line, and celebrate reaching it together.",
  "Let {N} lead something that helps someone else — a small project, a job for a sibling.",
  "Ask {N} to make the plan for part of the day, then actually follow {p} plan.",
 ],
 "Explorer": [
  "Take a different route somewhere today and let {N} lead the way.",
  "Say yes to one messy, physical thing — puddles, climbing, digging — and let {o} really go for it.",
  "Head outside with no plan and follow {p} curiosity for twenty minutes.",
  "Set a real challenge for {p} body: ‘Can you get all the way across without touching the ground?’",
  "Let {N} try something slightly daring with you spotting — a higher climb, a new skill.",
  "Turn an errand into an expedition: a map, a mission, one small discovery to find.",
  "Build movement in before something still — a run around the garden before the quiet task.",
  "Explore somewhere new this week — a trail, a creek, a part of town you’ve never walked.",
 ],
}

WEEKLY_REFLECT = [
 "Look back over this week. When did {N} lose track of time? That’s {p} spark showing — jot it down.",
 "Which small change landed best this week? Keep the one that made your days easier, drop the rest.",
 "Where did {N} stretch or wobble this week? How did meeting it calmly — instead of fixing it — go?",
 "What did you notice about {N} this month that you hadn’t put into words before? Write it down.",
]

WEEK_THEMES = [
 ("WEEK ONE", "Notice & name",
  "This week you change nothing — you just watch. The job is to spot {N}’s {noun} strength in the wild and give it words. Noticing on purpose is where everything else begins."),
 ("WEEK TWO", "Nurture at home",
  "Now, small tweaks. None of this needs a budget or a spare hour — just tiny changes to the days you already have, matched to how {N} is wired."),
 ("WEEK THREE", "A gentle stretch",
  "Strengths grow at their edges. This week adds a little challenge and a little friction. Met calmly, this is exactly where {N}’s confidence gets built."),
 ("WEEK FOUR", "Celebrate & sustain",
  "The last stretch is about making it stick — naming how far {N}’s come, and choosing the handful of moves worth keeping for good."),
]

BEYOND_THEME = ("BEYOND DAY 28", "Making it stick",
  "Two last moves to carry the plan past this month.")

# ---------------------------------------------------------------- helpers
def _nurture_actions(A):
    """Turn the profile's nurture_cards into (label, first-sentence) pairs."""
    out = []
    for title, body in A["nurture_cards"]:
        label = re.sub(r"^Try this:\s*", "", title).strip()
        label = (label[:1].upper() + label[1:]) if label else "Try this"
        first = re.split(r"(?<=[.!?])\s", body.strip())[0]
        out.append((label, first))
    return out

def _thrive_items(A):
    items = []
    for _h, lst in A["thrives"]:
        items.extend(lst)
    return items

def _build_days(A, key):
    """Return a list of dicts: {n, label, body, say, week} — exactly 30 days."""
    cv = A["convo"]; af = A["affirm"]; sh = A["shows"]
    th = _thrive_items(A); sh_help = A["str_help"]; nc = _nurture_actions(A)
    exp = A["experiment"]; mv = MOVES[key]
    D = []
    def add(n, week, label, body, say=None):
        D.append({"n": n, "week": week, "label": label, "body": body, "say": say})
    # Week 1 — Notice & name
    add(1, 0, "Notice", "Watch for this today, without commenting on it: " + sh[0])
    add(2, 0, "Ask", "Find a calm moment and try this question:", cv[0])
    add(3, 0, "Try", mv[0])
    add(4, 0, "Notice", "Keep watching. Today, look for: " + sh[1])
    add(5, 0, "Say it", "Catch a real moment today and say it out loud:", af[0])
    add(6, 0, "Play", "Make room for this today: " + th[0])
    add(7, 0, "Reflect", WEEKLY_REFLECT[0])
    # Week 2 — Nurture at home
    add(8, 1, nc[0][0], nc[0][1])
    add(9, 1, "Ask", "Try this one in the car or at dinner:", cv[1])
    add(10, 1, "Try", mv[1])
    add(11, 1, "Play", "Set up time for: " + th[1])
    add(12, 1, nc[1][0], nc[1][1])
    add(13, 1, "Say it", "Say it, and mean it:", af[1])
    add(14, 1, "Reflect", WEEKLY_REFLECT[1])
    # Week 3 — A gentle stretch
    add(15, 2, "Stretch", mv[2])
    add(16, 2, "In the hard moment", "When it gets tricky today, try: " + sh_help[0])
    add(17, 2, "Play", "Offer this: " + th[2])
    add(18, 2, "Ask", "A question worth sitting with today:", cv[2])
    add(19, 2, nc[2][0], nc[2][1])
    add(20, 2, "In the hard moment", "Another one to keep in your pocket: " + sh_help[1])
    add(21, 2, "Reflect", WEEKLY_REFLECT[2])
    # Week 4 — Celebrate & sustain
    add(22, 3, "Try", mv[3])
    add(23, 3, "Say it", "One more to say out loud:", af[2])
    add(24, 3, "Play", "Make time for: " + th[3])
    add(25, 3, "Ask", "Ask, and really listen:", cv[3])
    add(26, 3, "10-minute experiment", exp)
    add(27, 3, "Try", mv[4])
    add(28, 3, "Reflect", WEEKLY_REFLECT[3])
    # Beyond
    add(29, 4, "Ask", "One last question to keep the conversation going:", cv[4])
    add(30, 4, "Keep it going",
        "Look back over the month and pick the three moves {N} loved most — the ones "
        "that made {o} light up. Those three are your plan for next month. Small and steady wins.")
    return D

# ---------------------------------------------------------------- page machinery (local footer)
def _footer():
    c = E.c
    c.setStrokeColor(E.LINE); c.setLineWidth(0.7); c.line(E.ML, 60, E.PW - E.MR, 60)
    E.draw_logo(E.ML, 57, 12, E.INK, E.SAGE)
    c.setFont("Sans", 8); c.setFillColor(E.MUTED)
    c.drawRightString(E.PW - E.MR, 48, f"{E.NAME}’s Nurture Plan  ·  {E.st['page']}")

def _new_page():
    E.c.showPage(); E.st["page"] += 1; E.page_bg(); _footer(); E.st["y"] = E.TOP

def _need(h):
    if E.st["y"] - h < E.BOTTOM:
        _new_page()

# ---------------------------------------------------------------- day block
def _day_block(d):
    c = E.c; f = E.fmt; ML = E.ML; CW = E.CW
    body = f(d["body"]); say = f(d["say"]) if d["say"] else None
    body_lines = E.wrap(body, "Sans", 10.3, CW - 46)
    say_lines = E.wrap(say, "Serif-I", 11, CW - 62) if say else []
    h = 20 + len(body_lines) * 14.5 + (10 + len(say_lines) * 16 if say else 0) + 12
    _need(h)
    top = E.st["y"]
    # number badge
    c.setFillColor(E.SOFT); c.roundRect(ML, top - 30, 34, 30, 8, fill=1, stroke=0)
    c.setFont("Serif-B", 15); c.setFillColor(E.SAGED)
    c.drawCentredString(ML + 17, top - 21, str(d["n"]))
    tx = ML + 46
    # label kicker
    c.setFont("Sans-B", 8); c.setFillColor(E.SAGE)
    c.drawString(tx, top - 9, "  ".join(list(d["label"].upper())))
    # body
    yy = top - 22
    c.setFont("Sans", 10.3); c.setFillColor(E.INK)
    for ln in body_lines:
        c.drawString(tx, yy - 8, ln); yy -= 14.5
    # say line (mini quote)
    if say:
        yy -= 4
        c.setStrokeColor(E.SAGE); c.setLineWidth(2.5)
        c.line(tx + 2, yy - 6, tx + 2, yy - 6 - len(say_lines) * 16 + 4)
        c.setFont("Serif-I", 11); c.setFillColor(E.SAGED)
        for ln in say_lines:
            c.drawString(tx + 14, yy - 12, ln); yy -= 16
    E.st["y"] = top - h

# ---------------------------------------------------------------- cover
def _cover(A):
    c = E.c; f = E.fmt
    E.page_bg()
    c.setFillColor(E.SAGED); c.rect(0, E.PH - 300, E.PW, 300, fill=1, stroke=0)
    E.draw_icon_c(E.PW - 92, E.PH - 100, 92, HX("#33534A"))
    E.draw_logo(E.ML, E.PH - 60, 19, HX("#F4F8F5"), HX("#F4F8F5"))
    c.setFont("Sans-B", 9.5); c.setFillColor(HX("#9FC3B4"))
    c.drawString(E.ML, E.PH - 140, "  ".join(list("THE 30-DAY NURTURE PLAN")))
    c.setFont("Serif-B", 52); c.setFillColor(E.WHITE); c.drawString(E.ML - 2, E.PH - 205, E.NAME)
    c.setFont("Sans", 12); c.setFillColor(HX("#C7DBD0"))
    c.drawString(E.ML, E.PH - 232, f"A roadmap for {E.NAME}  ·  Age {E.AGE}  ·  {E.TODAY}")
    c.setFont("Sans-B", 9.5); c.setFillColor(E.SAGE)
    c.drawString(E.ML, E.PH - 360, "  ".join(list("MATCHED TO THE " + A["noun"].upper())))
    c.setFont("Serif-B", 34); c.setFillColor(E.INK); c.drawString(E.ML - 2, E.PH - 404, "The " + E.NOUN)
    c.setFont("Serif-I", 14); c.setFillColor(E.SAGE); c.drawString(E.ML, E.PH - 428, A["tag"])
    yy = E.PH - 466; c.setFont("Sans", 11); c.setFillColor(E.INK)
    intro = f("Thirty tiny, doable moves — one a day — chosen to fit exactly how {N} thinks, "
              "plays, and connects. No budget, no lesson plans. Just small, steady steps that "
              "turn what you learned in {p} profile into everyday habit.")
    for ln in E.wrap(intro, "Sans", 11, E.CW - 6):
        c.drawString(E.ML, yy, ln); yy -= 17
    c.setStrokeColor(E.LINE); c.setLineWidth(0.8); c.line(E.ML, 92, E.PW - E.MR, 92)
    c.setFont("Sans", 8.5); c.setFillColor(E.MUTED)
    c.drawString(E.ML, 78, "A guidance & enrichment plan for parents."); c.drawRightString(E.PW - E.MR, 78, "Their Spark")

# ---------------------------------------------------------------- render
def _render(key, child, out):
    A = E.CONTENT[key]
    E.NAME, E.SUB, E.POS, E.OBJ, E.AGE = child
    E.NOUN = A["noun"]
    f = E.fmt
    E.c = canvas.Canvas(out, pagesize=A4); E.st = {"y": E.TOP, "page": 1}
    _cover(A)
    # how to use
    _new_page(); E.kicker("How this plan works")
    E.h1(f("One small move a day, for thirty days."))
    E.para(f("You don’t need to do this perfectly, or even every single day. Miss one? Pick up "
             "the next. The point isn’t a checklist — it’s a gentle month of paying attention to "
             "{N}’s {noun} strength and feeding it in tiny ways."))
    E.para("The month has four simple movements:")
    E.bullets([
        f("Week 1 — Notice & name: learn to spot {N}’s strength and give it words."),
        f("Week 2 — Nurture at home: tiny tweaks to the days you already have."),
        f("Week 3 — A gentle stretch: small challenges that build confidence."),
        f("Week 4 — Celebrate & sustain: keep the handful of moves worth keeping."),
    ])
    E.quote(f("Small and steady beats big and rare. Ten quiet minutes with {N}, most days, "
              "will do more than any grand gesture."))
    # days grouped by week
    days = _build_days(A, key)
    cur_week = -1
    for d in days:
        if d["week"] != cur_week:
            cur_week = d["week"]
            theme = WEEK_THEMES[cur_week] if cur_week < 4 else BEYOND_THEME
            _need(120)
            if E.st["y"] < E.TOP - 20:
                _new_page()
            E.kicker(theme[0])
            E.h1(f(theme[1]))
            E.para(f(theme[2]), gap=8)
        _day_block(d)
    # closing
    _new_page(); E.kicker("One last thing")
    E.h1(f("You’re already the plan."))
    E.para(f("Thirty days from now, the biggest change won’t be anything on this list — it’ll "
             "be you, watching {N} a little more closely and meeting {o} where {s} already is. "
             "That’s the whole secret, and you already have it."))
    E.st["y"] -= 6; E.rule()
    E.c.setFont("Sans", 8.5); E.c.setFillColor(E.MUTED)
    disc = ("Their Spark is a guidance and enrichment tool for parents. It is not a diagnostic, medical, or "
            "psychological assessment, and it is not a substitute for professional advice. Every child is unique; "
            "use this plan as a lens, always alongside your own knowledge of your child.")
    for ln in E.wrap(disc, "Sans", 8.5, E.CW):
        E.c.drawString(E.ML, E.st["y"] - 9, ln); E.st["y"] -= 12
    _footer(); E.c.save()
    return out

# ---------------------------------------------------------------- public API
def generate_plan(answers, out_dir="."):
    name = (answers.get("name") or "your child").strip() or "your child"
    age = str(answers.get("age") or "").strip()
    sub, pos, obj = G.pronouns(answers.get("gender"))
    counts = answers.get("scores") or G.score(answers.get("strengths", []))
    key = G.signature(counts)
    child = (name, sub, pos, obj, age)
    safe = re.sub(r"[^A-Za-z0-9]+", "_", name) or "child"
    out = os.path.join(out_dir, f"theirspark-{safe}-NurturePlan.pdf")
    _render(key, child, out)
    return {"pdf": out, "signature": key}

# ---------------------------------------------------------------- demo
if __name__ == "__main__":
    G.setup_fonts()
    demos = [
        {"name": "Mia",   "age": "6", "gender": "Girl", "scores": {"Maker": 5, "Thinker": 3, "Explorer": 2, "Storyteller": 1, "Connector": 1, "Leader": 0}},
        {"name": "Diego", "age": "6", "gender": "Boy",  "scores": {"Leader": 5, "Connector": 3, "Explorer": 2, "Thinker": 1, "Maker": 1, "Storyteller": 0}},
        {"name": "Ava",   "age": "5", "gender": "Girl", "scores": {"Storyteller": 5, "Connector": 3, "Maker": 2, "Thinker": 1, "Explorer": 1, "Leader": 0}},
        {"name": "Noah",  "age": "7", "gender": "Boy",  "scores": {"Connector": 5, "Storyteller": 3, "Leader": 2, "Thinker": 1, "Explorer": 1, "Maker": 0}},
        {"name": "Sofia", "age": "8", "gender": "Girl", "scores": {"Thinker": 5, "Maker": 3, "Explorer": 2, "Storyteller": 1, "Leader": 1, "Connector": 0}},
        {"name": "Kai",   "age": "5", "gender": "Boy",  "scores": {"Explorer": 5, "Maker": 3, "Leader": 2, "Thinker": 1, "Connector": 1, "Storyteller": 0}},
    ]
    for d in demos:
        print(generate_plan(d, "."))

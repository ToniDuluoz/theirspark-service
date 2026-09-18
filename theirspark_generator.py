# -*- coding: utf-8 -*-
"""Their Spark — production profile generator.

generate(answers) -> personalised PDF, chosen from the child's actual quiz answers.
Fonts: embeds Fraunces (serif) + Inter (sans) if the .ttf files are found in ./fonts
or the current folder; otherwise falls back to DejaVu (bundled on most Linux boxes).

Reuses the layout engine + 5 archetypes' copy from build_profiles.py and adds Maker,
so all six strength types are available as data.
"""
import os, glob, json, sys, re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import build_profiles as E   # engine + CONTENT (5 archetypes); __main__ guard stops its sample run

# ---------------------------------------------------------------- fonts
def setup_fonts():
    """Embed Fraunces/Inter if available; else keep DejaVu (already registered by build_profiles)."""
    here = os.path.dirname(os.path.abspath(__file__))
    dirs = [os.path.join(here, "fonts"), here, "."]
    def find(*pats):
        for d in dirs:
            for pat in pats:
                m = sorted(glob.glob(os.path.join(d, pat)))
                if m: return m[0]
        return None
    used = {"serif": "DejaVu Serif", "sans": "DejaVu Sans"}
    fr  = find("Fraunces*Regular*.ttf", "Fraunces-Regular*.ttf", "Fraunces[!I]*.ttf", "Fraunces*.ttf")
    frb = find("Fraunces*SemiBold*.ttf", "Fraunces*Bold*.ttf")
    fri = find("Fraunces*Italic*.ttf", "Fraunces-Italic*.ttf")
    inr = find("Inter*Regular*.ttf", "Inter-Regular*.ttf", "Inter[!I]*.ttf", "Inter*.ttf")
    inb = find("Inter*SemiBold*.ttf", "Inter*Bold*.ttf")
    ini = find("Inter*Italic*.ttf")
    try:
        if fr and frb:
            pdfmetrics.registerFont(TTFont("Serif", fr))
            pdfmetrics.registerFont(TTFont("Serif-B", frb))
            pdfmetrics.registerFont(TTFont("Serif-I", fri or fr))
            used["serif"] = "Fraunces (embedded)"
    except Exception as e:
        print("Fraunces load failed:", e)
    try:
        if inr and inb:
            pdfmetrics.registerFont(TTFont("Sans", inr))
            pdfmetrics.registerFont(TTFont("Sans-B", inb))
            pdfmetrics.registerFont(TTFont("Sans-I", ini or inr))
            used["sans"] = "Inter (embedded)"
    except Exception as e:
        print("Inter load failed:", e)
    return used

# ---------------------------------------------------------------- Maker content (as data)
E.CONTENT["Maker"] = {
 "child": ("Mia","she","her","her","6"),
 "noun": "Maker", "tag": "Hands-on builder & creator",
 "h1_line": "{N} is a Maker.",
 "portrait": [
  "Makers understand the world by building it. Where another child asks how something works, a Maker reaches out and finds out — stacking, joining, taking apart, remixing. For {N}, thinking and doing are the same motion. Ideas don’t feel real to {o} until {s} can hold them in {p} hands.",
  "This is the strength of the inventor, the craftsperson, the engineer and the artist — anyone who turns ‘what if’ into ‘look what I made.’ It shows up early as a love of blocks, tools, art supplies, snap-together toys, and cheerful, purposeful mess. Underneath the mess is something serious: a child learning that {s} can act on the world and change it.",
 ],
 "shows": [
  "{N} learns by doing — {s} would rather try, fail, and adjust than be told the ‘right’ way first.",
  "Given a problem, {s} looks for a clever workaround rather than giving up or waiting for help.",
  "Finished isn’t always the point — the building, tinkering, and improving is where {s} comes alive.",
  "A pile of ‘stuff’ (boxes, tape, odds and ends) can hold {p} attention longer than most toys.",
 ],
 "glance": "Learns best by: making, testing, and improving with {p} hands.   Energized by: open-ended materials and a real problem to solve.   Needs: permission to make mess and mistakes.   Watch for: frustration when a vision outruns {p} skill.",
 "q1": "A Maker isn’t just busy — {s}’s rehearsing agency. Every ‘I made this’ is really ‘I can shape my world.’",
 "blend": {"The Maker":0.95,"The Thinker":0.66,"The Explorer":0.52,"The Storyteller":0.34,"The Connector":0.30,"The Leader":0.18},
 "blend_note": "{N}’s Maker strength is amplified by {p} Thinker streak: {s} doesn’t just build — {s} builds to answer a question. And {p} Explorer energy means {s} learns fastest on {p} feet, with room to move. Keep these three fed and {N} flourishes.",
 "mix_card": "Strengths don’t work in isolation. The rest of this profile focuses on the Maker, but the best activities for {N} tend to touch two or three of {p} top strengths at once — building something (Maker) that solves a real puzzle (Thinker) out in the world (Explorer).",
 "thinks": "{N} thinks with {p} hands. Abstract instructions can wash over {o}, but give {o} a concrete problem and materials and you’ll see focus arrive like a switch flipping. {S} reasons by trial: try, notice, adjust, try again. This looks like play, but it’s real problem-solving — the same loop engineers and scientists use their whole lives.",
 "feels": "{N}’s big feelings often cluster around {p} work. Deep pride when something finally stands up on its own; real frustration when {p} hands can’t yet do what {p} mind pictures. That frustration isn’t misbehaviour — it’s the gap between vision and skill, and it’s a sign {s} cares. How you meet those moments matters more than the finished tower.",
 "connects": "{N} often connects side-by-side rather than face-to-face — building next to a friend, sharing tools, showing rather than telling. ‘Want to make this with me?’ can be {p} way of saying ‘I like you.’ Honour that; not every child bonds through talking, and {N}’s way is just as warm.",
 "tfc_q": "If you want a window into {N}’s heart, don’t ask {o} to sit still and talk. Sit down and build alongside {o}.",
 "nurture_intro": "You don’t need a workshop or a budget. Makers need three simple things: open-ended materials, permission to make mistakes, and an audience that cares about the process, not just the result.",
 "nurture_cards": [
  ("Try this: a ‘maker box’", "Keep a bin of open-ended bits — boxes, tape, string, corks, paper tubes, bottle caps, fabric scraps. No instructions. When {N} is bored or wound up, the box is the reset button. Rotate in one new odd material each week to keep it fresh."),
  ("Try this: praise the process", "Swap ‘That’s beautiful!’ for ‘How did you get that piece to balance?’ Naming the thinking — the trying, the fixing — teaches {N} that effort and iteration are the point, and builds a mind that keeps going when things get hard."),
  ("Try this: let it stay unfinished", "Give {N} a spot where a project can live overnight without being tidied away. Makers think across days; a half-built thing left out is an invitation to come back and improve it — exactly the muscle you want to grow."),
 ],
 "avoid": [
  "Rushing to ‘help’ the moment {s} struggles — a little productive frustration is where the learning lives.",
  "Kits with one correct outcome as the only option; balance them with truly open-ended materials.",
  "Tidying away work-in-progress too quickly. To a Maker it can feel like erasing a thought mid-sentence.",
 ],
 "thrives_intro": "These aren’t a curriculum — just well-matched starting points. Follow {N}’s lead and notice which ones make {o} lose track of time. That’s the signal you’re on the right track.",
 "thrives": [
  ("Hands-on play", ["Building sets with real engineering (magnetic tiles, gears, marble runs, quality blocks).","‘Loose parts’ play — cardboard, tape, and recyclables beat most single-purpose toys.","Simple real tools with supervision: a kid-safe hammer, a glue gun, a trowel in the garden."]),
  ("Making & art", ["Sculpture and construction over colouring pages — clay, dough, wire, collage, junk-modelling.","‘Fix-it’ projects: taking apart an old radio or clock to see what’s inside.","Cooking and baking — a delicious, hands-on system with steps, cause, and effect."]),
  ("Out in the world", ["Hardware stores, maker fairs, science museums with build-it stations.","A patch of garden or a sandbox — somewhere {s} can dig, dam, and reshape.","Building forts and dens: architecture {s} can walk inside."]),
 ],
 "screens": ("A note on screens", "Makers can absolutely thrive with the right screen time — look for creation over consumption: simple coding for kids, stop-motion animation, digital drawing, building games. The test: does {N} make something {s} can point to afterward?"),
 "str_intro": "Every strength has a shadow side. For Makers, it’s the storm that hits when {p} hands can’t yet build what {p} imagination sees — the tower that won’t stand, the drawing that ‘looks wrong.’ Knowing the pattern helps you meet it calmly.",
 "str_look": [
  "Sudden frustration, sweeping the pieces away, or ‘I’m bad at this!’",
  "Perfectionism — refusing to finish because it isn’t matching the picture in {p} head.",
  "Shutting down when made to switch tasks before a build feels ‘done.’",
 ],
 "str_help": [
  "Name the gap, kindly: ‘Your idea is bigger than your hands can do yet — that’s so normal.’",
  "Shrink the step: ‘Let’s just get these two to balance first.’ One small win restarts the engine.",
  "Give a heads-up before transitions: ‘Five more minutes, then we pause — we can leave it out to finish later.’",
 ],
 "phrases": "Instead of ‘Calm down, it’s fine’ try ‘That’s the tricky part — what could we try next?’  Instead of ‘Just leave it’ try ‘Let’s save it right here and come back.’ You’re teaching {N} that a wall is information, not failure.",
 "grows": [
  "It’s early, and the point is never to pick {N}’s career at six. But it helps to know the deeper trait you’re nurturing: agency — the felt sense that ‘I can make things happen.’ Children who keep that flame tend to become adults who build, fix, design, and start things.",
  "The Maker strength is the common root under engineers and architects, chefs and surgeons, product designers, software builders, craftspeople, sculptors, and founders. What unites them isn’t a job title — it’s a lifelong comfort with turning ideas into real, working things, and a resilience built from a thousand small ‘try again’s.",
 ],
 "trait": "If you protect just one thing, protect {N}’s belief that effort changes outcomes. Makers learn this at the block table before they ever learn it anywhere else. Every time you let {o} struggle a little and then succeed, you’re building the quiet confidence that outlasts any single skill.",
 "grows_q": "You’re not raising a future job title. You’re raising a child who believes {s} can shape the world — and that belief travels everywhere.",
 "convo": [
  "‘If you could build anything at all and it would definitely work, what would you make?’",
  "‘What’s something you fixed or figured out this week? Show me how.’",
  "‘What’s the trickiest part of this one? What might you try next?’",
  "‘Want to make something together after dinner — you’re the boss, I’m the helper.’",
  "‘If this could be even better, what would you change?’",
 ],
 "affirm": [
  "‘You’re the kind of kid who figures things out.’",
  "‘Mistakes are just the parts you haven’t fixed yet.’",
  "‘I love watching you make things.’",
 ],
 "experiment": "Hand {N} three unrelated objects (a spoon, a cork, a rubber band) and one playful challenge: ‘Can you invent a machine that moves this pom-pom across the table?’ No right answer, no help unless asked. Then ask {o} to explain how it works. You’ll see the Maker light up — and learn a surprising amount about how {s} thinks.",
}

# ---------------------------------------------------------------- scoring
ARCHETYPES = ["Maker","Storyteller","Connector","Thinker","Leader","Explorer"]
PRIORITY   = ["Connector","Thinker","Maker","Storyteller","Leader","Explorer"]  # tie-break, matches funnel

def pronouns(gender):
    g = (gender or "").strip().lower()
    if g in ("girl","female","she","f"):   return ("she","her","her")
    if g in ("boy","male","he","m"):        return ("he","his","him")
    return ("they","their","them")   # NOTE: copy is tuned for she/he; 'they' needs a grammar pass

def score(strength_answers):
    """strength_answers: list of archetype names chosen across the scoring questions."""
    counts = {a:0 for a in ARCHETYPES}
    for a in strength_answers:
        if a in counts: counts[a]+=1
    return counts

def signature(counts):
    best, bestc = PRIORITY[0], -1
    for a in PRIORITY:
        if counts.get(a,0) > bestc:
            bestc, best = counts[a], a
    return best

def blend_from_counts(counts):
    """Map real counts -> bar values (signature ~0.95, others proportional, gentle floor)."""
    mx = max(counts.values()) or 1
    out = {}
    for a in ARCHETYPES:
        frac = counts.get(a,0)/mx
        out["The "+a] = round(0.20 + 0.75*frac, 3)
    return out

# ---------------------------------------------------------------- render one profile
def _render(key, child, blend, out):
    A = E.CONTENT[key]
    E.NAME, E.SUB, E.POS, E.OBJ, E.AGE = child
    E.NOUN = A["noun"]
    art = "an" if E.NOUN[0] in "AEIOU" else "a"
    E.c = canvas.Canvas(out, pagesize=A4); E.st = {"y": E.TOP, "page": 1}
    saved = A.get("blend"); A["blend"] = blend           # inject real blend for blend_page
    f = E.fmt
    E.cover(A)
    E.new_page(); E.kicker("A note before you begin")
    E.h1(f("Every child is a whole world. This is one clear window into {N}’s."))
    E.para(f("You know {N} better than any quiz ever could. What a profile like this can do is give language to things you may already sense — and a few you haven’t noticed yet — so you can nurture them on purpose."))
    E.para(f("We looked at how {N} plays, solves problems, handles frustration, and connects with others. Across every answer, one pattern came through more strongly than the rest. We call it {N}’s signature strength, and for {N} it is The {noun}."))
    E.para(f("A signature strength isn’t the whole story — no child is only one thing, and you’ll see {N}’s full blend a few pages in. Think of it as {p} default setting: the mode {s} returns to when {s} is free to be {o}self."))
    E.quote(f("Read this with {N} in mind, not against a standard. The goal isn’t to fix anything — it’s to help {p} become more fully who {s} already is."))
    E.para(f("Here’s how to use it: skim it once for the shape of things, then come back to the two sections most parents dog-ear — “Nurturing the {noun} at home” and “Try this week.” Small, steady changes there do more than any single grand gesture."))
    E.new_page(); E.kicker("Signature strength"); E.h1(f(A["h1_line"]))
    for p in A["portrait"]: E.para(f(p))
    E.h2(f("How it shows up in {N}"), color=E.SAGE); E.bullets([f(x) for x in A["shows"]])
    E.card("At a glance", f(A["glance"]), fill=E.SOFT, stroke=E.SOFT); E.quote(f(A["q1"]))
    E.blend_page(A)
    E.new_page(); E.kicker(f("Inside {N}’s world")); E.h1(f("How {N} thinks, feels, and connects."))
    E.h2(f("How {s} thinks"), color=E.SAGE, top=2); E.para(f(A["thinks"]))
    E.h2(f("How {s} feels")); E.para(f(A["feels"]))
    E.h2(f("How {s} connects")); E.para(f(A["connects"])); E.quote(f(A["tfc_q"]))
    E.new_page(); E.kicker(f("Nurturing the {noun} — at home")); E.h1(f("Small changes that help {N} thrive."))
    E.para(f(A["nurture_intro"]))
    for t,b in A["nurture_cards"]: E.card(f(t), f(b))
    E.h2("Gently avoid", color=E.SAGED); E.bullets([f(x) for x in A["avoid"]])
    E.new_page(); E.kicker(f("Where {N} thrives")); E.h1(f"Activities and spaces built for {art} {E.NOUN}.")
    E.para(f(A["thrives_intro"]))
    for i,(ht,items) in enumerate(A["thrives"]):
        E.h2(f(ht), color=E.SAGE, top=(2 if i==0 else 6)); E.bullets([f(x) for x in items])
    E.card(A["screens"][0], f(A["screens"][1]), fill=E.SOFT, stroke=E.SOFT)
    E.new_page(); E.kicker(f"When the {E.NOUN} hits a wall"); E.h1(f("Supporting {N} through the hard moments."))
    E.para(f(A["str_intro"]))
    E.h2("What it can look like", color=E.SAGE, top=2); E.bullets([f(x) for x in A["str_look"]])
    E.h2("How to help in the moment"); E.bullets([f(x) for x in A["str_help"]])
    E.card("Phrases that land", f(A["phrases"]), fill=E.CREAM, stroke=E.CREAM)
    E.new_page(); E.kicker("Where this can lead"); E.h1(f"The {E.NOUN}, grown up.")
    for p in A["grows"]: E.para(f(p))
    E.card("The trait under the trait", f(A["trait"]), fill=E.SOFT, stroke=E.SOFT); E.quote(f(A["grows_q"]))
    E.new_page(); E.kicker(f("Try this week with {N}")); E.h1("Five small things to try in the next seven days.")
    E.h2("Conversation starters", color=E.SAGE, top=2); E.bullets([f(x) for x in A["convo"]])
    E.h2("Affirmations to say out loud"); E.bullets([f(x) for x in A["affirm"]])
    E.card("One 10-minute experiment", f(A["experiment"]), fill=E.CREAM, stroke=E.CREAM)
    E.new_page(); E.kicker("One last thing"); E.h1("Keep looking for the spark.")
    E.para(f("A profile is a snapshot; {N} is a movie. {S} will grow, surprise you, and shift. What won’t change is the value of a parent who sees {o} clearly and nurtures what’s already there. You’re already doing that — you read to the end."))
    E.para("If this was useful, a few gentle next steps can help you turn insight into everyday habit:")
    E.bullets([f("The Nurture Plan — a 30-day, strengths-matched roadmap of tiny daily moves for {N}."),
               f("Spark Club — fresh activities matched to {N} each month, and a re-assessment as {s} grows."),
               f("A sibling profile — see how {N}’s strengths compare with a brother or sister’s.")])
    E.st["y"]-=6; E.rule()
    E.c.setFont("Sans",8.5); E.c.setFillColor(E.MUTED)
    disc=("Their Spark is a guidance and enrichment tool for parents. It is not a diagnostic, medical, or "
          "psychological assessment, and it is not a substitute for professional advice. Every child is unique; "
          "use this profile as a lens, always alongside your own knowledge of your child.")
    for ln in E.wrap(disc,"Sans",8.5,E.CW): E.c.drawString(E.ML, E.st["y"]-9, ln); E.st["y"]-=12
    E.footer(); A["blend"]=saved; E.c.save()
    return out

# ---------------------------------------------------------------- public API
def generate(answers, out_dir="."):
    """answers = {
         'name': 'Mia', 'age': '6', 'gender': 'Girl',
         'strengths': ['Maker','Thinker','Maker','Explorer','Maker','Thinker','Maker']  # the scoring answers
       }
       or provide 'scores': {archetype: count}.
    """
    name = (answers.get("name") or "your child").strip() or "your child"
    age  = str(answers.get("age") or "").strip()
    sub,pos,obj = pronouns(answers.get("gender"))
    counts = answers.get("scores") or score(answers.get("strengths", []))
    key = signature(counts)
    blend = blend_from_counts(counts)
    child = (name, sub, pos, obj, age)
    safe = re.sub(r"[^A-Za-z0-9]+","_", name) or "child"
    out = os.path.join(out_dir, f"theirspark-{safe}-{key}.pdf")
    _render(key, child, blend, out)
    return {"pdf": out, "signature": key, "scores": counts, "blend": blend}

# ---------------------------------------------------------------- CLI / demo
if __name__ == "__main__":
    fonts = setup_fonts()
    print("Fonts ->", fonts)
    if len(sys.argv) > 1 and sys.argv[1] != "--demo":
        answers = json.load(open(sys.argv[1], encoding="utf-8"))
        out_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        print(generate(answers, out_dir))
    else:
        demos = [
          {"name":"Leo","age":"5","gender":"Boy",
           "strengths":["Explorer","Explorer","Maker","Explorer","Leader","Explorer","Explorer"]},
          {"name":"Nora","age":"7","gender":"Girl",
           "strengths":["Connector","Connector","Storyteller","Connector","Connector","Thinker","Connector"]},
        ]
        for d in demos:
            print(generate(d, "."))


# ============================ THE EVERYDAY PACK ============================
def _do_items(A):
    out=[]
    for t,_ in A["nurture_cards"]:
        t2=re.sub(r'^Try this:\s*','',t).strip()
        out.append(t2[0].upper()+t2[1:])
    return out

def _twocol(c, y, ltitle, litems, rtitle, ritems):
    ML=E.ML; CW=E.CW; gap=24; colw=(CW-gap)/2
    def col(x, title, items, tcolor, bcolor):
        yy=y
        c.setFont("Sans-B",11); c.setFillColor(tcolor); c.drawString(x, yy-11, title); yy-=21
        for it in items:
            lines=E.wrap(it,"Sans",9.7,colw-13)
            c.setFillColor(bcolor); c.setFont("Sans-B",10); c.drawString(x, yy-10, "•")
            c.setFillColor(E.INK); c.setFont("Sans",9.7)
            for ln in lines: c.drawString(x+13, yy-10, ln); yy-=13.5
            yy-=5
        return yy
    y1=col(ML, ltitle, litems, E.SAGE, E.SAGE)
    y2=col(ML+colw+gap, rtitle, ritems, E.HexColor("#A9604F"), E.HexColor("#A9604F"))
    return min(y1,y2)

def render_pack(key, child, out):
    A=E.CONTENT[key]
    E.NAME,E.SUB,E.POS,E.OBJ,E.AGE=child; E.NOUN=A["noun"]
    c=canvas.Canvas(out, pagesize=A4); E.c=c; E.st={"y":E.TOP,"page":1}
    f=E.fmt; W=E.PW; H=E.PH; ML=E.ML; CW=E.CW; HX=E.HexColor
    def band(kick, title, sub):
        E.page_bg(); c.setFillColor(E.SAGED); c.rect(0,H-158,W,158,fill=1,stroke=0)
        E.draw_icon_c(W-72,H-80,74,HX("#33534A"))
        E.draw_logo(ML,H-38,14,HX("#F4F8F5"),HX("#F4F8F5"))
        c.setFont("Sans-B",9); c.setFillColor(HX("#9FC3B4")); c.drawString(ML,H-92,"  ".join(list(kick)))
        c.setFont("Serif-B",28); c.setFillColor(E.WHITE); c.drawString(ML-1,H-126,title)
        c.setFont("Serif-I",12.5); c.setFillColor(HX("#C7DBD0")); c.drawString(ML,H-146,sub)
    # ---------- PAGE 1 : FRIDGE GUIDE ----------
    band("THE FRIDGE GUIDE", f"{E.NAME} · The {E.NOUN}", A["tag"])
    y=H-192
    c.setFont("Sans-B",8.5); c.setFillColor(E.SAGE); c.drawString(ML,y,"  ".join(list("YOU'LL SEE THIS"))); y-=19
    for it in A["shows"][:3]:
        lines=E.wrap(f(it),"Sans",10,CW-14)
        c.setFillColor(E.SAGE); c.setFont("Sans-B",10); c.drawString(ML,y-10,"•")
        c.setFillColor(E.INK); c.setFont("Sans",10)
        for ln in lines: c.drawString(ML+14,y-10,ln); y-=14
        y-=5
    y-=10
    do=[f(x) for x in _do_items(A)]; avoid=[f(x) for x in A["avoid"]]
    y=_twocol(c, y, "Do more of this", do, "Gently avoid", avoid)
    y-=18
    # this-week box (fixed, no page break)
    tw=[f(A["convo"][0]), f(A["convo"][1]), f(A["affirm"][0])]
    tl=[]
    for s in tw: tl += E.wrap(s,"Sans",10,CW-32)
    bh=26+len(tl)*14+14
    c.setFillColor(E.CREAM); c.roundRect(ML,y-bh,CW,bh,12,fill=1,stroke=0)
    E.draw_icon_c(ML+19,y-17,9,E.SAGE)
    c.setFont("Sans-B",11); c.setFillColor(E.SAGE); c.drawString(ML+31,y-16,"This week, try saying…")
    yy=y-36; c.setFont("Sans",10); c.setFillColor(E.INK)
    for ln in tl: c.drawString(ML+16,yy-10,ln); yy-=14
    E.footer()
    # ---------- PAGE 2 : SHARE WITH THEIR CIRCLE ----------
    c.showPage(); E.st={"y":E.TOP,"page":2}
    band("SHARE WITH THEIR CIRCLE","Everyone on the same page", f"For {E.NAME}’s teachers, grandparents & sitters")
    E.st["y"]=H-188
    E.para(f"{E.NAME} is a {E.NOUN} — {A['tag'].lower()}. Here’s how the people who love {E.OBJ} can help {E.OBJ} shine, in a few simple moves.")
    E.h2("What helps "+E.NAME, color=E.SAGE, top=2)
    E.bullets([f(x) for x in A["str_help"]])
    E.h2("Please gently avoid")
    E.bullets([f(x) for x in A["avoid"][:2]])
    ph=f(A["phrases"]).split(" Instead")[0]
    E.quote(ph)
    E.st["y"]-=2
    E.para(f"Thank you for helping {E.NAME} grow into exactly who {E.SUB} already is.", color=E.MUTED, size=10)
    c.setFont("Serif-I",11); c.setFillColor(E.SAGE); c.drawString(ML, E.st["y"]-2, f"— {E.NAME}’s family, with Their Spark")
    E.footer(); c.save(); return out

def generate_pack(answers, out_dir="."):
    name=(answers.get("name") or "your child").strip() or "your child"
    age=str(answers.get("age") or "").strip()
    sub,pos,obj=pronouns(answers.get("gender"))
    counts=answers.get("scores") or score(answers.get("strengths",[]))
    key=signature(counts); child=(name,sub,pos,obj,age)
    safe=re.sub(r"[^A-Za-z0-9]+","_",name) or "child"
    out=os.path.join(out_dir, f"theirspark-{safe}-EverydayPack.pdf")
    render_pack(key, child, out)
    return {"pdf":out,"signature":key}

if __name__ == "__main__":
    setup_fonts()
    for d in [
      {"name":"Mia","age":"6","gender":"Girl","scores":{"Maker":5,"Thinker":3,"Explorer":2,"Storyteller":1,"Connector":1,"Leader":0}},
      {"name":"Diego","age":"6","gender":"Boy","scores":{"Leader":5,"Connector":3,"Explorer":2,"Thinker":1,"Maker":1,"Storyteller":0}},
    ]:
        print(generate_pack(d, "."))

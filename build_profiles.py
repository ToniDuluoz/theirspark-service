# -*- coding: utf-8 -*-
"""Their Spark — Strengths Profiles for Storyteller, Connector, Thinker, Leader, Explorer.
Content-driven engine (reportlab + DejaVu). Maker lives in build_maker_pdf.py."""
import math, datetime, re as _re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
try:
    from reportlab.pdfgen.canvas import FILL_NON_ZERO as _FNZ
except Exception:
    _FNZ = 1

import os as _os
# Prefer DejaVu fonts bundled next to this file (works on any host, e.g. Render);
# fall back to the common Linux system path if the bundled folder isn't present.
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_CANDS = [_HERE, _os.path.join(_HERE, "fonts"), "/usr/share/fonts/truetype/dejavu"]
D = next((p for p in _CANDS if _os.path.exists(_os.path.join(p, "DejaVuSerif.ttf"))),
         "/usr/share/fonts/truetype/dejavu") + "/"
try:
    pdfmetrics.registerFont(TTFont("Serif",   D+"DejaVuSerif.ttf"))
    pdfmetrics.registerFont(TTFont("Serif-B", D+"DejaVuSerif-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Serif-I", D+"DejaVuSerif-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("Sans",    D+"DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("Sans-B",  D+"DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Sans-I",  D+"DejaVuSans-Oblique.ttf"))
except Exception as _e:
    # Last-resort fallback so the app never crashes on boot: alias the code's
    # font names to reportlab's built-in Type-1 fonts (less pretty, still valid).
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    _std = {"Serif":"Times-Roman","Serif-B":"Times-Bold","Serif-I":"Times-Italic",
            "Sans":"Helvetica","Sans-B":"Helvetica-Bold","Sans-I":"Helvetica-Oblique"}
    from reportlab.pdfbase.pdfmetrics import getFont
    for _alias, _base in _std.items():
        try: pdfmetrics.registerFont(pdfmetrics.Font(_alias, _base, "WinAnsiEncoding"))
        except Exception: pass
    print("build_profiles: DejaVu not found, using built-in fonts:", _e)

INK=HexColor("#23303A"); SAGE=HexColor("#3F6E60"); SAGED=HexColor("#294036")
SOFT=HexColor("#E7EFEA"); SOFT2=HexColor("#F1F5F2"); IVORY=HexColor("#FBF8F2")
MUTED=HexColor("#6B7680"); LINE=HexColor("#E4DED2"); WHITE=HexColor("#FFFFFF"); CREAM=HexColor("#F3EEE4")
PW,PH=A4; ML=MR=58; CW=PW-ML-MR; TOP=PH-70; BOTTOM=78
TODAY=datetime.date.today().strftime("%B %Y")

c=None; st=None; NAME=""; SUB="she"; POS="her"; OBJ="her"; AGE="6"; NOUN=""

def _load_logo():
    for pth in ["/sessions/adoring-laughing-meitner/mnt/uploads/theirspark-logo.svg","theirspark-logo-black.svg"]:
        try:
            ds=_re.findall(r'd="([^"]+)"', open(pth,encoding="utf-8").read())
            if len(ds)>=2: return ds[0], ds[1]
        except Exception: pass
    return None,None
WORD_D,ICON_D=_load_logo()
def _add_path(p,d,T):
    toks=_re.findall(r'[MLHVCZ]|-?\d*\.?\d+', d); i=0; cx=cy=sx=sy=0.0; cmd=None
    while i<len(toks):
        t=toks[i]
        if t in "MLHVCZ": cmd=t; i+=1
        if cmd=="M":
            x=float(toks[i]);y=float(toks[i+1]);i+=2; X,Y=T(x,y); p.moveTo(X,Y); cx,cy=x,y; sx,sy=x,y; cmd="L"
        elif cmd=="L":
            x=float(toks[i]);y=float(toks[i+1]);i+=2; X,Y=T(x,y); p.lineTo(X,Y); cx,cy=x,y
        elif cmd=="H":
            x=float(toks[i]);i+=1; X,Y=T(x,cy); p.lineTo(X,Y); cx=x
        elif cmd=="V":
            y=float(toks[i]);i+=1; X,Y=T(cx,y); p.lineTo(X,Y); cy=y
        elif cmd=="C":
            x1=float(toks[i]);y1=float(toks[i+1]);x2=float(toks[i+2]);y2=float(toks[i+3]);x=float(toks[i+4]);y=float(toks[i+5]);i+=6
            A=T(x1,y1);B=T(x2,y2);E=T(x,y); p.curveTo(A[0],A[1],B[0],B[1],E[0],E[1]); cx,cy=x,y
        elif cmd=="Z":
            p.close(); cx,cy=sx,sy
        else: i+=1
def draw_logo(ox,oy,H,wc,ic):
    if not WORD_D: return
    s=H/14.0; T=lambda x,y:(ox+x*s, oy-y*s)
    p=c.beginPath(); _add_path(p,WORD_D,T); c.setFillColor(wc); c.drawPath(p,fill=1,stroke=0,fillMode=_FNZ)
    p2=c.beginPath(); _add_path(p2,ICON_D,T); c.setFillColor(ic); c.drawPath(p2,fill=1,stroke=0,fillMode=_FNZ)
def draw_icon_c(cx,cy,size,color):
    if not ICON_D: return
    sc=size/8.02; T=lambda x,y:(cx+(x-4.011)*sc, cy-(y-7.734)*sc)
    p=c.beginPath(); _add_path(p,ICON_D,T); c.setFillColor(color); c.drawPath(p,fill=1,stroke=0,fillMode=_FNZ)

def page_bg(): c.setFillColor(IVORY); c.rect(0,0,PW,PH,fill=1,stroke=0)
def footer():
    c.setStrokeColor(LINE); c.setLineWidth(0.7); c.line(ML,60,PW-MR,60)
    draw_logo(ML,57,12,INK,SAGE)
    c.setFont("Sans",8); c.setFillColor(MUTED); c.drawRightString(PW-MR,48, f"{NAME}’s Strengths Profile  ·  {st['page']}")
def new_page(): c.showPage(); st["page"]+=1; page_bg(); footer(); st["y"]=TOP
def need(h):
    if st["y"]-h < BOTTOM: new_page()
def wrap(text,font,size,maxw):
    out=[]
    for pg in text.split("\n"):
        words=pg.split(" "); cur=""
        for w in words:
            t=(cur+" "+w).strip()
            if stringWidth(t,font,size)<=maxw: cur=t
            else:
                if cur: out.append(cur)
                cur=w
        out.append(cur)
    return out
def para(text,size=10.5,font="Sans",leading=15.5,color=INK,gap=11,x=ML,maxw=CW):
    for ln in wrap(text,font,size,maxw):
        need(leading); c.setFont(font,size); c.setFillColor(color); c.drawString(x, st["y"]-size, ln); st["y"]-=leading
    st["y"]-=gap
def kicker(text,color=SAGE,x=ML,gap=8):
    need(16); c.setFont("Sans-B",8.5); c.setFillColor(color); c.drawString(x, st["y"]-9, " ".join(text.upper())); st["y"]-=(14+gap)
def h1(text,size=23,gap=12):
    for ln in wrap(text,"Serif-B",size,CW):
        need(size+8); c.setFont("Serif-B",size); c.setFillColor(INK); c.drawString(ML, st["y"]-size, ln); st["y"]-=(size+5)
    st["y"]-=gap
def h2(text,size=13.5,color=INK,gap=8,top=6):
    st["y"]-=top; need(size+6); c.setFont("Serif-B",size); c.setFillColor(color); c.drawString(ML, st["y"]-size, text); st["y"]-=(size+gap)
def bullets(items,size=10.5,leading=15.5,gap_item=4,color=INK):
    for it in items:
        lines=wrap(it,"Sans",size,CW-16); need(leading*len(lines)+gap_item)
        c.setFillColor(SAGE); c.setFont("Sans-B",size); c.drawString(ML, st["y"]-size, "•")
        c.setFillColor(color); c.setFont("Sans",size)
        for ln in lines: c.drawString(ML+16, st["y"]-size, ln); st["y"]-=leading
        st["y"]-=gap_item
    st["y"]-=7
def card(title,body,fill=WHITE,stroke=LINE,pad=15,title_color=SAGE,icon=True):
    size=10.3; leading=15; tsize=11.5
    lines=wrap(body,"Sans",size,CW-2*pad); h=pad+tsize+9+leading*len(lines)+pad-3
    need(h+10); top=st["y"]
    c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(1); c.roundRect(ML, top-h, CW, h, 12, fill=1, stroke=1)
    yy=top-pad
    if icon: draw_icon_c(ML+pad+4, yy-6, 9, SAGE); tx=ML+pad+16
    else: tx=ML+pad
    c.setFont("Sans-B",tsize); c.setFillColor(title_color); c.drawString(tx, yy-tsize+1, title); yy-=(tsize+9)
    c.setFont("Sans",size); c.setFillColor(INK)
    for ln in lines: c.drawString(ML+pad, yy-size, ln); yy-=leading
    st["y"]=top-h-13
def rule(gap=8):
    st["y"]-=2; need(gap); c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(ML, st["y"], PW-MR, st["y"]); st["y"]-=(gap+6)
def quote(text):
    lines=wrap(text,"Serif-I",13,CW-40); h=len(lines)*20+22; need(h+6); top=st["y"]
    c.setFillColor(SOFT2); c.roundRect(ML, top-h, CW, h, 10, fill=1, stroke=0)
    c.setStrokeColor(SAGE); c.setLineWidth(3); c.line(ML+16, top-16, ML+16, top-h+16)
    yy=top-20; c.setFont("Serif-I",13); c.setFillColor(SAGED)
    for ln in lines: c.drawString(ML+32, yy-11, ln); yy-=20
    st["y"]=top-h-14

BLEND_META=[("The Maker","Builds to understand"),("The Thinker","Wants to know why"),
 ("The Explorer","Learns on the move"),("The Storyteller","Thinks in stories"),
 ("The Connector","Feels the room"),("The Leader","Sets the plan")]

def fmt(s):
    S=SUB[:1].upper()+SUB[1:]
    return s.format(N=NAME,s=SUB,S=S,p=POS,o=OBJ,noun=NOUN)

def cover(A):
    page_bg(); c.setFillColor(SAGED); c.rect(0, PH-300, PW, 300, fill=1, stroke=0)
    draw_icon_c(PW-92, PH-100, 92, HexColor("#33534A"))
    draw_logo(ML, PH-60, 19, HexColor("#F4F8F5"), HexColor("#F4F8F5"))
    c.setFont("Sans-B",9.5); c.setFillColor(HexColor("#9FC3B4")); c.drawString(ML, PH-140, "  ".join(list("STRENGTHS PROFILE")))
    c.setFont("Serif-B",54); c.setFillColor(WHITE); c.drawString(ML-2, PH-205, NAME)
    c.setFont("Sans",12); c.setFillColor(HexColor("#C7DBD0")); c.drawString(ML, PH-232, f"Prepared for {NAME}  ·  Age {AGE}  ·  {TODAY}")
    c.setFont("Sans-B",9.5); c.setFillColor(SAGE); c.drawString(ML, PH-360, "  ".join(list("SIGNATURE STRENGTH")))
    c.setFont("Serif-B",40); c.setFillColor(INK); c.drawString(ML-2, PH-408, "The "+NOUN)
    c.setFont("Serif-I",14); c.setFillColor(SAGE); c.drawString(ML, PH-432, A["tag"])
    yy=PH-470; c.setFont("Sans",11); c.setFillColor(INK)
    intro=fmt("This profile is a warm, practical portrait of how {N} naturally thinks, plays, and connects — built from your answers and grounded in strengths-based child development. It’s a lens for seeing {o} more clearly, not a label or a test score.")
    for ln in wrap(intro,"Sans",11,CW-6): c.drawString(ML, yy, ln); yy-=17
    c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(ML, 92, PW-MR, 92)
    c.setFont("Sans",8.5); c.setFillColor(MUTED)
    c.drawString(ML, 78, "A guidance & enrichment profile for parents."); c.drawRightString(PW-MR, 78, "Their Spark")

def blend_page(A):
    new_page(); kicker(fmt("{N}’s full blend"))
    h1(fmt("No child is one note. Here’s {N}’s whole chord."))
    para(fmt("Every child carries all six strengths in different measures. {N}’s answers lean most toward The {noun}, and the strengths just beneath it shape how that plays out day to day. This mix is what makes {p} particular — two children who share a signature strength are never quite the same."))
    st["y"]-=4
    sig="The "+NOUN
    order=sorted(BLEND_META, key=lambda m:-A["blend"][m[0]])
    barx=ML+150; barw=CW-150-40
    for label,desc in order:
        val=A["blend"][label]; hi=(label==sig); need(34)
        c.setFont("Serif-B",11); c.setFillColor(INK if hi else HexColor("#4A5560")); c.drawString(ML, st["y"]-11, label)
        c.setFont("Sans",8.3); c.setFillColor(MUTED); c.drawString(ML, st["y"]-22, desc)
        yb=st["y"]-13
        c.setFillColor(SOFT); c.roundRect(barx, yb-4, barw, 9, 4.5, fill=1, stroke=0)
        c.setFillColor(SAGE if hi else HexColor("#9DBCB0")); c.roundRect(barx, yb-4, barw*val, 9, 4.5, fill=1, stroke=0)
        st["y"]-=34
    st["y"]-=2
    para(fmt(A["blend_note"]), gap=6)
    card("Why the mix matters", fmt(A["mix_card"]), fill=CREAM, stroke=CREAM)

def render(key):
    global c, st, NAME, SUB, POS, OBJ, AGE, NOUN
    A=CONTENT[key]; NAME,SUB,POS,OBJ,AGE=A["child"]; NOUN=A["noun"]
    art="an" if NOUN[0] in "AEIOU" else "a"
    fn=f"theirspark-{key}-sample.pdf"
    c=canvas.Canvas(fn, pagesize=A4); st={"y":TOP,"page":1}
    cover(A)
    # note
    new_page(); kicker("A note before you begin")
    h1(fmt("Every child is a whole world. This is one clear window into {N}’s."))
    para(fmt("You know {N} better than any quiz ever could. What a profile like this can do is give language to things you may already sense — and a few you haven’t noticed yet — so you can nurture them on purpose."))
    para(fmt("We looked at how {N} plays, solves problems, handles frustration, and connects with others. Across every answer, one pattern came through more strongly than the rest. We call it {N}’s signature strength, and for {N} it is The {noun}."))
    para(fmt("A signature strength isn’t the whole story — no child is only one thing, and you’ll see {N}’s full blend a few pages in. Think of it as {p} default setting: the mode {s} returns to when {s} is free to be {o}self."))
    quote(fmt("Read this with {N} in mind, not against a standard. The goal isn’t to fix anything — it’s to help {p} become more fully who {s} already is."))
    para(fmt("Here’s how to use it: skim it once for the shape of things, then come back to the two sections most parents dog-ear — “Nurturing the {noun} at home” and “Try this week.” Small, steady changes there do more than any single grand gesture."))
    # signature
    new_page(); kicker("Signature strength"); h1(fmt(A["h1_line"]))
    for p in A["portrait"]: para(fmt(p))
    h2(fmt("How it shows up in {N}"), color=SAGE)
    bullets([fmt(x) for x in A["shows"]])
    card("At a glance", fmt(A["glance"]), fill=SOFT, stroke=SOFT)
    quote(fmt(A["q1"]))
    # blend
    blend_page(A)
    # thinks/feels/connects
    new_page(); kicker(fmt("Inside {N}’s world")); h1(fmt("How {N} thinks, feels, and connects."))
    h2(fmt("How {s} thinks"), color=SAGE, top=2); para(fmt(A["thinks"]))
    h2(fmt("How {s} feels")); para(fmt(A["feels"]))
    h2(fmt("How {s} connects")); para(fmt(A["connects"]))
    quote(fmt(A["tfc_q"]))
    # nurture
    new_page(); kicker(fmt("Nurturing the {noun} — at home")); h1(fmt("Small changes that help {N} thrive."))
    para(fmt(A["nurture_intro"]))
    for t,b in A["nurture_cards"]: card(fmt(t), fmt(b))
    h2("Gently avoid", color=SAGED); bullets([fmt(x) for x in A["avoid"]])
    # thrives
    new_page(); kicker(fmt("Where {N} thrives")); h1(f"Activities and spaces built for {art} {NOUN}.")
    para(fmt(A["thrives_intro"]))
    for i,(ht,items) in enumerate(A["thrives"]):
        h2(fmt(ht), color=SAGE, top=(2 if i==0 else 6)); bullets([fmt(x) for x in items])
    card(A["screens"][0], fmt(A["screens"][1]), fill=SOFT, stroke=SOFT)
    # struggles
    new_page(); kicker(f"When the {NOUN} hits a wall"); h1(fmt("Supporting {N} through the hard moments."))
    para(fmt(A["str_intro"]))
    h2("What it can look like", color=SAGE, top=2); bullets([fmt(x) for x in A["str_look"]])
    h2("How to help in the moment"); bullets([fmt(x) for x in A["str_help"]])
    card("Phrases that land", fmt(A["phrases"]), fill=CREAM, stroke=CREAM)
    # grows
    new_page(); kicker("Where this can lead"); h1(f"The {NOUN}, grown up.")
    for p in A["grows"]: para(fmt(p))
    card("The trait under the trait", fmt(A["trait"]), fill=SOFT, stroke=SOFT)
    quote(fmt(A["grows_q"]))
    # this week
    new_page(); kicker(fmt("Try this week with {N}")); h1("Five small things to try in the next seven days.")
    h2("Conversation starters", color=SAGE, top=2); bullets([fmt(x) for x in A["convo"]])
    h2("Affirmations to say out loud"); bullets([fmt(x) for x in A["affirm"]])
    card("One 10-minute experiment", fmt(A["experiment"]), fill=CREAM, stroke=CREAM)
    # closing
    new_page(); kicker("One last thing"); h1("Keep looking for the spark.")
    para(fmt("A profile is a snapshot; {N} is a movie. {S} will grow, surprise you, and shift. What won’t change is the value of a parent who sees {o} clearly and nurtures what’s already there. You’re already doing that — you read to the end."))
    para("If this was useful, a few gentle next steps can help you turn insight into everyday habit:")
    bullets([fmt("The Nurture Plan — a 30-day, strengths-matched roadmap of tiny daily moves for {N}."),
             fmt("Spark Club — fresh activities matched to {N} each month, and a re-assessment as {s} grows."),
             fmt("A sibling profile — see how {N}’s strengths compare with a brother or sister’s.")])
    st["y"]-=6; rule()
    c.setFont("Sans",8.5); c.setFillColor(MUTED)
    disc=("Their Spark is a guidance and enrichment tool for parents. It is not a diagnostic, medical, or "
          "psychological assessment, and it is not a substitute for professional advice. Every child is unique; "
          "use this profile as a lens, always alongside your own knowledge of your child.")
    for ln in wrap(disc,"Sans",8.5,CW): c.drawString(ML, st["y"]-9, ln); st["y"]-=12
    footer(); c.save(); return fn, st["page"]

# ============================ CONTENT ============================
CONTENT = {}

CONTENT["Storyteller"] = {
 "child": ("Ava","she","her","her","5"),
 "noun": "Storyteller", "tag": "Imaginative & expressive",
 "h1_line": "{N} is a Storyteller.",
 "portrait": [
  "Storytellers make sense of the world by narrating it. Where another child sees a stick, {N} sees a wand, a fishing rod, or a brave knight’s sword. For {N}, imagination isn’t a break from real life — it’s how {s} processes it. Play, pretend, and language are {p} thinking made visible.",
  "This is the strength of the writer, the performer, the designer and the teacher — anyone who moves people with an image or an idea. It shows up early as elaborate make-believe, a love of books and songs, running commentary, and characters who follow {o} from room to room. Underneath the whimsy is real cognitive work: {s} is learning to hold ideas, feelings, and possibilities in mind and give them shape.",
 ],
 "shows": [
  "{N} narrates as {s} plays — {p} toys have names, voices, histories, and feelings.",
  "{S} reaches for metaphor and ‘what if,’ turning ordinary moments into little stories.",
  "Books, songs, drawing, and dress-up hold {p} attention longer than most toys.",
  "{S} often works out big feelings by acting them out or telling them as a story.",
 ],
 "glance": "Learns best by: story, imagery, and imaginative play.   Energized by: an audience and room to pretend.   Needs: unstructured time and open-ended props.   Watch for: big feelings that arrive as vividly as {p} ideas.",
 "q1": "A Storyteller isn’t ‘off in a dream world.’ {S}’s rehearsing empathy, language, and possibility — the deep tools of a creative life.",
 "blend": {"The Storyteller":0.95,"The Connector":0.62,"The Maker":0.50,"The Thinker":0.38,"The Explorer":0.30,"The Leader":0.24},
 "blend_note": "{N}’s Storyteller strength is coloured by a warm Connector streak: {s} tells stories to reach people, not just to entertain {o}self. And a solid Maker thread means {s} loves to build the worlds {s} invents. Feed the imagination and the words, and {N} lights up.",
 "mix_card": "Strengths don’t work alone. The best moments for {N} tend to braid two or three together — inventing a character (Storyteller) who feels real (Connector) and then building it a house from a cardboard box (Maker).",
 "thinks": "{N} thinks in scenes and stories. A bare fact is hard for {o} to hold, but wrap it in a character or a ‘what if’ and it sticks instantly. {S} reasons by imagining: what would happen if…? how would they feel? This narrative thinking is the root of both creativity and empathy — {s} is constantly running little simulations of the world.",
 "feels": "{N}’s feelings are vivid and close to the surface, and they often arrive in story form — a bad day becomes an epic, a small worry becomes a monster under the bed. This isn’t drama for its own sake; it’s how {s} makes feelings manageable. When you enter the story with {o} rather than correcting it, {s} feels understood.",
 "connects": "{N} connects through imagination and words — inviting others into {p} worlds, giving them roles, telling them how the story goes. ‘You be the dragon’ is {p} way of saying ‘I want to be close to you.’ {S} also reads the emotional weather of a room early, which makes {o} a tender, perceptive friend.",
 "tfc_q": "If you want a window into {N}’s heart, don’t ask {o} to explain how {s} feels. Ask {o} to tell you a story about it.",
 "nurture_intro": "Storytellers need three simple things: raw material for the imagination, an audience who takes their worlds seriously, and language — lots of it, poured in and drawn out.",
 "nurture_cards": [
  ("Try this: become a character", "When {N} is building a world, don’t just watch — ask to join it. ‘What’s my name? What do I do here?’ Taking a role tells {o} that {p} inner world is worth entering, and it stretches {p} storytelling by adding a second mind."),
  ("Try this: capture the stories", "Now and then, write down {N}’s inventions word-for-word, or let {o} ‘dictate’ a story to you. Seeing {p} ideas become a real, keepable thing is powerful — and it quietly builds the bridge from talking to writing."),
  ("Try this: read wide, then wonder", "Read a notch above {p} level and pause to wonder together: ‘What do you think happens next? Why did she do that?’ You’re feeding vocabulary and, just as importantly, teaching {o} that stories are places to think."),
 ],
 "avoid": [
  "Rushing to correct ‘that’s not real’ — the pretend is where the learning lives; you can hold truth and imagination at once.",
  "Over-scheduling every hour. Storytellers need boredom and blank time; that’s when the best worlds get built.",
  "Treating big, dramatic feelings as misbehaviour. Enter the story first, then guide it.",
 ],
 "thrives_intro": "These aren’t a curriculum — just well-matched starting points. Follow {N}’s lead and notice which ones make {o} lose track of time. That’s your signal.",
 "thrives": [
  ("Imaginative play", ["Open-ended props over single-purpose toys — scarves, boxes, figurines, a dress-up bin.","Small-world play: dollhouses, animal figures, tiny scenes {s} can direct.","Puppets and a simple ‘stage’ — a doorway, a sofa-back, a torch on the wall."]),
  ("Words & story", ["A huge, rotating stack of picture books and, soon, chapter books read aloud.","Making tiny books: fold paper, {s} dictates or scribbles, you staple it.","Songs, rhymes, and silly wordplay — the raw musculature of language."]),
  ("Expression & performance", ["Drawing and painting as storytelling, not just decoration.","Dress-up, skits, and ‘shows’ for a patient family audience.","Simple drama or music-and-movement classes, if {s} enjoys a stage."]),
 ],
 "screens": ("A note on screens", "Storytellers thrive with creation over consumption: stop-motion apps, drawing tools, audiobooks and story podcasts, simple ‘make your own tale’ games. The test: does {N} come away having made or imagined something — or only watched?"),
 "str_intro": "Every strength has a shadow side. For Storytellers, the imagination that is such a gift can also amplify worry, blur the line with reality, or make leaving a beloved world genuinely painful. Knowing the pattern helps you meet it gently.",
 "str_look": [
  "Fears and worries that feel very real and very big (the vivid mind cuts both ways).",
  "Difficulty stopping a game or story — leaving the world can feel like a small loss.",
  "Getting ‘lost’ in pretend when it’s time to focus on something concrete.",
 ],
 "str_help": [
  "Meet the feeling inside its story: ‘That monster sounds scary — shall we find out what he’s afraid of?’ You calm the fear without dismissing it.",
  "Give worlds a soft landing: ‘Let’s find a good pausing place — we can pick up the story after lunch.’",
  "Use {p} own strength to redirect: turn the boring task into a quick narrative (‘these blocks are commuters trying to get home’).",
 ],
 "phrases": "Instead of ‘It’s not real, stop worrying’ try ‘Let’s tell that worry a different ending.’ Instead of ‘Stop playing and come now’ try ‘Time to pause the story — where’s a good spot to leave it?’ You’re honouring {p} world while guiding {o} out of it.",
 "grows": [
  "It’s early, and the point is never to script {N}’s future at five. But it helps to know the deeper trait you’re nurturing: imagination — the ability to picture what isn’t yet, and to move others with it. Children who keep it alive tend to become adults who create, communicate, and lead with vision.",
  "The Storyteller strength is the common root under writers and directors, designers and marketers, teachers, therapists, and founders with a compelling ‘why.’ What unites them isn’t a job — it’s the power to turn ideas and feelings into a story other people want to step inside.",
 ],
 "trait": "If you protect one thing, protect {N}’s belief that {p} inner world matters and is worth sharing. Storytellers learn this every time an adult stops, listens, and steps into the world they’ve built. That belief becomes the confidence to speak up, create, and move people for the rest of {p} life.",
 "grows_q": "You’re not raising a future job title. You’re raising a child who can imagine a better story — and bring other people into it.",
 "convo": [
  "‘Tell me a story where you’re the hero. What happens?’",
  "‘If your favourite toy could talk, what would it say about today?’",
  "‘What do you think happens next in that book — and why?’",
  "‘Can we make up a story together? You start, I’ll add the next part.’",
  "‘If this feeling were a character, what would it look like?’",
 ],
 "affirm": [
  "‘You have the most wonderful imagination.’",
  "‘I love the worlds you make.’",
  "‘Your stories help me understand you.’",
 ],
 "experiment": "Give {N} three unrelated objects (a spoon, a scarf, a toy car) and one prompt: ‘These three are about to go on an adventure — tell me what happens.’ Don’t steer; just listen and ask ‘and then?’ You’ll see the Storyteller light up — and learn a surprising amount about what’s on {p} mind.",
}

CONTENT["Connector"] = {
 "child": ("Noah","he","his","him","7"),
 "noun": "Connector", "tag": "Warm, social & empathetic",
 "h1_line": "{N} is a Connector.",
 "portrait": [
  "Connectors understand the world through people. Before {N} can settle into a room, {s} reads it — who’s happy, who’s left out, who needs a friend. For {N}, feelings are as real and as interesting as facts, and relationships are where {s} does {p} deepest thinking. Warmth isn’t a nicety for {o}; it’s {p} native language.",
  "This is the strength of the teacher, the nurse, the coach and the peacemaker — anyone who builds trust and brings people together. It shows up early as empathy that seems almost too big for {p} age, a radar for others’ moods, and real distress when someone is hurt or excluded. Underneath the sweetness is serious skill: {s} is learning to read, name, and move human emotion.",
 ],
 "shows": [
  "{N} notices when a friend is sad or left out — often before the adults do.",
  "{S} is happiest around people, and can wilt with too much time alone.",
  "{S} remembers the emotional details: who was kind, who was upset, who made up.",
  "{S} soothes, includes, and smooths things over — a natural peacemaker.",
 ],
 "glance": "Learns best by: talking, sharing, and doing things with others.   Energized by: connection, belonging, and being needed.   Needs: warmth, one-on-one time, and help with limits.   Watch for: absorbing others’ feelings and losing track of {p} own.",
 "q1": "A Connector isn’t just ‘sweet.’ {S}’s building emotional intelligence — the quiet superpower behind every strong relationship and team {s}’ll ever be part of.",
 "blend": {"The Connector":0.95,"The Storyteller":0.60,"The Leader":0.50,"The Thinker":0.36,"The Explorer":0.30,"The Maker":0.24},
 "blend_note": "{N}’s Connector strength is lifted by a Storyteller streak — {s} reaches people through words and imagination — and a real flair for leadership, gathering others toward a shared idea. Keep {o} connected and included, and {N} flourishes.",
 "mix_card": "Strengths work together. {N} shines brightest when connection meets purpose — rallying friends (Connector) around a game {s} invents (Storyteller) and gently steers (Leader). Look for activities that let {o} belong and contribute at once.",
 "thinks": "{N} thinks out loud and thinks with others. Ideas get clearer for {o} in conversation, and {s} often understands a situation through how people feel about it rather than its bare mechanics. This social reasoning is real intelligence — {s} is mapping motives, relationships, and consequences, the exact skills that make collaboration and leadership possible.",
 "feels": "{N} feels deeply and, crucially, feels others’ feelings too. This empathy is a gift, but it can flood {o}: a friend’s bad day can become {p} bad day. Part of your job is to help {o} tell the difference between caring about a feeling and carrying it. Naming that out loud — ‘that’s her sadness, and you’re being kind to it’ — is a lifelong skill.",
 "connects": "Connecting is {p} whole mode — {s} bonds through talking, sharing, helping, and simply being together. Belonging matters enormously to {o}, which makes {o} loyal and generous, and also more sensitive than most to exclusion. Being trusted with a small responsibility (‘can you look after the new kid?’) lights {o} up.",
 "tfc_q": "If you want a window into {N}’s heart, ask about {p} friends. You’ll learn what {s}’s feeling by hearing who {s}’s thinking about.",
 "nurture_intro": "Connectors need three simple things: warm, unhurried connection; chances to help and belong; and gentle coaching in where they end and other people begin.",
 "nurture_cards": [
  ("Try this: name feelings out loud", "Narrate the emotional world together — yours, {p}, characters’ in books: ‘He looks frustrated. What do you think he needs?’ You’re giving {N} a rich vocabulary for the thing {s} already senses, which turns raw empathy into real skill."),
  ("Try this: give a real job", "Connectors thrive on being needed. Offer genuine responsibility scaled to {p} age — setting the table ‘because the family counts on you,’ welcoming a guest, checking on a younger sibling. Contribution is how {s} feels {p} worth."),
  ("Try this: protect a solo refill", "Because {s} pours out so much, teach {o} to refill. Build in gentle alone-time and name it kindly: ‘Even really loving people need quiet time to fill back up.’ You’re preventing the burnout that sensitive kids can drift into."),
 ],
 "avoid": [
  "Dismissing social hurts as ‘no big deal’ — to a Connector, a fractured friendship is a big deal.",
  "Overloading {o} as the family’s emotional helper; {s} needs to be cared for, not only caring.",
  "Assuming {s}’s fine because {s}’s smiling. Check in on the feelings under the helpfulness.",
 ],
 "thrives_intro": "These aren’t a curriculum — just well-matched starting points. Follow {N}’s lead and notice which ones make {o} light up. That’s your signal.",
 "thrives": [
  ("With others", ["Playdates, small groups, team games — connection is {p} favourite material.","Caring roles: helping with a pet, a plant, a baby cousin, a classmate.","Cooperative games and projects over winner-takes-all competition."]),
  ("Feelings & story", ["Books and shows about friendship and feelings — then talking them over.","Role-play that works out social situations: shops, doctors, school.","Simple ‘how are you’ rituals at bedtime to name the day’s emotions."]),
  ("Belonging & contribution", ["Family jobs framed as helping the people {s} loves.","Clubs, teams, or classes with a warm, familiar group.","Small acts of kindness {s} can lead — a card, a welcome, a share."]),
 ],
 "screens": ("A note on screens", "Connectors do best with screens that involve people, not replace them: video calls with family, co-op games played side-by-side, shows watched and discussed together. The test: does the screen bring {N} closer to people, or pull {o} away from them?"),
 "str_intro": "Every strength has a shadow side. For Connectors, the openness that makes {o} so warm can also make {o} a sponge — soaking up others’ moods, over-giving, and struggling when relationships wobble or {s} feels left out. Knowing the pattern helps you steady {o}.",
 "str_look": [
  "Big reactions to social pain — being excluded, a friend’s anger, a fallout.",
  "Losing {p} own preferences to keep everyone else happy (the little peacemaker).",
  "Coming home ‘flooded’ after busy social days, tired and tearful.",
 ],
 "str_help": [
  "Separate caring from carrying: ‘You can feel sad for her and still have your own good day.’",
  "Coach small, kind honesty: ‘It’s okay to want something different — let’s practise saying it.’",
  "Give a decompression ritual after big days: quiet, a snack, a cuddle, low light.",
 ],
 "phrases": "Instead of ‘Don’t be so sensitive’ try ‘You feel things deeply — that’s a strength; let’s help you carry it.’ Instead of ‘Just share and be nice’ try ‘You can be kind and still say what you need.’ You’re teaching {N} that empathy and self-respect belong together.",
 "grows": [
  "It’s early, and the point is never to plan {N}’s future at seven. But it helps to know the deeper trait you’re nurturing: emotional intelligence — the ability to read people, build trust, and bring them together. Children who keep it grow into adults others instinctively follow and confide in.",
  "The Connector strength is the common root under teachers and therapists, nurses and doctors, coaches, community and team leaders, and founders who build great cultures. What unites them isn’t a job — it’s the rare gift of making other people feel seen, safe, and part of something.",
 ],
 "trait": "If you protect one thing, protect {N}’s belief that {p} sensitivity is a strength, not a weakness to toughen out of. Connectors hear the opposite message a lot. Every time you honour {p} empathy while helping {o} set a kind boundary, you’re raising an adult who can care deeply without losing {o}self.",
 "grows_q": "You’re not raising a future job title. You’re raising a child who makes other people feel less alone — and that changes every room {s} ever walks into.",
 "convo": [
  "‘Who did you play with today? How were they feeling?’",
  "‘Was anyone left out? What did you do?’",
  "‘What’s something kind someone did for you — and something kind you did?’",
  "‘If your friend were sad, what would you say to help?’",
  "‘What do you need right now — a talk, a hug, or some quiet?’",
 ],
 "affirm": [
  "‘You have such a kind, noticing heart.’",
  "‘People feel safe with you.’",
  "‘Your feelings are welcome here.’",
 ],
 "experiment": "Read a short story together and pause at a tricky moment: ‘How do you think she feels? What could someone do to help?’ Then flip it: ‘Has that ever happened to you?’ You’ll watch the Connector come alive — and learn who and what is on {p} heart right now.",
}

CONTENT["Thinker"] = {
 "child": ("Sofia","she","her","her","8"),
 "noun": "Thinker", "tag": "Curious & analytical",
 "h1_line": "{N} is a Thinker.",
 "portrait": [
  "Thinkers meet the world with a question. Where another child accepts ‘because that’s how it is,’ {N} wants the reason underneath — and the reason under that. For {N}, curiosity isn’t restlessness; it’s how {s} builds a map of how things truly work. A good puzzle can hold {o} the way a story holds other kids.",
  "This is the strength of the scientist, the analyst, the detective and the philosopher — anyone who follows a question to the truth. It shows up early as relentless ‘why?’, a love of patterns and categories, and deep, quiet focus when something genuinely interests {o}. Underneath the questions is real rigour: {s} is learning to reason, test, and think for {o}self.",
 ],
 "shows": [
  "{N} asks ‘why’ and ‘how’ about everything — and isn’t satisfied with a hand-wave.",
  "{S} loves to sort, order, compare, and find the pattern or the rule.",
  "Given a puzzle, {s} will stay with it — {p} focus can be remarkable.",
  "{S} notices inconsistencies and fairness gaps others miss (‘but that’s not logical’).",
 ],
 "glance": "Learns best by: questions, patterns, and figuring it out {o}self.   Energized by: a real puzzle and time to think.   Needs: honest answers and room to go deep.   Watch for: over-thinking, or frustration when the world isn’t logical.",
 "q1": "A Thinker isn’t ‘too much’ with the questions. {S}’s building the engine of independent thought — the ability to reason, doubt, and understand for {o}self.",
 "blend": {"The Thinker":0.95,"The Maker":0.60,"The Explorer":0.50,"The Storyteller":0.34,"The Leader":0.30,"The Connector":0.26},
 "blend_note": "{N}’s Thinker strength is amplified by a Maker streak — {s} likes to test ideas by building them — and an Explorer thread that sends {p} curiosity out into the world. Give {o} real questions and time to chase them, and {N} flourishes.",
 "mix_card": "Strengths work together. {N} is at {p} best when a question meets {p} hands and feet — investigating how something works (Thinker) by taking it apart (Maker) out in the world (Explorer). Aim for activities that let {o} wonder and do.",
 "thinks": "{N} thinks carefully and systematically. {S} wants the mechanism, the pattern, the rule — and {s} will hold a question in mind long after other kids have moved on. This is deep, disciplined cognition: {s}’s learning to break problems apart, spot what doesn’t fit, and reason toward an answer rather than guessing. It can look like stubbornness; it’s usually thoroughness.",
 "feels": "{N}’s feelings can run quieter and more inward than other kids’, and {s} often tries to reason with them — to understand a feeling before {s}’ll express it. {S} also feels unfairness and illogic keenly; a broken rule or a contradiction genuinely bothers {o}. Naming feelings simply and without pressure (‘you seem frustrated — want to think it through?’) respects how {s}’s wired.",
 "connects": "{N} often connects through shared interest — {s} bonds with people who’ll explore a question with {o}, and can find small talk baffling. {S} may observe before joining, sizing up the situation first. This isn’t coldness; it’s how {s} feels safe. A friend who’ll wonder alongside {o} is worth more to {o} than a dozen playground acquaintances.",
 "tfc_q": "If you want a window into {N}’s heart, don’t rush {o} to talk about feelings. Hand {o} a real question and think it through together — the closeness comes with the curiosity.",
 "nurture_intro": "Thinkers need three simple things: honest answers, hard-enough problems, and the patience to let them arrive at understanding on their own.",
 "nurture_cards": [
  ("Try this: honour the question", "When {N} asks ‘why,’ resist the tidy final answer. Try ‘What do you think?’ or ‘How could we find out?’ You’re teaching {o} that {p} own mind is a tool for answering questions — the single most important thing a Thinker can learn."),
  ("Try this: feed a deep dive", "When {s} latches onto a topic — space, bugs, volcanoes, how the body works — go deep with {o}: library books, a documentary, a real expert if you can. Depth over breadth suits {p} mind and teaches {o} the joy of mastering something."),
  ("Try this: let the answer be earned", "Resist solving {p} puzzle the moment {s} stalls. A little productive struggle — ‘you’re close; what have you tried?’ — is where a Thinker’s confidence is forged. The goal isn’t the finished puzzle; it’s the felt sense of ‘I worked it out.’"),
 ],
 "avoid": [
  "Fobbing off questions with ‘just because.’ To a Thinker it reads as ‘your curiosity doesn’t matter.’",
  "Rushing in with the answer; the struggle is the learning.",
  "Dismissing {p} need for logic and fairness as ‘being difficult’ — it’s how {s}’s built.",
 ],
 "thrives_intro": "These aren’t a curriculum — just well-matched starting points. Follow {N}’s lead and notice which ones make {o} lose track of time. That’s your signal.",
 "thrives": [
  ("Puzzles & systems", ["Logic puzzles, mazes, strategy games, jigsaws, sorting and pattern toys.","Building sets with real cause-and-effect (marble runs, circuits, gears).","Collections to organise and classify — rocks, cards, bugs, facts."]),
  ("Investigation", ["Simple kitchen and garden science — hypotheses, tests, ‘what if we change this?’","Taking safe things apart to see the mechanism inside.","‘How does it work?’ books and documentaries on {p} current obsession."]),
  ("Deep dives", ["Library trips that follow the question of the week.","Museums with real depth — science, natural history, discovery centres.","A grown-up who’ll take {p} questions seriously and think out loud with {o}."]),
 ],
 "screens": ("A note on screens", "Thinkers can genuinely benefit from the right screens: quality science content, simple coding and logic games, well-made explainers on {p} obsessions. The test: is {N} following a question and building understanding — or just being fed a stream to watch passively?"),
 "str_intro": "Every strength has a shadow side. For Thinkers, the mind that loves to reason can also over-think, get stuck on fairness and ‘right,’ and grow frustrated when people or the world refuse to be logical. Knowing the pattern helps you steady {o}.",
 "str_look": [
  "Over-thinking or worrying a problem in circles, struggling to let it go.",
  "Frustration or rigidity when a rule seems unfair or a plan changes without reason.",
  "Perfectionism — reluctance to try until {s}’s sure {s}’ll get it ‘right.’",
 ],
 "str_help": [
  "Give the worry somewhere to go: ‘Let’s write down the question and decide when we’ll think about it.’",
  "Explain the reason behind changes; a Thinker cooperates with logic far better than with ‘because I said so.’",
  "Reframe mistakes as data: ‘That didn’t work — now we know something. What does it tell us?’",
 ],
 "phrases": "Instead of ‘Stop overthinking it’ try ‘Your brain’s working hard — let’s give that question a rest and come back.’ Instead of ‘Because I said so’ try ‘Here’s the reason, and here’s the bit we can’t change.’ You’re honouring {p} logic while helping {o} hold uncertainty.",
 "grows": [
  "It’s early, and the point is never to pick {N}’s career at eight. But it helps to know the deeper trait you’re nurturing: independent thinking — the confidence and skill to reason toward the truth rather than just take it on trust. Children who keep it become adults who solve, question, and understand.",
  "The Thinker strength is the common root under scientists and engineers, analysts and researchers, doctors, lawyers, detectives, and founders who see the pattern first. What unites them isn’t a job — it’s a lifelong habit of asking ‘why,’ testing the answer, and thinking for themselves.",
 ],
 "trait": "If you protect one thing, protect {N}’s trust in {p} own mind. Thinkers can be made to feel ‘too much,’ too questioning, too slow to just accept. Every time you take a question seriously and let {o} reason it out, you’re building the quiet intellectual confidence that outlasts any single fact {s}’ll ever memorise.",
 "grows_q": "You’re not raising a future job title. You’re raising a child who thinks for {o}self — and that’s the one skill no one can ever take away.",
 "convo": [
  "‘That’s a great question — what do you think the answer is?’",
  "‘How could we find out for sure?’",
  "‘What’s something you figured out today that surprised you?’",
  "‘What doesn’t make sense to you right now? Let’s think about it.’",
  "‘If you could learn everything about one thing, what would it be?’",
 ],
 "affirm": [
  "‘You ask the best questions.’",
  "‘I love how your mind works.’",
  "‘Not knowing yet is the fun part.’",
 ],
 "experiment": "Pose a real puzzle with no obvious answer: ‘Why do you think the moon seems to follow the car?’ or ‘How could we keep this ice cube from melting the longest?’ Don’t give the answer — ask ‘what’s your theory?’ and test it together. You’ll see the Thinker light up, and learn how {s} reasons.",
}

CONTENT["Leader"] = {
 "child": ("Diego","he","his","him","6"),
 "noun": "Leader", "tag": "Confident & organizing",
 "h1_line": "{N} is a Leader.",
 "portrait": [
  "Leaders meet the world with a plan and a pull that others follow. Where another child waits to be told, {N} decides — where to go, what the rules are, who does what. For {N}, taking charge isn’t bossiness; it’s a natural sense that things can be organised and made to happen, and a comfort with being the one to start.",
  "This is the strength of the captain, the founder, the director and the organiser — anyone who sets a direction and brings people with them. It shows up early as strong opinions, a love of being ‘in charge’ of the game, a sharp eye for what’s fair, and real drive to reach a goal. Underneath the confidence is something valuable: {s} is learning agency, responsibility, and how to move a group.",
 ],
 "shows": [
  "{N} naturally takes charge — inventing the game, setting the rules, assigning the roles.",
  "{S} has strong opinions and a clear sense of how things ‘should’ go.",
  "{S} is goal-driven — {s} likes a target, a plan, and the satisfaction of finishing.",
  "{S} cares intensely about fairness, and will argue the point when a rule seems wrong.",
 ],
 "glance": "Learns best by: leading, deciding, and owning a real goal.   Energized by: responsibility, challenge, and a clear win.   Needs: appropriate power, firm limits, and coaching in empathy.   Watch for: bossiness, and big feelings when {s}’s not in control.",
 "q1": "A Leader isn’t just ‘bossy.’ {S}’s rehearsing agency and initiative — the drive to decide, organise, and make things happen that the world desperately needs in adults.",
 "blend": {"The Leader":0.95,"The Connector":0.60,"The Explorer":0.52,"The Thinker":0.40,"The Maker":0.30,"The Storyteller":0.24},
 "blend_note": "{N}’s Leader strength is warmed by a Connector streak — {s} leads best when {s}’s also caring for the group — and an Explorer thread that gives {p} plans energy and daring. Give {o} real, age-sized responsibility, and {N} flourishes.",
 "mix_card": "Strengths work together. {N} is at {p} best when leadership serves people — rallying friends (Leader) toward an adventure (Explorer) while making sure everyone’s included (Connector). Look for chances to lead something that helps others.",
 "thinks": "{N} thinks in goals and plans. {S} sizes up a situation quickly, forms an opinion, and wants to act — {s}’d rather decide and adjust than wait and wonder. This is executive thinking: prioritising, organising people and steps, and holding a goal in mind. It can look like impatience; it’s usually a mind already three moves ahead.",
 "feels": "{N}’s feelings run strong and often attach to control and fairness — real frustration when {s}’s overruled, when a plan collapses, or when something is unjust. These big reactions aren’t defiance for its own sake; they’re the flip side of caring deeply about how things go. Helping {o} feel the feeling without needing to win is one of the great gifts you can give a young Leader.",
 "connects": "{N} connects by organising and including — {s} bonds through shared projects and by giving people a role in {p} plan. {S} can be a fierce, loyal friend and a natural captain, but the same drive can tip into controlling. The skill {s}’s learning — and needs your help with — is leading with people rather than over them.",
 "tfc_q": "If you want a window into {N}’s heart, put {o} in charge of something small and real. You’ll see {p} character in how {s} treats the people {s}’s leading.",
 "nurture_intro": "Leaders need three simple things: real responsibility to grow into, firm and fair limits to push against, and gentle coaching in the empathy that turns a boss into a leader.",
 "nurture_cards": [
  ("Try this: give real ownership", "Hand {N} genuine, age-sized authority — plan the family walk, be in charge of the weekend job, lead the game. Real responsibility feeds {p} drive and teaches {o} that leadership is service, not just control."),
  ("Try this: coach the other side", "When {s} steamrolls, pause and turn {o} toward the group: ‘You’re a strong leader — and a great leader checks: does everyone else want to play it this way?’ You’re adding empathy to initiative, which is the whole game."),
  ("Try this: hold firm, fair limits", "Leaders need to feel the edges. Keep your limits calm, consistent, and reasoned — {s}’ll push, and the steadiness teaches {o} that not being in charge of everything is safe and survivable."),
 ],
 "avoid": [
  "Crushing the drive with constant ‘stop being bossy’ — redirect it instead; the initiative is gold.",
  "Winning every power struggle by force; give real choices so {s} can practise leading well.",
  "Ignoring the fairness radar — when {s} cries ‘unfair,’ there’s often a real point worth hearing.",
 ],
 "thrives_intro": "These aren’t a curriculum — just well-matched starting points. Follow {N}’s lead and notice which ones let {o} lead well. That’s your signal.",
 "thrives": [
  ("Leading & organising", ["Games and projects {s} can plan and run (with a nudge toward including others).","Real jobs with ownership — captain of the tidy-up, keeper of the schedule.","Team sports and clubs where {s} can take initiative and learn to share the lead."]),
  ("Goals & challenge", ["Projects with a clear target and a satisfying finish.","Age-appropriate strategy games — planning, deciding, adjusting.","Stretch challenges that reward drive: ‘can you organise the whole thing?’"]),
  ("Fairness & responsibility", ["Roles that channel {p} justice streak — ‘fairness monitor,’ helper, mentor to a younger child.","Chances to make real decisions and live with the results.","Causes {s} can lead in a small way — a fundraiser, a family project."]),
 ],
 "screens": ("A note on screens", "Leaders do well with screens that involve strategy and building over passive watching: planning and management games, team play with real cooperation, creating rather than consuming. The test: is {N} deciding, organising, and leading — or just being led along by the feed?"),
 "str_intro": "Every strength has a shadow side. For Leaders, the drive that makes {o} capable can tip into control, and the strong will that helps {o} start things can make sharing power and losing genuinely hard. Knowing the pattern helps you meet it calmly.",
 "str_look": [
  "Bossiness — insisting on {p} way, struggling when friends want something else.",
  "Big meltdowns around losing, being overruled, or a plan that falls apart.",
  "Rigidity when {s}’s not in charge or the rules change without {p} say-so.",
 ],
 "str_help": [
  "Give controlled choices so {s} keeps some agency: ‘You can’t decide that, but you can decide this.’",
  "Name the feeling under the fight: ‘It’s hard when you’re not the one deciding — that’s real.’",
  "Coach repair, not just apology: ‘How could you lead that so your friend still wants to play?’",
 ],
 "phrases": "Instead of ‘Stop bossing everyone’ try ‘A great leader makes sure everyone gets a turn to choose.’ Instead of ‘You’re not in charge’ try ‘You’re not in charge of this one — here’s what you are in charge of.’ You’re keeping the drive and adding the wisdom.",
 "grows": [
  "It’s early, and the point is never to plan {N}’s future at six. But it helps to know the deeper trait you’re nurturing: agency — the confidence to take initiative, make decisions, and move things forward. Children who keep it, and learn to pair it with empathy, become the adults others are glad to follow.",
  "The Leader strength is the common root under founders and directors, captains and coaches, organisers, entrepreneurs, and anyone who starts things and rallies people to them. What unites them isn’t a title — it’s the willingness to decide, to own the outcome, and to bring a group toward a goal.",
 ],
 "trait": "If you protect one thing, protect {N}’s initiative — while steadily teaching {o} to use it for the group, not just over it. Leaders often hear only ‘stop being bossy,’ which can teach a capable child to shrink. Every time you redirect the drive instead of crushing it, you’re raising someone who leads with both strength and heart.",
 "grows_q": "You’re not raising a future job title. You’re raising a child who steps up and makes things happen — and who, with your coaching, brings people with {o}.",
 "convo": [
  "‘You’re in charge of this one — what’s your plan?’",
  "‘How did you make sure everyone got a turn today?’",
  "‘What’s a goal you want to reach this week? What’s step one?’",
  "‘What felt unfair today? What would you have done differently?’",
  "‘When is it great to lead — and when is it someone else’s turn?’",
 ],
 "affirm": [
  "‘You’re a strong, capable leader.’",
  "‘People trust you to take the lead.’",
  "‘A great leader takes care of everyone.’",
 ],
 "experiment": "Put {N} genuinely in charge of a small real task — planning tonight’s dessert, organising a family game, leading a clean-up ‘crew.’ Give {o} the authority, then watch: does {s} include people, adjust, share the win? You’ll see the Leader in action, and exactly where to coach next.",
}

CONTENT["Explorer"] = {
 "child": ("Kai","he","his","him","5"),
 "noun": "Explorer", "tag": "Active & adventurous",
 "h1_line": "{N} is an Explorer.",
 "portrait": [
  "Explorers learn with their whole body and their whole nerve. Where another child watches from the edge, {N} climbs in — moving, trying, testing what {s} and the world can do. For {N}, sitting still to learn feels backwards; {s} understands things by doing them, at speed, and often more than once. Energy isn’t a problem to manage; it’s {p} way of thinking.",
  "This is the strength of the athlete, the adventurer, the field scientist and the entrepreneur — anyone who learns by doing and isn’t afraid to try. It shows up early as constant motion, boldness (sometimes more than you’d like), a love of the outdoors, and a ‘let me try it myself’ streak. Underneath the whirlwind is real learning: {s} is building courage, resilience, and an experimenter’s relationship with the world.",
 ],
 "shows": [
  "{N} learns by moving — {s}’d rather try it, fast, than be told how first.",
  "{S} is drawn to the outdoors, to physical challenge, and to ‘can I climb that?’",
  "{S} is bold — often the first to try the new, the high, the untested.",
  "{S} gets restless and wilty when made to sit still for too long.",
 ],
 "glance": "Learns best by: moving, doing, and trying it {o}self.   Energized by: physical challenge, novelty, and the outdoors.   Needs: space to move, and safe risk — lots of it.   Watch for: leaping before looking, and frustration when penned in.",
 "q1": "An Explorer isn’t ‘too much energy.’ {S}’s building courage, resilience, and a hands-on, try-it relationship with the world that book-learning alone never gives.",
 "blend": {"The Explorer":0.95,"The Maker":0.58,"The Leader":0.50,"The Thinker":0.36,"The Connector":0.30,"The Storyteller":0.26},
 "blend_note": "{N}’s Explorer strength is powered by a Maker streak — {s} loves to build and test in the real world — and a Leader thread that turns adventures into expeditions {s} rallies others toward. Give {o} room to move and safe things to conquer, and {N} flourishes.",
 "mix_card": "Strengths work together. {N} is at {p} best when adventure has a purpose — building something (Maker) out in the world (Explorer) and getting others to join the mission (Leader). Look for active, hands-on challenges with a real goal.",
 "thinks": "{N} thinks through {p} body. Abstract, seated instruction slides off {o}; let {o} move, handle, and try and the understanding arrives fast. {S} reasons by experiment — do it, see what happens, adjust, go again — which is exactly how scientists and athletes actually learn. What looks like ‘not listening’ is often just a mind that needs to be in motion to engage.",
 "feels": "{N}’s feelings, like {p} energy, are big and physical — joy that bounces off the walls, frustration that needs somewhere to go. Bottled up or penned in, that energy turns to friction fast. {S} regulates best through movement, not stillness; a run, a climb, or a big physical job often does more for a young Explorer than a talking-to ever could.",
 "connects": "{N} connects through shared doing — {s} bonds on the move, in the game, on the adventure, side by side rather than sitting face to face. ‘Race you!’ and ‘come see this!’ are {p} invitations to closeness. {S} makes friends fast and warms to people who’ll get up and do things with {o}.",
 "tfc_q": "If you want a window into {N}’s heart, don’t sit {o} down for a talk. Get moving together — the conversation flows once {p} body is busy.",
 "nurture_intro": "Explorers need three simple things: room to move, permission to take safe risks, and an adult who sees the energy as fuel rather than a fault.",
 "nurture_cards": [
  ("Try this: move first, then focus", "Front-load the day with big physical activity — a park, a climb, a bike — before you ask for stillness. A well-moved Explorer can concentrate; a penned-in one can’t. You’re working with {p} wiring instead of against it."),
  ("Try this: allow safe risk", "Let {N} climb the tree, balance the wall, use the real tool — with sensible spotting, not a hovering ‘be careful.’ Safe risk is how an Explorer builds judgement and courage; over-protection just teaches {o} that {p} instincts can’t be trusted."),
  ("Try this: turn lessons into missions", "Make learning physical and adventurous — spell words by hopping, learn maths with steps and jumps, do science outdoors. When knowledge comes wrapped in motion and challenge, it sticks for {o} in a way a worksheet never will."),
 ],
 "avoid": [
  "Punishing the energy with endless ‘sit still’ — channel it instead; the drive is the strength.",
  "Hovering with ‘be careful’ at every turn; measured risk is how {s} learns to judge it.",
  "Long stretches of seated, passive learning with no movement — it’s a losing battle for both of you.",
 ],
 "thrives_intro": "These aren’t a curriculum — just well-matched starting points. Follow {N}’s lead and notice which ones make {o} lose track of time. That’s your signal.",
 "thrives": [
  ("Move & challenge", ["Climbing, balancing, running, swimming, biking, scooting — daily and outdoors.","Sports and physical clubs that reward energy and courage.","Obstacle courses and ‘can you get across without touching the floor?’ games."]),
  ("Outdoors & adventure", ["Real nature — woods, beaches, hills, streams to dam and rocks to scramble.","Camping, dens, exploring, mini ‘expeditions’ with a map and a mission.","Gardening, digging, building outdoors — big, physical, hands-on jobs."]),
  ("Hands-on doing", ["Real tools and real tasks with supervision — building, fixing, cooking.","Learning by trying: ‘have a go, then we’ll adjust’ beats a demo every time.","Active games that teach — scavenger hunts, movement-based counting and spelling."]),
 ],
 "screens": ("A note on screens", "Explorers are the kids most drained by too much sitting, so screens need a tight leash — and are best when active or paired with doing: movement games, filming their own stunts, videos that send them outside to try something. The test: does the screen get {N} up and doing, or glue {o} down?"),
 "str_intro": "Every strength has a shadow side. For Explorers, the boldness and drive that make {o} so alive can outrun {p} judgement, and the need to move can collide hard with a world that asks small children to sit still. Knowing the pattern helps you meet it calmly.",
 "str_look": [
  "Leaping before looking — impulsive risks, bumps, and ‘I didn’t think first.’",
  "Restlessness, fidgeting, or friction when required to sit still for long.",
  "Frustration that goes physical fast when {s}’s bored, penned in, or under-moved.",
 ],
 "str_help": [
  "Give the energy an exit before the storm: ‘Let’s run to the tree and back, then we’ll try again.’",
  "Coach the pause without killing the courage: ‘Brave and smart — check the landing, then jump.’",
  "Build movement into the day on purpose; prevention beats correction with an Explorer.",
 ],
 "phrases": "Instead of ‘Sit still and stop fidgeting’ try ‘Your body needs to move — let’s get that out, then focus.’ Instead of ‘Stop being reckless’ try ‘Brave is great; let’s be brave and smart — what’s your plan for landing?’ You’re keeping the courage and adding the judgement.",
 "grows": [
  "It’s early, and the point is never to pick {N}’s path at five. But it helps to know the deeper trait you’re nurturing: courage — the willingness to try, to risk, to learn by doing rather than waiting for certainty. Children who keep it become adults who start, adventure, and bounce back.",
  "The Explorer strength is the common root under athletes and adventurers, field scientists and paramedics, entrepreneurs, makers, and anyone who learns by doing and isn’t afraid to fail forward. What unites them isn’t a job — it’s a body-and-nerve confidence that the way to understand the world is to go out and try it.",
 ],
 "trait": "If you protect one thing, protect {N}’s courage — while steadily teaching {o} to pair it with judgement. Explorers hear a lot of ‘no,’ ‘careful,’ and ‘sit down,’ which can teach a bold child that {p} instincts are a problem. Every time you allow safe risk and coach the pause, you’re raising someone who dares — wisely.",
 "grows_q": "You’re not raising a future job title. You’re raising a child who isn’t afraid to try — and who learns, in {p} whole body, that {s} can handle the world by meeting it head-on.",
 "convo": [
  "‘What’s the bravest thing you tried today?’",
  "‘Where should we go explore this weekend — you choose.’",
  "‘You went for it! What did your body learn?’",
  "‘What’s something you want to get better at? Let’s practise it.’",
  "‘When is it smart to be careful, and when is it great to be bold?’",
 ],
 "affirm": [
  "‘You are brave and strong.’",
  "‘I love how you go for things.’",
  "‘Trying and falling is how we learn.’",
 ],
 "experiment": "Head outside and set a physical challenge with no single right way: ‘Can you get from here to that tree without touching the path?’ Let {o} invent the route, try, fail, adjust. Then ask ‘what worked?’ You’ll see the Explorer fully alive — and see how {s} learns by doing.",
}

if __name__ == "__main__":
    for key in ["Storyteller","Connector","Thinker","Leader","Explorer"]:
        fn,pages = render(key)
        print(f"{fn}  ->  {pages} pages")

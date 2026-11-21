#!/usr/bin/env python3
"""Render a deterministic, engraved passport spread for the Republic of Vermeille."""

from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


SCALE = 2
SIZE = 1024
W = H = SIZE * SCALE
RNG = random.Random(91403765)
INK = (42, 42, 38)
NAVY = (24, 49, 75)


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    base = Path("/usr/share/fonts/truetype/dejavu")
    name = "DejaVuSansMono.ttf" if mono else ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    try:
        return ImageFont.truetype(str(base / name), size * SCALE)
    except OSError:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size * SCALE)
        except OSError:
            return ImageFont.load_default()


def q(v: float) -> int:
    return round(v * SCALE)


def line(draw: ImageDraw.ImageDraw, points, fill, width=1):
    if getattr(draw, "document_ink", False):
        fill = INK + tuple(fill[3:])
    draw.line([(q(x), q(y)) for x, y in points], fill=fill, width=q(width), joint="curve")


def text(draw: ImageDraw.ImageDraw, xy, value, size=9, fill=(60, 54, 42), bold=False, mono=False, anchor=None):
    if len(fill) == 3:
        fill = NAVY if value in {"REPUBLIC OF VERMEILLE - PASSEPORT", "REPUBLIC OF VERMEILLE", "VISAS / VISAS", "VISA DE SEJOUR  /  ARTISTE"} else INK
    draw.text((q(xy[0]), q(xy[1])), value, font=font(size, bold, mono), fill=fill, anchor=anchor)


def centered(draw, cx, y, value, size, fill, bold=False):
    text(draw, (cx, y), value, size, fill, bold, anchor="mt")


def rounded(draw, box, radius, outline, width=1, fill=None):
    draw.rounded_rectangle(tuple(q(x) for x in box), radius=q(radius), outline=outline,
                           width=q(width), fill=fill)


def guilloche(draw, box, color, phase=0):
    x0, y0, x1, y1 = box
    for row in range(5):
        pts = []
        for i in range(181):
            t = i / 180
            x = x0 + (x1 - x0) * t
            y = (y0 + (y1-y0) * (row + .5) / 5
                 + 5 * math.sin(t * math.tau * 3 + row * .7 + phase)
                 + 1.8 * math.sin(t * math.tau * 8 + row))
            pts.append((x, y))
        line(draw, pts, color, .38)
    for col in range(7):
        pts = []
        for i in range(121):
            t = i / 120
            y = y0 + (y1-y0) * t
            x = x0 + (x1-x0) * (col + .5) / 7 + 2.4 * math.sin(t * math.tau * 4 + col)
            pts.append((x, y))
        line(draw, pts, color, .32)


def portrait(draw, x, y, w, h):
    # Banknote-style portrait made from cut polygons and fine engraved strokes.
    ink = (86, 83, 66)
    light = (190, 177, 143)
    mid = (149, 137, 108)
    draw.rectangle((q(x), q(y), q(x+w), q(y+h)), fill=(217, 204, 169), outline=(112, 101, 76), width=q(1))
    # Background rosette arcs.
    for r in range(5):
        box = (q(x+5+r*3), q(y+7+r*2), q(x+w-5-r*3), q(y+h-7-r*2))
        draw.ellipse(box, outline=(170, 157, 126), width=q(.45))
    # Neck and shoulders.
    draw.polygon([(q(x+17),q(y+h-5)),(q(x+20),q(y+55)),(q(x+34),q(y+48)),
                  (q(x+53),q(y+49)),(q(x+66),q(y+58)),(q(x+69),q(y+h-5))], fill=mid, outline=ink)
    draw.polygon([(q(x+12),q(y+h-5)),(q(x+16),q(y+68)),(q(x+27),q(y+62)),
                  (q(x+39),q(y+67)),(q(x+51),q(y+62)),(q(x+70),q(y+72)),(q(x+74),q(y+h-5))], fill=(178,165,133), outline=ink)
    # Tied-back hair silhouette and bun.
    draw.ellipse((q(x+18),q(y+12),q(x+39),q(y+34)), fill=(74,70,57), outline=ink)
    draw.polygon([(q(x+22),q(y+20)),(q(x+27),q(y+10)),(q(x+42),q(y+8)),(q(x+54),q(y+15)),
                  (q(x+58),q(y+29)),(q(x+54),q(y+50)),(q(x+46),q(y+57)),(q(x+31),q(y+54)),
                  (q(x+23),q(y+43))], fill=(89,82,64), outline=ink)
    # Face, slightly turned, with cheek and jaw planes.
    draw.polygon([(q(x+27),q(y+24)),(q(x+51),q(y+21)),(q(x+56),q(y+30)),(q(x+52),q(y+47)),
                  (q(x+44),q(y+57)),(q(x+33),q(y+53)),(q(x+27),q(y+42))], fill=(202,187,151), outline=ink)
    draw.polygon([(q(x+45),q(y+25)),(q(x+54),q(y+30)),(q(x+51),q(y+45)),(q(x+43),q(y+54)),
                  (q(x+39),q(y+43))], fill=(171,157,126))
    # Hairline and tied-back strands.
    line(draw, [(x+25,y+25),(x+31,y+16),(x+44,y+15),(x+54,y+23)], ink, 1.4)
    line(draw, [(x+54,y+27),(x+61,y+22),(x+66,y+25),(x+57,y+31)], ink, 1.2)
    # Eyes, nose, mouth; restrained engraved marks, not a cartoon face.
    line(draw, [(x+32,y+34),(x+38,y+33)], ink, .8)
    line(draw, [(x+44,y+32),(x+49,y+33)], ink, .7)
    draw.ellipse((q(x+35),q(y+33),q(x+36.5),q(y+34.5)), fill=ink)
    draw.ellipse((q(x+46),q(y+33),q(x+47.5),q(y+34.5)), fill=ink)
    line(draw, [(x+42,y+34),(x+40,y+42),(x+43,y+43)], (105,94,72), .6)
    line(draw, [(x+38,y+48),(x+43,y+49),(x+47,y+47)], (93,73,63), .65)
    # Engraving hatches follow face, hair, collar and jacket planes.
    hatch_groups = [((x+27,y+38),(x+34,y+50),6),((x+45,y+35),(x+51,y+46),6),
                    ((x+23,y+23),(x+35,y+18),6),((x+48,y+17),(x+56,y+25),6),
                    ((x+24,y+70),(x+35,y+78),7),((x+51,y+68),(x+66,y+79),8)]
    for (ax,ay),(bx,by),n in hatch_groups:
        for i in range(n):
            t=i/max(1,n-1)
            xx=ax+(bx-ax)*t; yy=ay+(by-ay)*t
            line(draw, [(xx,yy),(xx+3,yy+4)], (104,96,75), .42)
    # Neck scarf knot, characteristic of a formal maritime portrait.
    draw.polygon([(q(x+38),q(y+57)),(q(x+45),q(y+57)),(q(x+49),q(y+67)),(q(x+42),q(y+72)),(q(x+35),q(y+66))], fill=(111,103,80), outline=ink)
    line(draw, [(x+39,y+59),(x+44,y+66),(x+40,y+69)], light, .55)
    text(draw, (x+4,y+h-11), "VLM 2019", 5, (91,82,62), mono=True)


def stamp(draw, cx, cy, radius, color, title, date, kind="oval", angle=-8):
    # Transparent ink effect: layered imperfect outlines and rotated lettering.
    layer = Image.new("RGBA", (q(220), q(110)), (0,0,0,0))
    sd = ImageDraw.Draw(layer)
    if kind == "oval":
        sd.ellipse((q(8),q(9),q(212),q(101)), outline=color+(220,), width=q(2))
        sd.ellipse((q(13),q(14),q(207),q(96)), outline=color+(175,), width=q(.7))
        shape=(q(20),q(20),q(200),q(88))
        sd.arc(shape, 185, 355, fill=color+(220,), width=q(1))
        sd.arc(shape, 5, 175, fill=color+(220,), width=q(1))
    elif kind == "box":
        sd.rounded_rectangle((q(8),q(9),q(212),q(101)), radius=q(10), outline=color+(225,), width=q(2))
        sd.rounded_rectangle((q(14),q(15),q(206),q(95)), radius=q(7), outline=color+(175,), width=q(.7))
    else:
        sd.ellipse((q(25),q(2),q(195),q(108)), outline=color+(225,), width=q(2))
        sd.ellipse((q(31),q(8),q(189),q(102)), outline=color+(170,), width=q(.8))
    f1=font(7,bold=True); f2=font(7,mono=True)
    sd.text((q(110),q(32)), title, font=f1, fill=color+(235,), anchor="mm")
    sd.text((q(110),q(51)), date, font=f2, fill=color+(235,), anchor="mm")
    sd.text((q(110),q(69)), "VERMEILLE", font=f1, fill=color+(220,), anchor="mm")
    layer=layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
    draw._image.paste(layer, (q(cx-55),q(cy-27)), layer)


def make_art() -> Image.Image:
    # Dark, tactile tabletop and soft page shadow.
    base = Image.new("RGB", (W,H), (25,31,30))
    pix=base.load()
    for yy in range(H):
        for xx in range(W):
            n=RNG.randint(-2,2)
            vignette=max(0, 1-math.hypot(xx-W*.5, yy-H*.5)/(W*.85))
            pix[xx,yy]=(max(0,min(255,25+n+int(4*vignette))),max(0,min(255,31+n+int(5*vignette))),max(0,min(255,30+n+int(4*vignette))))
    shadow=Image.new("RGBA",(W,H),(0,0,0,0)); sh=ImageDraw.Draw(shadow)
    sh.rounded_rectangle((q(63),q(95),q(961),q(925)),radius=q(23),fill=(0,0,0,180))
    shadow=shadow.filter(ImageFilter.GaussianBlur(q(22)))
    base=Image.alpha_composite(base.convert("RGBA"),shadow)
    # The open passport is one connected spread with a visible central binding.
    # Blend translucent ink onto opaque paper; RGBA drawing on RGBA would
    # replace alpha and expose the dark tabletop through the page itself.
    paper=base.convert("RGB"); d=ImageDraw.Draw(paper, "RGBA")
    d.rounded_rectangle((q(66),q(75),q(958),q(920)),radius=q(18),fill=(193,179,145),outline=(83,70,51),width=q(2))
    d.rounded_rectangle((q(72),q(81),q(952),q(914)),radius=q(14),fill=(229,218,187),outline=(247,238,210),width=q(2))
    # Warm, subtly varied page field, split by the binding.
    for y in range(q(86),q(910)):
        t=(y-q(86))/(q(824))
        c=(int(243-8*t),int(234-8*t),int(211-8*t),255)
        d.line((q(78),y,q(946),y),fill=c,width=1)
    d.rectangle((q(78),q(87),q(507),q(908)),fill=INK+(2,))
    d.rectangle((q(519),q(87),q(946),q(908)),fill=(255,255,255,3))
    # Page perimeter, stitch marks and central cloth hinge.
    d.rounded_rectangle((q(83),q(92),q(941),q(903)),radius=q(8),outline=(155,137,99),width=q(1))
    for y in range(111,889,12):
        line(d,[(510,y),(515,y+4)],(139,119,85,180),.7)
    d.rectangle((q(506),q(91),q(518),q(904)),fill=(153,130,94,65))
    line(d,[(507,96),(507,900)],(124,103,75,170),.7)
    line(d,[(517,96),(517,900)],(249,239,212,220),.7)
    # Underprint guilloche and a faint maritime emblem on both leaves.
    guilloche(d,(91,219,493,781),INK+(24,),.4)
    guilloche(d,(529,107,933,891),INK+(22,),1.1)
    for cx,cy in [(291,626),(722,345),(721,738)]:
        for r in (22,32,42):
            d.ellipse((q(cx-r),q(cy-r),q(cx+r),q(cy+r)),outline=(157,137,100,35),width=q(.6))
        for a in range(0,360,30):
            x1=cx+22*math.cos(math.radians(a));y1=cy+22*math.sin(math.radians(a))
            x2=cx+42*math.cos(math.radians(a));y2=cy+42*math.sin(math.radians(a))
            line(d,[(x1,y1),(x2,y2)],(157,137,100,30),.5)
    # LEFT: identity page.
    text(d,(103,101),"REPUBLIC OF VERMEILLE - PASSEPORT",10,(62,48,37),True)
    text(d,(447,101),"PRTL",9,(69,53,38),True,mono=True)
    line(d,[(100,121),(493,121)],(112,84,57),.8)
    text(d,(103,132),"PASSPORT  /  PASSEPORT",6,(117,98,67),True)
    text(d,(103,151),"REPUBLIC OF VERMEILLE",12,(61,48,38),True)
    text(d,(103,168),"Passeport de la Republique de Vermeille",6,(104,88,61))
    # Identity portrait.
    portrait(d,105,198,112,143)
    d.document_ink = True
    # Watermark seal overlapping portrait field, lightly printed.
    d.ellipse((q(127),q(270),q(194),q(337)),outline=(119,102,72,45),width=q(1))
    d.ellipse((q(133),q(276),q(188),q(331)),outline=(119,102,72,38),width=q(.6))
    # Data columns with restrained rules.
    lx=231
    fields=[("Surname", "CABRAL", 202), ("Given names", "MARIANA-ELENA", 236),
            ("Nationality", "VERMEILLAIS", 270), ("Date of birth", "1984-11-27", 304)]
    for label,val,y in fields:
        text(d,(lx,y),label.upper(),5.5,(119,99,67),True)
        text(d,(lx,y+9),val,9,(46,45,37),True)
        line(d,[(lx,y+27),(478,y+27)],(151,130,95,105),.5)
    # issuance details in narrow paired columns
    for label,val,x,y in [("DATE OF ISSUE","2019-06-14",104,361),
                          ("DATE OF EXPIRY","2029-06-13",294,361),
                          ("AUTHORITY","PORT OF SAINT-AMARY",104,399),
                          ("SERIAL NUMBER","91403765",294,399)]:
        text(d,(x,y),label,5.5,(119,99,67),True)
        text(d,(x,y+9),val,8,(47,45,37),True,mono=(label=="SERIAL NUMBER"))
    line(d,[(102,431),(492,431)],(120,99,67),.8)
    centered(d,297,440,"SIGNATURE / SIGNATURE",5.5,(120,101,72),True)
    # hand-signed engraved flourish
    line(d,[(214,474),(226,461),(233,477),(244,455),(250,472),(260,468),(270,456),(277,478),(288,463),(300,469),(312,459),(323,471),(337,464)],(60,72,67),1.15)
    text(d,(342,461),"M. Cabral",7,(57,66,60),False)
    line(d,[(104,488),(487,488)],(133,112,80,170),.6)
    # Biometric icon and serial microprint.
    d.ellipse((q(107),q(500),q(135),q(528)),outline=(94,90,71),width=q(1))
    for rr in (3,6,9):
        d.arc((q(121-rr),q(514-rr),q(121+rr),q(514+rr)),190,350,fill=(87,84,68),width=q(.65))
    text(d,(144,502),"BIOMETRIC",5.5,(98,86,61),True)
    text(d,(144,511),"VERMEILLAIS CITIZEN  /  MERIDIAN COASTAL REGISTER",5.2,(104,94,72),mono=True)
    # MRZ panel.
    d.rectangle((q(97),q(538),q(498),q(590)),fill=(211,198,166),outline=INK,width=q(.6))
    text(d,(103,542),"P<PRTCABRAL<<MARIANA<ELENA<<<<<<<<<<<<",7.4,(38,40,35),mono=True)
    text(d,(103,562),"PRTC91403765<4VER8411278F2906136<<<<<<",7.4,(38,40,35),mono=True)
    text(d,(103,583),"READABLE BY MACHINE  /  LECTURE OPTIQUE",4.8,(113,100,73),True)
    # Small folio and language note.
    text(d,(103,612),"VERMEILLAIS / ENGLISH",6,(110,96,69),True)
    text(d,(457,612),"01",8,(101,84,59),True,mono=True)
    # RIGHT: visa and travel record page.
    centered(d,733,101,"VISAS / VISAS",7,(99,78,53),True)
    text(d,(548,116),"REPUBLIQUE MARITIME  -  PORTS & FRONTIERES",5.5,(123,103,72),True)
    line(d,[(535,130),(929,130)],(137,113,78),.8)
    # Paper visa label with aged perforated edge.
    d.rounded_rectangle((q(548),q(149),q(914),q(278)),radius=q(4),fill=(237,224,187),outline=(148,112,66),width=q(1))
    d.rectangle((q(554),q(155),q(908),q(272)),outline=(179,142,86),width=q(.6))
    for xx in range(557,908,9):
        d.ellipse((q(xx),q(146),q(xx+3),q(152)),fill=(222,208,174))
        d.ellipse((q(xx),q(275),q(xx+3),q(281)),fill=(222,208,174))
    text(d,(563,162),"VISA DE SEJOUR  /  ARTISTE",7,(103,68,42),True)
    text(d,(563,178),"TEMPORARY CULTURAL PERMIT",5.5,(115,84,53),True)
    line(d,[(563,193),(894,193)],(162,128,78),.55)
    text(d,(563,202),"CONDITION: ARTIST'S PASS -",7,(53,47,37),True)
    text(d,(563,214),"WORK PROHIBITED, SALES PERMITTED",7,(53,47,37),True)
    text(d,(563,239),"ISSUED AT SAINT-AMARY  /  VALID TO 2024-06-30",5.5,(101,80,55),mono=True)
    # Embossed circular seal over visa corner.
    d.ellipse((q(861),q(199),q(899),q(237)),outline=(145,76,56,170),width=q(1.2))
    d.ellipse((q(866),q(204),q(894),q(232)),outline=(145,76,56,145),width=q(.7))
    centered(d,880,210,"V",12,(139,77,54,170),True)
    # Chronological port / city travel stamps.
    stamp(d,613,345,1,(15,63,137),"PORT AUTHORITY OF SAINT-AMARY","ARRIVAL 2021-03-02","oval",-7)
    stamp(d,803,345,1,(20,94,47),"CITY OF NORDHAFEN","DEPARTURE 2021-09-18","box",5)
    stamp(d,613,466,1,(161,29,32),"HALCOTT AIRPORT","ENTRY 2023-05-11","circle",-4)
    stamp(d,803,466,1,(131,76,15),"PORT OF VELLACROIX","EXIT 2024-02-09","oval",6)
    # Fine guide rules give the right page a real ledger rhythm.
    for y in (411,532,553,574,595,616,637,658,679,700,721,742,763,784,805,826,847,868):
        line(d,[(544,y),(927,y)],(155,137,104,46),.45)
    text(d,(548,551),"ENTRY & DEPARTURE RECORD",5.5,(120,101,70),True)
    text(d,(548,563),"MARITIME CLIMATE  /  MIXED PORTUGUESE-FRENCH CUSTOM",5.2,(128,111,79))
    # Faint administrative annotation, a quiet clue rather than a caption.
    rounded(d,(552,601,915,670),3,INK+(130,),.65,(220,207,175))
    text(d,(562,608),"PORTS KEEP THEIR OWN CALENDARS.",6.3,(87,77,57),True)
    text(d,(562,621),"A market stall may count as a studio; a studio",5.5,(100,89,66))
    text(d,(562,631),"may be entered as a vessel. Customs practice",5.5,(100,89,66))
    text(d,(562,641),"is settled at the quay, in two languages.",5.5,(100,89,66))
    text(d,(562,657),"BUREAU DES PASSAGES  /  FOLIO 02",4.8,(124,106,75),True,mono=True)
    # Intentionally understated national seal near bottom of right leaf.
    cx,cy=729,779
    for rr in (32,37,42):
        d.ellipse((q(cx-rr),q(cy-rr),q(cx+rr),q(cy+rr)),outline=(136,117,80,82),width=q(.7))
    d.polygon([(q(cx),q(cy-26)),(q(cx+5),q(cy-6)),(q(cx+25),q(cy)),(q(cx+5),q(cy+6)),
               (q(cx),q(cy+26)),(q(cx-5),q(cy+6)),(q(cx-25),q(cy)),(q(cx-5),q(cy-6))],
              outline=(133,112,77,105),fill=(191,174,136,45))
    text(d,(783,768),"REPUBLIC OF",5.5,(121,103,72),True)
    text(d,(783,778),"VERMEILLE",8,(98,80,55),True)
    text(d,(783,791),"PORTS LIBRES",5.3,(121,103,72),True)
    text(d,(548,878),"02",8,(101,84,59),True,mono=True)
    text(d,(821,878),"PASSPORT CONTROL  /  CONTROLE",5,(117,97,68),True)
    # Fine grain confined to paper keeps output tactile while remaining deterministic.
    # Add sparse fibers on the page as tiny, low-contrast marks.
    grain=ImageDraw.Draw(paper, "RGBA")
    for _ in range(1500):
        xx=RNG.randrange(q(80),q(944)); yy=RNG.randrange(q(90),q(906))
        if RNG.random()<.5:
            col=(115,94,62,17)
        else:
            col=(255,251,226,35)
        grain.line((xx,yy,xx+RNG.randrange(1,5),yy),fill=col,width=1)
    base=paper
    out=base.convert("RGB").resize((SIZE,SIZE),Image.Resampling.LANCZOS)
    return out


def main() -> None:
    img=make_art()
    preferred=Path("/output/entry.png")
    if preferred.parent.is_dir() and os.access(preferred.parent,os.W_OK):
        target=preferred
    else:
        target=Path(__file__).resolve().parent/"entry.png"
    target.parent.mkdir(parents=True,exist_ok=True)
    img.save(target,format="PNG",optimize=True,compress_level=9)
    print(target)


if __name__ == "__main__":
    main()

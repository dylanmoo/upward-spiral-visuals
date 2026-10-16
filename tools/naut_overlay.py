"""Animated math overlay for the nautilus loop: a logarithmic spiral traced along the shell, the golden ratio
computed, and Fibonacci ratios converging on phi. Gold on black for Add/Screen blending; exact loop (blank at both ends).
Usage: naut_overlay.py <out_dir_for_rgba_pngs> [preview_frame]"""
import math
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

N, S, SS = 228, 1080, 2            # frames, output size, supersample
CX, CY, R0, B, ROT = 638, 518, 372, 0.150, 0.0   # spiral fit: r = R0*e^(-B*theta_cw)
GOLD = (255, 214, 140)
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"
f_big, f_mid, f_small = (ImageFont.truetype(SERIF, n * SS) for n in (36, 30, 24))
f_ital = ImageFont.truetype(SERIF_I, 44 * SS)
f_ital_small = ImageFont.truetype(SERIF_I, 26 * SS)
FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def span(f, a, b):
    return ease((f - a) / (b - a))


def spiral_pts(frac):
    # theta_cw from deep inside (r~4) out to the shell lip (r~640)
    t_in, t_out = math.log(R0 / 4) / B, -math.log(585 / R0) / B
    t_end = t_in + (t_out - t_in) * frac
    pts, n = [], 900
    for i in range(n + 1):
        th = t_in + (t_end - t_in) * i / n
        r = R0 * math.exp(-B * th)
        a = th + ROT
        pts.append(((CX + r * math.cos(a)) * SS, (CY + r * math.sin(a)) * SS))
    return pts


def centered(d, y, text, font, alpha):
    w = d.textlength(text, font=font)
    d.text((S * SS / 2 - w / 2, y * SS), text, font=font, fill=GOLD + (int(255 * alpha),))


def frame(f):
    img = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    out = 1 - span(f, 180, 214)                       # global fade out
    # spiral
    sp = span(f, 12, 112)
    if sp > 0:
        d.line(spiral_pts(sp), fill=GOLD + (int(235 * out),), width=4 * SS, joint="curve")
    # phi derivation (types on)
    phi_txt = "φ = (1 + √5) / 2 = 1.6180339887…"
    k = int(len(phi_txt) * span(f, 24, 84))
    if k:
        centered(d, 112, phi_txt[:k], f_big, out)
    # Fibonacci ratio ticker converging on phi
    fa = span(f, 60, 150)
    if fa > 0:
        i = 1 + int(fa * (len(FIB) - 2))
        seq = ", ".join(str(x) for x in FIB[: i + 1])
        centered(d, 902, seq, f_small, out)
        centered(d, 942, f"{FIB[i]} / {FIB[i - 1]} = {FIB[i] / FIB[i - 1]:.7f}", f_mid, out)
    # log spiral law over the empty body chamber
    la = span(f, 100, 128) * out
    if la > 0:
        base = "r = a · e"
        d.text((168 * SS, 690 * SS), base, font=f_ital, fill=GOLD + (int(255 * la),))
        x = 168 * SS + d.textlength(base, font=f_ital) + 3 * SS
        d.text((x, 680 * SS), "bθ", font=f_ital_small, fill=GOLD + (int(255 * la),))
    a = lay.getchannel("A")
    halo = Image.new("RGBA", img.size, (0, 0, 0, 0))
    halo.putalpha(a.filter(ImageFilter.GaussianBlur(5 * SS)).point(lambda v: min(255, v * 2)))
    glow = lay.filter(ImageFilter.GaussianBlur(9 * SS))
    img.alpha_composite(halo)
    img.alpha_composite(glow)
    img.alpha_composite(lay)
    return img.resize((S, S), Image.LANCZOS)


if len(sys.argv) > 2:
    frame(int(sys.argv[2])).save(sys.argv[1])
else:
    for f in range(N):
        frame(f).save(f"{sys.argv[1]}/ov_{f:04d}.png")

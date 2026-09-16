#!/usr/bin/env python3
"""Imperfections of a cheap recycled sheet, all wrapping seamlessly.

Writes two MVG files:
  OUT_SHARP  - flecks/inclusions and pits (drawn small, blurred very little)
  OUT_SOFT   - blotches and pulp/water density streaks (blurred a lot)
  OUT_CREASE - one or two faint fold lines (own layer so it can stay very faint)

usage: marks.py SEED OUT_SHARP OUT_SOFT OUT_CREASE
       [N_FLECK N_PIT N_BLOTCH N_STREAK N_CREASE]
"""
import math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wrap import W, offsets

seed = int(sys.argv[1]); out_sharp = sys.argv[2]; out_soft = sys.argv[3]; out_crease = sys.argv[4]
g = lambda i, d: int(sys.argv[i]) if len(sys.argv) > i else d
N_FLECK  = g(5, 55)
N_PIT    = g(6, 70)
N_BLOTCH = g(7, 14)
N_STREAK = g(8, 7)
N_CREASE = g(9, 2)

rnd = random.Random(seed)
sharp  = ['stroke none']
soft   = ['stroke none', 'fill none']
crease = ['stroke none', 'fill none']

def blob(dst, cx, cy, r, col, op, squash, rot, wobble=0.35):
    """An irregular closed blob: a polygon on a jittered radius, so nothing is a
    perfect circle."""
    n = rnd.randint(7, 11)
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        rr = r * (1 + rnd.uniform(-wobble, wobble))
        px, py = rr * math.cos(t), rr * math.sin(t) * squash
        px, py = (px * math.cos(rot) - py * math.sin(rot),
                  px * math.sin(rot) + py * math.cos(rot))
        pts.append((cx + px, cy + py))
    for dx, dy in offsets(pts, 2):
        dst += ['fill %s' % col, 'fill-opacity %.3f' % op,
                'polygon ' + ' '.join('%.2f,%.2f' % (p[0]+dx, p[1]+dy) for p in pts)]

def stroke_path(dst, pts, col, op, sw):
    d = 'M %.2f,%.2f' % pts[0]
    for i in range(1, len(pts) - 1, 2):
        d += ' Q %.2f,%.2f %.2f,%.2f' % (pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
    for dx, dy in offsets(pts, sw + 2):
        body = 'M %.2f,%.2f' % (pts[0][0]+dx, pts[0][1]+dy)
        for i in range(1, len(pts) - 1, 2):
            body += ' Q %.2f,%.2f %.2f,%.2f' % (pts[i][0]+dx, pts[i][1]+dy,
                                                pts[i+1][0]+dx, pts[i+1][1]+dy)
        dst += ['stroke %s' % col, 'stroke-width %.2f' % sw,
                'stroke-opacity %.3f' % op, 'fill none', "path '%s'" % body]

# --- recycled-pulp specks: small, dark, irregular, a wide range of darkness ---
for _ in range(N_FLECK):
    r = rnd.random()
    rad = 0.6 + 2.2 * r * r                      # mostly tiny, occasionally 3-4 px
    op  = rnd.uniform(0.25, 1.0) * (0.55 if rad < 1.4 else 0.85)
    blob(sharp, rnd.uniform(0, W), rnd.uniform(0, W), rad, '#000000', op,
         rnd.uniform(0.45, 1.0), rnd.uniform(0, math.pi), wobble=0.45)

# --- pits: tiny surface holes, a dark core with a light rim on the lit side ---
for _ in range(N_PIT):
    cx, cy = rnd.uniform(0, W), rnd.uniform(0, W)
    rad = rnd.uniform(0.8, 2.4)
    op  = rnd.uniform(0.15, 0.5)
    blob(sharp, cx, cy, rad, '#000000', op, rnd.uniform(0.6, 1.0), rnd.uniform(0, math.pi))
    # rim offset toward the light (azimuth 118 deg -> up-left)
    blob(sharp, cx - rad * 0.8, cy - rad * 0.6, rad * 0.75, '#ffffff', op * 0.7,
         rnd.uniform(0.6, 1.0), rnd.uniform(0, math.pi))

# --- faint broad blotches in pulp density ---
for _ in range(N_BLOTCH):
    blob(soft, rnd.uniform(0, W), rnd.uniform(0, W), rnd.uniform(14, 52),
         '#000000' if rnd.random() < 0.6 else '#ffffff',
         rnd.uniform(0.10, 0.30), rnd.uniform(0.35, 1.0), rnd.uniform(0, math.pi), 0.5)

# --- long, thin, gently curved density streaks (water / pulp draw marks) ---
for _ in range(N_STREAK):
    x, y = rnd.uniform(0, W), rnd.uniform(0, W)
    a = rnd.uniform(0, 2 * math.pi)
    L = rnd.uniform(220, 620)
    nseg = 4
    seg = L / nseg
    pts = [(x, y)]
    px, py = x, y
    for _s in range(nseg):
        da = rnd.gauss(0, 0.22)
        pts.append((px + math.cos(a) * seg * .5, py + math.sin(a) * seg * .5))
        px, py = px + math.cos(a + da * .5) * seg, py + math.sin(a + da * .5) * seg
        pts.append((px, py)); a += da
    stroke_path(soft, pts, '#000000' if rnd.random() < 0.55 else '#ffffff',
                rnd.uniform(0.10, 0.26), rnd.uniform(4, 13))

# --- one or two very faint crease lines running most of the way across ---
for _ in range(N_CREASE):
    a = rnd.uniform(0, 2 * math.pi)
    x, y = rnd.uniform(0, W), rnd.uniform(0, W)
    seg = rnd.uniform(260, 420)
    pts = [(x, y)]
    px, py = x, y
    for _s in range(4):
        da = rnd.gauss(0, 0.13)                   # a fold wanders, it is not a ruled line
        pts.append((px + math.cos(a) * seg * .5, py + math.sin(a) * seg * .5))
        px, py = px + math.cos(a + da * .5) * seg, py + math.sin(a + da * .5) * seg
        pts.append((px, py)); a += da
    sw = rnd.uniform(1.5, 3.0)
    stroke_path(crease, pts, '#ffffff', rnd.uniform(0.35, 0.55), sw)
    stroke_path(crease, [(p[0] + 2.5, p[1] + 2.0) for p in pts], '#000000',
                rnd.uniform(0.28, 0.45), sw)

open(out_sharp,  'w').write('\n'.join(sharp)  + '\n')
open(out_soft,   'w').write('\n'.join(soft)   + '\n')
open(out_crease, 'w').write('\n'.join(crease) + '\n')
print('marks: %d flecks, %d pits, %d blotches, %d streaks, %d creases'
      % (N_FLECK, N_PIT, N_BLOTCH, N_STREAK, N_CREASE))

#!/usr/bin/env python3
"""Short, thin, curved fibre strands at fully random angles, clustered rather
than evenly scattered, with a minority of long strands. Wraps seamlessly.

usage: fibres.py SEED COUNT OUT LMIN LMAX WMIN WMAX OPMAX
                 [LONG_FRAC] [LONG_MAX] [CLUSTER] [WHITE_FRAC]
"""
import math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wrap import W, offsets

seed, count, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
lmin, lmax = float(sys.argv[4]), float(sys.argv[5])
wmin, wmax = float(sys.argv[6]), float(sys.argv[7])
opmax = float(sys.argv[8])
long_frac = float(sys.argv[9])  if len(sys.argv) > 9  else 0.07
long_max  = float(sys.argv[10]) if len(sys.argv) > 10 else 80.0
cluster   = float(sys.argv[11]) if len(sys.argv) > 11 else 0.55  # share placed in clumps
whitefrac = float(sys.argv[12]) if len(sys.argv) > 12 else 0.58  # share lighter than the sheet

rnd = random.Random(seed)
lines = ['fill none', 'stroke-linecap round']

# clumps of pulp: some fibres bunch together, leaving other areas bare
ncl = max(4, int(count / 55))
clumps = [(rnd.uniform(0, W), rnd.uniform(0, W), rnd.uniform(18, 70)) for _ in range(ncl)]

def place():
    if rnd.random() < cluster:
        cx, cy, cr = clumps[rnd.randrange(ncl)]
        return (cx + rnd.gauss(0, cr)) % W, (cy + rnd.gauss(0, cr)) % W
    return rnd.uniform(0, W), rnd.uniform(0, W)

for _ in range(count):
    x, y = place()
    ang = rnd.uniform(0, 2 * math.pi)                 # fully random orientation
    if rnd.random() < long_frac:
        L = rnd.uniform(lmax, long_max)
        nseg = rnd.choice((3, 4))
        bend = rnd.uniform(-1.1, 1.1)                 # long ones wander more
        sw = rnd.uniform(wmin, wmin + (wmax - wmin) * 0.6)
    else:
        L = rnd.uniform(lmin, lmax)
        nseg = 2 if rnd.random() < 0.7 else 1
        bend = rnd.uniform(-0.6, 0.6)
        sw = rnd.uniform(wmin, wmax)

    # contrast: most faint, a few distinctly visible
    r = rnd.random()
    op = opmax * (0.30 + 0.70 * r * r if r < 0.8 else 1.0)
    col = '#ffffff' if rnd.random() < whitefrac else '#000000'

    px, py, a = x, y, ang
    seg = L / nseg
    pts = [(px, py)]
    d = 'M %.2f,%.2f' % (px, py)
    for _s in range(nseg):
        da = bend / nseg + rnd.gauss(0, 0.10)          # per-segment jitter
        cx = px + math.cos(a) * seg * 0.5
        cy = py + math.sin(a) * seg * 0.5
        ex = px + math.cos(a + da * 0.5) * seg
        ey = py + math.sin(a + da * 0.5) * seg
        d += ' Q %.2f,%.2f %.2f,%.2f' % (cx, cy, ex, ey)
        pts += [(cx, cy), (ex, ey)]
        px, py, a = ex, ey, a + da

    for dx, dy in offsets(pts, sw + 2):
        body = d if (dx == 0 and dy == 0) else \
            'M %.2f,%.2f' % (x + dx, y + dy) + ''.join(
                ' Q %.2f,%.2f %.2f,%.2f' % (pts[i][0]+dx, pts[i][1]+dy, pts[i+1][0]+dx, pts[i+1][1]+dy)
                for i in range(1, len(pts) - 1, 2))
        lines += ['stroke %s' % col, 'stroke-width %.2f' % sw,
                  'stroke-opacity %.3f' % op, "path '%s'" % body]

open(out, 'w').write('\n'.join(lines) + '\n')
print('%s: %d fibres -> %d strokes' % (os.path.basename(out), count,
      sum(1 for l in lines if l.startswith('path'))))

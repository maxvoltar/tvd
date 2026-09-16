"""Shared helpers: emit MVG shapes that wrap seamlessly across a W x W tile.

Everything drawn is duplicated at +/-W in x and/or y whenever its bounding box
(including stroke width) comes within reach of an edge, so the tile has no seam.
"""
W = 1024

def offsets(pts, pad):
    """Which (dx,dy) copies are needed for a shape covering `pts` with `pad` slack."""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1 = min(xs) - pad, max(xs) + pad
    y0, y1 = min(ys) - pad, max(ys) + pad
    dxs = [0]; dys = [0]
    if x0 < 0: dxs.append(W)
    if x1 > W: dxs.append(-W)
    if y0 < 0: dys.append(W)
    if y1 > W: dys.append(-W)
    return [(dx, dy) for dx in dxs for dy in dys]

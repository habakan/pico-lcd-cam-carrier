"""Places J1-J4 on the board from generate.py and routes it on two layers. Run with KiCad's Python after generate.py:
~/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 route.py"""

import heapq
import os
from pathlib import Path

import numpy as np
import pcbnew

import generate as g

FP_DIR = Path(os.environ.get("KICAD_FOOTPRINTS", Path.home() / "Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"))
PCB = g.OUT / "hat_carrier.kicad_pcb"
# JLCPCB's standard process takes 0.127 mm; 0.15 leaves margin and still fits one track between 2.54 mm pads
TRACK, CLEARANCE, VIA, DRILL = 0.25, 0.15, 0.6, 0.3
RES, SLACK, VIA_COST = 0.1, 0.03, 25
# Copper stays clear of the M2.5 standoffs and screw heads (radius 2.9) and the case's M2 screws
KEEPOUT = [(g.HAT_XY[0] + x, g.HAT_XY[1] + y, 3.0) for x, y in g.HAT_HOLES] + [(x, y, 2.3) for x, y in g.CASE_SCREWS]

# ref, footprint, side, nets by pad, then where pads 1, 2 and 3 must land (front view)
J3_1 = (g.HAT_XY[0] + g.HAT_HEADER[0] + 9.5 * 2.54, g.HAT_XY[1] + g.HAT_HEADER[1] - 1.27)
J1_1 = (g.PICO_XY[0] + 1.37, g.PICO_XY[1] + 1.61)
J2_1 = (g.PICO_XY[0] + 1.37, g.PICO_XY[1] + 19.39)
J4_1 = (g.CAMERA_XY[0] + 3.81, g.CAMERA_XY[1] + 1.27)
PARTS = [
    ("J1", "Connector_PinSocket_2.54mm", "PinSocket_1x20_P2.54mm_Vertical", True, g.PICO_LEFT,
     [J1_1, (J1_1[0] + 2.54, J1_1[1]), (J1_1[0] + 5.08, J1_1[1])]),
    ("J2", "Connector_PinSocket_2.54mm", "PinSocket_1x20_P2.54mm_Vertical", True, g.PICO_RIGHT,
     [J2_1, (J2_1[0] + 2.54, J2_1[1]), (J2_1[0] + 5.08, J2_1[1])]),
    ("J3", "Connector_PinHeader_2.54mm", "PinHeader_2x20_P2.54mm_Vertical", False, [g.HAT[n][1] for n in range(1, 41)],
     [J3_1, (J3_1[0], J3_1[1] + 2.54), (J3_1[0] - 2.54, J3_1[1])]),
    # Seen from the front, the B0070's pins run in the mirror of KiCad's socket numbering; the header has the same pads
    ("J4", "Connector_PinHeader_2.54mm", "PinHeader_2x10_P2.54mm_Vertical", True, g.CAMERA,
     [J4_1, (J4_1[0], J4_1[1] + 2.54), (J4_1[0] + 2.54, J4_1[1])]),
]


def mm(v):
    return pcbnew.FromMM(v)


def place(board, ref, lib, name, back, targets):
    fp = pcbnew.FootprintLoad(str(FP_DIR / f"{lib}.pretty"), name)
    fp.SetReference(ref)
    board.Add(fp)
    if back:
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    for deg in (0, 90, 180, 270):
        fp.SetOrientationDegrees(deg)
        pos = [fp.FindPadByNumber(str(n)).GetPosition() for n in (1, 2, 3)]
        rel = [(pcbnew.ToMM(p.x - pos[0].x), pcbnew.ToMM(p.y - pos[0].y)) for p in pos]
        want = [(x - targets[0][0], y - targets[0][1]) for x, y in targets]
        if all(abs(a - b) < 1e-3 for r, w in zip(rel, want) for a, b in zip(r, w)):
            fp.Move(pcbnew.VECTOR2I(mm(targets[0][0]) - pos[0].x, mm(targets[0][1]) - pos[0].y))
            return fp
    raise SystemExit(f"{ref}: no orientation puts pads 1-3 at {targets}")


class Grid:
    """Owner maps on a 0.1 mm grid: -1 free, -2 blocked for everyone, else the only net allowed there."""

    def __init__(self, w, h):
        self.nx, self.ny = round(w / RES) + 1, round(h / RES) + 1
        self.xs, self.ys = np.arange(self.nx) * RES, np.arange(self.ny) * RES
        self.track = [np.full((self.ny, self.nx), -1, np.int32) for _ in range(2)]
        self.via = np.full((self.ny, self.nx), -1, np.int32)

    def stamp(self, arr, net, dist, reach, box):
        x0, y0, x1, y1 = box
        i0, i1 = max(0, int((x0 - reach) / RES)), min(self.nx, int((x1 + reach) / RES) + 2)
        j0, j1 = max(0, int((y0 - reach) / RES)), min(self.ny, int((y1 + reach) / RES) + 2)
        X, Y = np.meshgrid(self.xs[i0:i1], self.ys[j0:j1])
        hit = dist(X, Y) < reach
        sub = arr[j0:j1, i0:i1]
        if net < 0:
            sub[hit] = -2
            return
        sub[hit & (sub == -1)] = net
        sub[hit & (sub != net)] = -2

    def add(self, net, layers, dist, radius, box):
        """An object of the given radius around dist(); tracks and vias of other nets keep CLEARANCE from it."""
        for layer in layers:
            self.stamp(self.track[layer], net, dist, radius + CLEARANCE + TRACK / 2 + SLACK, box)
        self.stamp(self.via, net, dist, radius + CLEARANCE + VIA / 2 + SLACK, box)


def seg_dist(ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    n = dx * dx + dy * dy or 1e-9
    def dist(X, Y):
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / n, 0, 1)
        return np.hypot(X - ax - t * dx, Y - ay - t * dy)
    return dist


def astar(grid, net, sources, goal):
    nx, ny = grid.nx, grid.ny
    gi, gj = goal
    tr, via = grid.track, grid.via
    def free(layer, i, j):
        o = tr[layer][j, i]
        return o == -1 or o == net
    def h(i, j):
        dx, dy = abs(i - gi), abs(j - gj)
        return max(dx, dy) + 0.414 * min(dx, dy)
    best, prev, heap = {}, {}, []
    for s in sources:
        best[s] = 0
        heapq.heappush(heap, (h(s[1], s[2]), 0, s))
    while heap:
        _, cost, s = heapq.heappop(heap)
        if cost > best.get(s, 1e18):
            continue
        layer, i, j = s
        if (i, j) == goal:
            path = [s]
            while path[-1] in prev:
                path.append(prev[path[-1]])
            return path[::-1]
        steps = []
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            ni, nj = i + di, j + dj
            if not (0 <= ni < nx and 0 <= nj < ny) or not free(layer, ni, nj):
                continue
            if di and dj and not (free(layer, ni, j) and free(layer, i, nj)):
                continue
            steps.append(((layer, ni, nj), 1.414 if di and dj else 1))
        o = via[j, i]
        if (o == -1 or o == net) and free(1 - layer, i, j):
            steps.append(((1 - layer, i, j), VIA_COST))
        for n, c in steps:
            nc = cost + c
            if nc < best.get(n, 1e18):
                best[n], prev[n] = nc, s
                heapq.heappush(heap, (nc + h(n[1], n[2]), nc, n))
    return None


def simplify(path):
    """Grid steps to (layer, points) runs with collinear points dropped."""
    runs, cur = [], [path[0]]
    for s in path[1:]:
        if s[0] != cur[-1][0]:
            runs.append(cur)
            cur = [s]
        else:
            cur.append(s)
    runs.append(cur)
    out = []
    for run in runs:
        pts = [run[0][1:]]
        for k in range(1, len(run) - 1):
            a, b, c = run[k - 1][1:], run[k][1:], run[k + 1][1:]
            if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
                pts.append(b)
        if len(run) > 1:
            pts.append(run[-1][1:])
        out.append((run[0][0], pts))
    return out


def main():
    board = pcbnew.LoadBoard(str(PCB))
    ds = board.GetDesignSettings()
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(mm(CLEARANCE))
    nc.SetTrackWidth(mm(TRACK))
    nc.SetViaDiameter(mm(VIA))
    nc.SetViaDrill(mm(DRILL))
    ds.m_MinClearance = mm(CLEARANCE)

    nets, pins, pads = {}, {}, []
    for ref, lib, name, back, by_pad, targets in PARTS:
        fp = place(board, ref, lib, name, back, targets)
        fp.SetValue(name)
        for k, net in enumerate(by_pad):
            pad = fp.FindPadByNumber(str(k + 1))
            p = pad.GetPosition()
            pads.append((net, pcbnew.ToMM(p.x), pcbnew.ToMM(p.y), pad.GetShape() == pcbnew.PAD_SHAPE_RECTANGLE,
                         pcbnew.ToMM(pad.GetSize().x) / 2))
            if net is None:
                continue
            if net not in nets:
                nets[net] = pcbnew.NETINFO_ITEM(board, net)
                board.Add(nets[net])
            pad.SetNet(nets[net])
            pins.setdefault(net, []).append(pads[-1][1:3])

    w, h = g.BOARD
    grid = Grid(w, h)
    ids = {net: k for k, net in enumerate(sorted(nets))}
    # Unconnected pads (net None) block every net
    for net, x, y, rect, r in pads:
        if rect:
            grid.add(ids.get(net, -1), (0, 1), lambda X, Y, x=x, y=y, r=r: np.hypot(np.maximum(abs(X - x) - r, 0), np.maximum(abs(Y - y) - r, 0)),
                     0, (x - r, y - r, x + r, y + r))
        else:
            grid.add(ids.get(net, -1), (0, 1), lambda X, Y, x=x, y=y: np.hypot(X - x, Y - y), r, (x, y, x, y))
    for x, y, r in KEEPOUT:
        grid.add(-1, (0, 1), lambda X, Y, x=x, y=y: np.hypot(X - x, Y - y), r - CLEARANCE, (x, y, x, y))
    # 0.5 mm from the edge and the 1 mm chamfers
    X, Y = np.meshgrid(grid.xs, grid.ys)
    edge = np.minimum.reduce([X, Y, w - X, h - Y, (X + Y - 1) / 2 ** 0.5, (w - X + Y - 1) / 2 ** 0.5,
                              (X + h - Y - 1) / 2 ** 0.5, (w - X + h - Y - 1) / 2 ** 0.5])
    for arr in grid.track + [grid.via]:
        arr[edge < 0.5 + TRACK / 2] = -2

    def cell(x, y):
        return round(x / RES), round(y / RES)

    # Signals first with the longest last, then 3V3 and GND; GND also gets a pour on both layers
    order = sorted((n for n in pins if n not in ("3V3", "GND")),
                   key=lambda n: -max(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a in pins[n] for b in pins[n]))[::-1]
    failed = []
    for net in order + ["3V3", "GND"]:
        ps = sorted(pins[net])
        tree = {(layer, *cell(*ps[0])) for layer in (0, 1)}
        todo = ps[1:]
        while todo:
            todo.sort(key=lambda p: min(abs(cell(*p)[0] - s[1]) + abs(cell(*p)[1] - s[2]) for s in tree))
            p = todo.pop(0)
            path = astar(grid, ids[net], tree, cell(*p))
            if path is None:
                failed.append((net, p))
                continue
            for layer, pts in simplify(path):
                for (i0, j0), (i1, j1) in zip(pts, pts[1:]):
                    a, b = (i0 * RES, j0 * RES), (i1 * RES, j1 * RES)
                    t = pcbnew.PCB_TRACK(board)
                    t.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
                    t.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
                    t.SetWidth(mm(TRACK))
                    t.SetLayer(pcbnew.F_Cu if layer == 0 else pcbnew.B_Cu)
                    t.SetNet(nets[net])
                    board.Add(t)
                    grid.add(ids[net], (layer,), seg_dist(*a, *b), TRACK / 2, (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])))
            for s, n in zip(path, path[1:]):
                if s[0] != n[0]:
                    x, y = s[1] * RES, s[2] * RES
                    v = pcbnew.PCB_VIA(board)
                    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                    v.SetWidth(mm(VIA))
                    v.SetDrill(mm(DRILL))
                    v.SetNet(nets[net])
                    board.Add(v)
                    grid.add(ids[net], (0, 1), lambda X, Y, x=x, y=y: np.hypot(X - x, Y - y), VIA / 2, (x, y, x, y))
            tree |= {(layer, i, j) for layer, i, j in path} | {(1 - layer, i, j) for layer, i, j in (path[0], path[-1])}

    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(nets["GND"])
        z.SetLocalClearance(mm(0.25))
        z.SetMinThickness(mm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        o = z.Outline()
        o.NewOutline()
        for x, y in [(0.3, 0.3), (w - 0.3, 0.3), (w - 0.3, h - 0.3), (0.3, h - 0.3)]:
            o.Append(mm(x), mm(y))
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(str(PCB))
    print(f"{len(order) + 2} nets, {sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)} vias")
    for net, xy in failed:
        print(f"unrouted: {net} at {xy}")


if __name__ == "__main__":
    main()

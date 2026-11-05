import json
from collections import defaultdict
from itertools import combinations, pairwise
from pathlib import Path

import numpy as np
import shapely as sh
import trimesh
from shapely.affinity import scale
from shapely.geometry import Point, Polygon, box
from shapely.ops import polygonize

OUT = Path(__file__).resolve().parent
P = json.loads((OUT / "case_dimensions.json").read_text())
C = P["case"]
O = C["wall"] + C["fit_clearance"]
PW, PD = P["carrier"]["size"]
W, D = PW + 2 * O, PD + 2 * O
cam, pico, lcd, btn = P["camera"], P["pico"], P["lcd"], P["buttons"]
CAM_TIP = C["wall"] + cam["face_gap"]
CAM_FRONT = CAM_TIP + cam["lens_height"]
CAM_BACK = CAM_FRONT + cam["pcb_thickness"]
PCB_Z = CAM_BACK + cam["standoff"]
PCB_TOP = PCB_Z + P["carrier"]["thickness"]
PICO_BACK = PCB_Z - pico["standoff"]
PICO_FACE = PICO_BACK - pico["pcb_thickness"]
LCD_BOTTOM = PCB_TOP + lcd["standoff"]
LCD_TOP = LCD_BOTTOM + lcd["pcb_thickness"]
H = LCD_TOP + lcd["glass_height"] + lcd["face_gap"]
TOP = H + C["face_thickness"]
SCREWS = [(x + O, y + O) for x, y in P["carrier"]["screws"]]
OUTLINE = [
    (O + 1, O),
    (W - O - 1, O),
    (W - O, O + 1),
    (W - O, D - O - 1),
    (W - O - 1, D - O),
    (O + 1, D - O),
    (O, D - O - 1),
    (O, O + 1),
]
# B-side boards are seen from the front, so the camera drawing (lens side) is mirrored in x
CX, CY = cam["xy"][0] + O, cam["xy"][1] + O
CAM_HOLES = [(CX + cam["size"] - x, CY + y) for x, y in cam["holes"]]
LENS = (CX + cam["size"] - cam["lens"][0], CY + cam["lens"][1])
PX, PY = pico["xy"][0] + O, pico["xy"][1] + O
PICO_HOLES = [(PX + x, PY + y) for x, y in pico["holes"]]
LX, LY = lcd["xy"][0] + O, lcd["xy"][1] + O
LCD_HOLES = [(LX + x, LY + y) for x, y in lcd["holes"]]
# SW1-SW6 in schematic order: up, down, left, right, select, reject
(DX, DY), PITCH = btn["dpad"], btn["pitch"]
BUTTONS = [(DX + O + i * PITCH, DY + O + j * PITCH) for i, j in ((0, -1), (0, 1), (-1, 0), (1, 0), (0, 0))]
BUTTONS.append((btn["reject"][0] + O, btn["reject"][1] + O))
KEYS = [("上", "#cae0e1"), ("下", "#cae0e1"), ("左", "#cae0e1"), ("右", "#cae0e1"), ("決定", "#e5ac56"), ("拒否", "#c96f5b")]


def disk(x, y, radius):
    return Point(x, y).buffer(radius, quad_segs=12)


def rounded(x0, y0, x1, y1, radius):
    return box(x0 + radius, y0 + radius, x1 - radius, y1 - radius).buffer(
        radius, quad_segs=12
    )


def op(poly, z0, z1, cut=False):
    if z1 <= z0:
        raise ValueError(f"Nonpositive extrusion height: {z0}, {z1}")
    return ("cut" if cut else "add", poly, round(z0, 6), round(z1, 6))


def slices(ops):
    zs = sorted({z for _, _, a, b in ops for z in (a, b)})
    result = []
    for lo, hi in pairwise(zs):
        poly = Polygon()
        for action, footprint, a, b in ops:
            if a <= (lo + hi) / 2 <= b:
                poly = (
                    poly.union(footprint)
                    if action == "add"
                    else poly.difference(footprint)
                )
        result.append((lo, hi, poly))
    return result


def mesh_slices(layers):
    boundaries = sh.union_all([p.boundary for _, _, p in layers if not p.is_empty])
    xy = []
    for cell in polygonize(boundaries):
        for tri in sh.get_parts(sh.constrained_delaunay_triangles(cell)):
            coords = np.asarray(tri.exterior.coords[:3])
            if np.cross(coords[1] - coords[0], coords[2] - coords[0]) < 0:
                coords = coords[::-1]
            xy.append(coords)
    xy = np.asarray(xy)
    centers = sh.points(xy.mean(axis=1))
    occupied = np.array([sh.covers(p, centers) for _, _, p in layers])
    edges = defaultdict(list)
    for i, triangle in enumerate(xy):
        for e in range(3):
            key = tuple(
                sorted(tuple(np.round(v, 7)) for v in triangle[[e, (e + 1) % 3]])
            )
            edges[key].append((i, e))
    neighbors = {}
    for entries in edges.values():
        if len(entries) == 2:
            (a, e), (b, f) = entries
            neighbors[a, e], neighbors[b, f] = b, a
        elif len(entries) != 1:
            raise ValueError("Non-manifold planar subdivision")
    faces = []
    for k, (lo, hi, _) in enumerate(layers):
        for i in np.flatnonzero(occupied[k]):
            low = np.column_stack((xy[i], np.full(3, lo)))
            high = np.column_stack((xy[i], np.full(3, hi)))
            if k == 0 or not occupied[k - 1, i]:
                faces.append(low[::-1])
            if k == len(layers) - 1 or not occupied[k + 1, i]:
                faces.append(high)
            for e in range(3):
                other = neighbors.get((i, e))
                if other is None or not occupied[k, other]:
                    f = (e + 1) % 3
                    faces.extend(
                        ([low[e], low[f], high[f]], [low[e], high[f], high[e]])
                    )
    vertices = np.asarray(faces).reshape(-1, 3)
    return trimesh.Trimesh(
        vertices=vertices, faces=np.arange(len(vertices)).reshape(-1, 3), process=True
    )


def make_parts():
    parts = []

    def add(name, label, ops, color, group, printable=False):
        parts.append(
            {
                "name": name,
                "label": label,
                "ops": ops,
                "color": color,
                "group": group,
                "printable": printable,
            }
        )

    wall, clearance = C["wall"], C["fit_clearance"]
    screw = P["carrier"]["screw"]
    base = [
        op(rounded(0, 0, W, D, 4), 0, H),
        op(rounded(wall, wall, W - wall, D - wall, 1.6), wall, H + 1, True),
        op(disk(*LENS, cam["window_diameter"] / 2), -1, wall + 1, True),
    ]
    # Each screw rests on the board it passes through, or on the carrier where nothing is behind it
    rests = {SCREWS[0]: CAM_FRONT, SCREWS[1]: PCB_Z, SCREWS[2]: PICO_FACE}
    for x, y in SCREWS:
        top = rests.get((x, y), PICO_FACE)
        if (x, y) == SCREWS[3]:
            # the Micro-USB shell passes 1.6 mm from this hole
            base.extend([op(disk(x, y, 2.2), wall, PICO_FACE - pico["usb_height"] - 0.2), op(disk(x, y, 1.6), wall, top)])
        else:
            base.append(op(disk(x, y, 2.2 if top == PICO_FACE else 2.6), wall, top))
        base.extend(
            [
                op(disk(x, y, screw["clearance"]), -1, top + 1, True),
                op(disk(x, y, screw["head"]), -1, screw["head_depth"], True),
            ]
        )
    for x, y in CAM_HOLES:
        if not np.isclose([x, y], SCREWS[0]).all():
            base.append(op(disk(x, y, 2), wall, CAM_FRONT))
    for x, y in PICO_HOLES[:1] + PICO_HOLES[2:3]:
        base.append(op(disk(x, y, 1.5), wall, PICO_FACE))
    usb_x, usb_z = PX + 10.5, PICO_FACE - pico["usb_height"] / 2
    base.append(op(box(usb_x - 5.4, D - wall - 1, usb_x + 5.4, D + 1), max(usb_z - 3.4, wall), usb_z + 3.4, True))
    base.append(op(box(usb_x - 3.5, -1, usb_x + 3.5, wall + 1), PICO_FACE - pico["debug_height"] - 0.6, PICO_FACE + 0.4, True))
    bootsel = (PX + pico["bootsel"][0], PY + 51 - pico["bootsel"][1])
    base.append(op(disk(*bootsel, 1.6), -1, wall + 1, True))
    add("base", "背面ケース", base, "#455c68", "base", True)

    size = cam["size"]
    cam_board = [op(box(CX, CY, CX + size, CY + size), CAM_FRONT, CAM_BACK)]
    for x, y in CAM_HOLES:
        cam_board.append(op(disk(x, y, 1.6), CAM_FRONT - 0.1, CAM_BACK + 0.1, True))
    add("camera_board", "OV7675 B0070・レンズは背面向き", cam_board, "#d74238", "camera")
    half = cam["lens_body"] / 2
    add("camera_lens", "カメラモジュール・高さは要実測", [op(box(LENS[0] - half, LENS[1] - half, LENS[0] + half, LENS[1] + half), CAM_TIP + 0.15, CAM_FRONT)], "#202b36", "camera")
    add("camera_glass", "カメラ光学面", [op(disk(*LENS, 2.5), CAM_TIP, CAM_TIP + 0.15)], "#397986", "camera")
    (hx, hy), rows = cam["pins"]["first"], cam["pins"]["pitch_rows"]
    header = box(CX + size - hx + 1.27, CY + hy + rows - 1.27, CX + size - hx - 2.54 * cam["pins"]["count"] + 1.27, CY + hy + 1.27)
    add("camera_header", "カメラ2×10ヘッダ・キャリアへ直付け", [op(header, CAM_BACK, PCB_Z)], "#252c32", "camera")
    spacer = [op(disk(*SCREWS[0], 2.2), CAM_BACK, PCB_Z), op(disk(*SCREWS[0], screw["clearance"]), CAM_BACK - 0.1, PCB_Z + 0.1, True)]
    add("camera_spacer", "カメラ下角のスペーサー・はんだ付け前に挟む", spacer, "#83999c", "retainer", True)
    # the holes away from the header sit under the D-pad, so a peg locates each spacer and the back case clamps it
    for i, (x, y) in enumerate(CAM_HOLES[:2], 1):
        peg = [op(disk(x, y, 2.2), CAM_BACK, PCB_Z), op(disk(x, y, 1.4), CAM_FRONT + 0.2, CAM_BACK)]
        add(f"camera_peg_{i}", "カメラ上角のスペーサー・ピンを穴へ", peg, "#83999c", "retainer", True)

    pico_ops = [op(box(PX, PY, PX + 21, PY + 51), PICO_FACE, PICO_BACK)]
    for x, y in PICO_HOLES:
        pico_ops.append(op(disk(x, y, 1.05), PICO_FACE - 0.1, PICO_BACK + 0.1, True))
    add("pico", "Pico 2 H・部品面は背面側", pico_ops, "#32976d", "pico")
    add("pico_headers", "Pico 2 Hのヘッダ・キャリアへ直付け", [op(box(PX + x - 1.25, PY + 0.1, PX + x + 1.25, PY + 50.9), PICO_BACK, PCB_Z) for x in (1.61, 19.39)], "#343b42", "pico")
    add("rp2350", "RP2350", [op(box(PX + 7, PY + 22, PX + 14, PY + 29), PICO_FACE - 0.9, PICO_FACE)], "#233038", "pico")
    add("bootsel", "BOOTSEL・背面の穴から押す", [op(box(bootsel[0] - 1.5, bootsel[1] - 2, bootsel[0] + 1.5, bootsel[1] + 2), PICO_FACE - 1.5, PICO_FACE)], "#f1eade", "pico")
    usb = [
        op(box(usb_x - 4, PY + 51 - 4.2, usb_x + 4, PY + 51 + pico["usb_overhang"]), PICO_FACE - pico["usb_height"], PICO_FACE),
        op(box(usb_x - 3.25, PY + 51 - 3, usb_x + 3.25, PY + 51 + pico["usb_overhang"] + 0.1), PICO_FACE - pico["usb_height"] + 0.45, PICO_FACE - 0.45, True),
    ]
    add("usb", "Micro-USB・下辺の開口へ", usb, "#aeb8bb", "pico")
    add("debug", "SWDコネクタ・上辺の開口へ", [op(box(usb_x - 2.5, PY, usb_x + 2.5, PY + 4.3), PICO_FACE - pico["debug_height"], PICO_FACE)], "#f1eade", "pico")

    lid = [op(rounded(0, 0, W, D, 4), H, TOP)]
    lip = rounded(wall + clearance, wall + clearance, W - wall - clearance, D - wall - clearance, 2)
    lip = lip.difference(rounded(wall + clearance + 1.2, wall + clearance + 1.2, W - wall - clearance - 1.2, D - wall - clearance - 1.2, 1))
    for x, y in SCREWS:
        lip = lip.difference(disk(x, y, 3))
    lid.append(op(lip, H - 1.8, H))
    for x, y in SCREWS:
        lid.extend([op(disk(x, y, 2.3), PCB_TOP, H), op(disk(x, y, screw["pilot"]), PCB_TOP - 0.1, TOP - 0.8, True)])

    lw, ld = lcd["size"]
    lcd_ops = [op(box(LX, LY, LX + lw, LY + ld), LCD_BOTTOM, LCD_TOP)]
    for x, y in LCD_HOLES:
        lcd_ops.append(op(disk(x, y, lcd["hole_diameter"] / 2), LCD_BOTTOM - 0.1, LCD_TOP + 0.1, True))
        lid.extend([op(disk(x, y, 1.75), LCD_TOP, H), op(disk(x, y, 0.8), LCD_BOTTOM + 0.2, LCD_TOP)])
    gx, gy, gw, gd = lcd["glass"]
    ax, ay, aw, ad = lcd["active"]
    m = lcd["window_margin"]
    lid.append(op(box(LX + ax - m, LY + ay - m, LX + ax + aw + m, LY + ay + ad + m), H - 1, TOP + 1, True))
    add("lcd_board", "LCD基板・ヘッダをキャリアへ直付け", lcd_ops, "#175989", "lcd")
    add("lcd_glass", "LCDガラス", [op(box(LX + gx, LY + gy, LX + gx + gw, LY + gy + gd), LCD_TOP, H - lcd["face_gap"] - 0.03)], "#131d27", "lcd")
    add("lcd_active", "表示域 27.72 mm角", [op(box(LX + ax, LY + ay, LX + ax + aw, LY + ay + ad), H - lcd["face_gap"] - 0.03, H - lcd["face_gap"])], "#91c7ce", "lcd")
    (px1, py1), n = lcd["pins"]["first"], lcd["pins"]["count"]
    add("lcd_header", "LCDヘッダ・上辺", [op(box(LX + px1 - 1.27, LY + py1 - 1.25, LX + px1 + 2.54 * (n - 1) + 1.27, LY + py1 + 1.25), PCB_TOP, LCD_BOTTOM)], "#252c32", "lcd")

    board = [op(Polygon(OUTLINE), PCB_Z, PCB_TOP)]
    for x, y in SCREWS:
        board.append(op(disk(x, y, screw["clearance"]), PCB_Z - 0.1, PCB_TOP + 0.1, True))
    body_top = PCB_TOP + btn["body_height"]
    tip = PCB_TOP + btn["switch_height"]
    (boss, boss_h), (key, key_h) = btn["stem_boss"], btn["stem_top"]
    flange = H - btn["free_gap"]
    for i, (bx, by) in enumerate(BUTTONS):
        lid.append(op(disk(bx, by, 2.75), H - 0.1, TOP + 1, True))
        # the cap rests on the 2.4 mm square stem top; its flange stops just under the cover
        cap = [
            op(disk(bx, by, 3.6), flange - 1, flange),
            op(disk(bx, by, 2.5), flange, TOP + 0.8),
            op(disk(bx, by, boss / 2 + 0.25), flange - 1.1, flange - 0.4, True),
            op(rounded(bx - key / 2 - 0.15, by - key / 2 - 0.15, bx + key / 2 + 0.15, by + key / 2 + 0.15, 0.2), flange - 0.5, tip, True),
        ]
        add(f"button_{i + 1}", f"{KEYS[i][0]}ボタン", cap, KEYS[i][1], "button", True)
        add(
            f"switch_{i + 1}",
            "TVDP01-G73BB",
            [
                op(box(bx - 3, by - 3, bx + 3, by + 3), PCB_TOP, body_top),
                op(disk(bx, by, boss / 2), body_top, body_top + boss_h),
                op(disk(bx, by, 0.75), body_top + boss_h, tip - key_h),
                op(box(bx - key / 2, by - key / 2, bx + key / 2, by + key / 2), tip - key_h, tip),
            ],
            "#232c34",
            "board",
        )
    add("lid", "前カバー", lid, "#e4e6dc", "lid", True)
    add("carrier", "キャリア基板", board, "#287567", "board")
    add(
        "case_screw_heads",
        "M2×16 なべ小ねじ・背面から",
        [op(disk(x, y, 1.9), 0, screw["head_depth"]) for x, y in SCREWS],
        "#a6b3b9",
        "base",
    )
    return parts


def overlap(a, b):
    volume = 0.0
    for lo, hi, p in a:
        for low, high, q in b:
            height = min(hi, high) - max(lo, low)
            if height > 1e-7:
                volume += p.intersection(q).area * height
    return volume


def scad_source(parts):
    source = 'part = "assembly";\n// Generated from case_dimensions.json. Units: mm.\n'
    for part in parts:
        source += f"module {part['name']}() {{ union() {{\n"
        for lo, hi, footprint in part["layers"]:
            for poly in sh.get_parts(footprint):
                if poly.is_empty:
                    continue
                rings = [list(poly.exterior.coords)[:-1]] + [
                    list(r.coords)[:-1] for r in poly.interiors
                ]
                points, paths = [], []
                for ring in rings:
                    paths.append(list(range(len(points), len(points) + len(ring))))
                    points.extend([[round(x, 6), round(y, 6)] for x, y in ring])
                source += f"translate([0,0,{lo}]) linear_extrude({hi - lo}) polygon(points={json.dumps(points)},paths={json.dumps(paths)});\n"
        source += "} }\n"
    source += 'if (part == "assembly") {\n'
    for part in parts:
        source += f'color("{part["color"]}") {part["name"]}();\n'
    source += "}\n"
    for part in parts:
        if part["printable"]:
            bounds = part["mesh"].bounds
            if part["name"] == "lid" or part["name"].startswith("button_"):
                transform = f"translate([{-bounds[0, 0]},{bounds[1, 1]},{bounds[1, 2]}]) rotate([180,0,0]) "
            else:
                transform = f"translate({(-bounds[0]).tolist()}) "
            source += f'if(part == "{part["name"]}") {transform}{part["name"]}();\n'
    return source


def main():
    from export_formats import export_formats
    from render_case import export_views

    parts = make_parts()
    report = {
        "units": "mm",
        "assumptions": P["assumptions"],
        "parts": [],
        "interferences": [],
    }
    scene = trimesh.Scene()
    for part in parts:
        # KiCad's y runs down; flip it so the STL is right-handed and not the mirror image of the boards
        part["ops"] = [(a, scale(p, 1, -1, origin=(0, D / 2)), lo, hi) for a, p, lo, hi in part["ops"]]
        part["layers"] = slices(part["ops"])
        mesh = mesh_slices(part["layers"])
        part["mesh"] = mesh
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError(f"Invalid mesh: {part['name']}")
        expected = sum((hi - lo) * p.area for lo, hi, p in part["layers"])
        if not np.isclose(mesh.volume, expected, rtol=1e-6, atol=1e-5):
            raise ValueError(f"Volume mismatch: {part['name']}")
        mesh.visual.face_colors = [
            int(part["color"][i : i + 2], 16) for i in (1, 3, 5)
        ] + [255]
        scene.add_geometry(mesh, node_name=part["name"], geom_name=part["name"])
        if part["printable"]:
            if (
                len(
                    trimesh.graph.connected_components(
                        mesh.face_adjacency,
                        nodes=np.arange(len(mesh.faces)),
                        engine="networkx",
                    )
                )
                != 1
            ):
                raise ValueError(f"Disconnected printable: {part['name']}")
            printed = mesh.copy()
            if part["name"] == "lid" or part["name"].startswith("button_"):
                printed.apply_transform(
                    trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
                )
            printed.apply_translation(-printed.bounds[0])
            part["print_mesh"] = printed
            name = "front" if part["name"] == "lid" else part["name"]
            printed.export(OUT / f"pico2h_case_{name}.stl")
            exported = trimesh.load_mesh(OUT / f"pico2h_case_{name}.stl", process=True)
            if not exported.is_watertight or not exported.is_winding_consistent:
                raise ValueError(f"STL roundtrip failed: {name}")
        report["parts"].append(
            {
                "name": part["name"],
                "watertight": bool(mesh.is_watertight),
                "volume_mm3": round(mesh.volume, 3),
                "bounds": mesh.bounds.round(3).tolist(),
                "printable": part["printable"],
            }
        )
        print(part["name"], len(mesh.faces), "triangles", flush=True)
    checked = 0
    for a, b in combinations(parts, 2):
        if a["name"] == "case_screw_heads" or b["name"] == "case_screw_heads":
            continue
        checked += 1
        volume = overlap(a["layers"], b["layers"])
        if volume > 1e-4:
            report["interferences"].append(
                {"a": a["name"], "b": b["name"], "volume_mm3": round(volume, 4)}
            )
    report["checked_pairs"] = checked
    report["scope"] = (
        "Nominal simplified solid envelopes only. Wiring bends, insertion paths, optical field and physical tolerances need physical confirmation."
    )
    (OUT / "fit_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )
    if report["interferences"]:
        raise ValueError(report["interferences"])
    (OUT / "pico2h_case.scad").write_text(scad_source(parts))
    scene.export(OUT / "assembly.glb")
    # the VRML, previews and viewer draw y downwards like KiCad, so they get the flip undone
    flip = np.diag([1.0, -1.0, 1.0, 1.0])
    flip[1, 3] = D
    shown = [{**p, "mesh": p["mesh"].copy().apply_transform(flip)} for p in parts]
    export_formats(shown, OUT, (O, O, PCB_TOP))
    export_views(shown, (W, D, TOP), OUT)
    print(
        f"PASS: {checked} nominal body pairs, closed printable meshes and STL roundtrips"
    )


if __name__ == "__main__":
    main()

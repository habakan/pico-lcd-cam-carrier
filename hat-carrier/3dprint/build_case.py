"""Builds the Rev E case around the HAT carrier: STL to print, a fit report and preview images."""

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, box

OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(OUT.parent), str(OUT.parents[1] / "pico2h-carrier" / "3dprint")]
import generate as layout  # noqa: E402
from build_case_stl import mesh_slices, op, overlap, rounded, slices  # noqa: E402
from render_case import render  # noqa: E402

BW, BD = layout.BOARD
WALL, CLEARANCE = 2.4, 0.3
O = WALL + CLEARANCE
W, D = BW + 2 * O, BD + 2 * O

# Back to front. Camera and Pico sit on 8.5 mm sockets over their own 2.5 mm header plastic
CAM_TIP = WALL + 0.6
CAM_FRONT = CAM_TIP + 3.5  # lens height, to measure
CAM_BACK = CAM_FRONT + 1.6
PCB_Z = CAM_BACK + 2.5 + 8.5
PCB_TOP = PCB_Z + 1.6
PICO_BACK = PCB_Z - 8.5 - 2.5
PICO_FACE = PICO_BACK - 1.0
USB_H = 2.9
# The HAT's 7.5 mm socket is read from SeedSigner's Orange Pill case (10 mm spacers)
HAT_BOTTOM = PCB_TOP + 2.5 + 7.5
HAT_TOP = HAT_BOTTOM + 1.6
H = HAT_TOP


def opz(u):
    """Height of a plane of Orange Pill's OP_Upper.stl, whose HAT face is at u = 1.5 and outer face at u = -2.5."""
    return HAT_TOP + 1.5 - u


hx, hy = layout.HAT_XY


def opxy(x, y):
    """A point of OP_Upper.stl in carrier coordinates; its origin is the HAT's centre and seen from the front y runs down."""
    return hx + 32.5 + x, hy + 15.1 + y


# The front copies OP_Upper so Orange Pill's caps fit unchanged: the cover rests on the HAT and pockets clear its parts
TOP = opz(-2.5)
LCD_TOP = opz(-0.2)
KEY_TOP = opz(-1.5)  # where a cap's flange sits when pushed up to the cover
STICK = opxy(-25.34, 0.35)
STICK_BODY, KNOB_TIP, CAP_BOTTOM = HAT_TOP + 1.2, HAT_TOP + 3.4, HAT_TOP + 1.2
KEYS = [opxy(24.5, y) for y in (-5.9, 0, 5.9)]
ACTIVE = opxy(-1.25, 0.25)
HAT_HOLES = [(hx + x, hy + y) for x, y in layout.HAT_HOLES]
HAT_CORNER = (hx + 61.5, hy + 3.5)
px, py = layout.PICO_XY
PICO_MID = py + 10.5
BOOTSEL = (px + 11.7, py + 7.0)
cx, cy = layout.CAMERA_XY
LENS = (cx + 15.24, cy + 30.5 - 12.65)
J3 = (hx + 32.5 - 25.4, hy + 26.7 - 2.54, hx + 32.5 + 25.4, hy + 26.7 + 2.54)
J4 = (cx + 3.81 - 1.27, cy, cx + 3.81 + 9 * 2.54 + 1.27, cy + 5.08)


def kbox(x0, y0, x1, y1):
    """A rectangle in carrier coordinates. KiCad's y runs down, so it is flipped to keep the STL right-handed."""
    return box(x0 + O, D - y1 - O, x1 + O, D - y0 - O)


def kdisk(x, y, r):
    return Point(x + O, D - y - O).buffer(r, quad_segs=12)


def make_parts():
    parts = []

    def add(name, label, ops, color, group, printable=False):
        parts.append({"name": name, "label": label, "ops": ops, "color": color, "group": group, "printable": printable})

    base = [
        op(rounded(0, 0, W, D, 4), 0, H),
        op(rounded(WALL, WALL, W - WALL, D - WALL, 1.6), WALL, H + 1, True),
        op(kdisk(*LENS, 6), -1, WALL + 1, True),
        op(kdisk(*BOOTSEL, 1.6), -1, WALL + 1, True),
        op(kbox(-O - 1, PICO_MID - 5.4, -O + WALL + 1, PICO_MID + 5.4), WALL, PICO_FACE - USB_H / 2 + 3.4, True),
    ]
    # Posts press the Pico and camera into their sockets; the Micro-USB shell passes 0.1 mm from the left pair
    for i, (x, y) in enumerate(layout.PICO_HOLES):
        base.append(op(kdisk(x, y, 1.6 if i < 2 else 1.5), WALL, PICO_FACE))
    for x, y in layout.CAMERA_HOLES:
        base.append(op(kdisk(x, y, 2), WALL, CAM_FRONT))
    for x, y in layout.CASE_SCREWS:
        base += [op(kdisk(x, y, 1.1), -1, H, True), op(kdisk(x, y, 2.1), -1, 1.2, True)]
    add("base", "背面ケース", base, "#455c68", "base", True)

    lid = [op(rounded(0, 0, W, D, 4), H, TOP)]
    lip = rounded(O, O, W - O, D - O, 2).difference(rounded(O + 1.2, O + 1.2, W - O - 1.2, D - O - 1.2, 1))
    for x, y in layout.CASE_SCREWS:
        lip = lip.difference(kdisk(x, y, 3))
    # The cover now rests on the HAT, whose top edge is 0.5 mm from the carrier's
    lip = lip.difference(kbox(hx - 0.3, hy - 0.3, hx + 65.3, hy + 30.5))
    lid.append(op(lip, H - 1.8, H))
    for x, y in layout.CASE_SCREWS:
        lid += [op(kdisk(x, y, 2.3), PCB_TOP, H), op(kdisk(x, y, 0.8), PCB_TOP - 0.1, TOP - 0.8, True)]
    def opbox(x, y, w, h):
        cx, cy = opxy(x, y)
        return kbox(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

    # Pockets and holes measured from OP_Upper; the 45 degree chamfers are cut in 0.25 mm steps
    lid += [op(opbox(0.5, 0.25, 32.5, 28.5), H - 1, LCD_TOP, True), op(opbox(-1.25, 0.25, 24, 24.5), H - 1, opz(-1), True),
            op(kdisk(*STICK, 7), H - 1, opz(-1), True),
            op(opbox(25.08, 0, 14.5, 28.5), H - 1, opz(-0.5), True), op(opbox(24.5, 0, 14.5, 19), H - 1, opz(-1.9), True)]
    for k in range(6):
        z0, z1 = opz(-1) + 0.25 * k, opz(-1) + 0.25 * (k + 1)
        lid += [op(opbox(-1.25, 0.25, 24 + 2 * (z1 - opz(-1)), 24.5 + 2 * (z1 - opz(-1))), z0, TOP + 1 if k == 5 else z1, True),
                op(kdisk(*STICK, 6.75 - (z1 - opz(-1))), z0, TOP + 1 if k == 5 else z1, True)]
    lid += [op(kbox(x - 4.25, y - 2.6, x + 4.25, y + 2.6), H - 1, TOP + 1, True) for x, y in KEYS]
    # Screw heads on the HAT's left holes; the right ones and the post sit in the key pocket
    lid += [op(kdisk(x, y, 2.5), H - 1, opz(-0.5), True) for x, y in HAT_HOLES[:2]]
    # The HAT corner without a carrier hole is held by a post, its peg in the HAT's hole
    lid += [op(kdisk(*HAT_CORNER, 2.25), HAT_TOP, opz(-0.5)), op(kdisk(*HAT_CORNER, 1.1), HAT_BOTTOM + 0.2, HAT_TOP)]
    add("lid", "前カバー", lid, "#e4e6dc", "lid", True)

    # Orange Pill's joystick.stl and button.stl, printed from seedsigner/; modelled here only to check the fit
    stick_cap = [
        op(kdisk(*STICK, 6.4), CAP_BOTTOM, CAP_BOTTOM + 1),
        op(kdisk(*STICK, 4.5), CAP_BOTTOM + 1, CAP_BOTTOM + 5),
        op(kdisk(*STICK, 4.97), CAP_BOTTOM + 5, CAP_BOTTOM + 10),
        op(kbox(STICK[0] - 1.12, STICK[1] - 1.12, STICK[0] + 1.12, STICK[1] + 1.12), CAP_BOTTOM - 0.1, CAP_BOTTOM + 2.4, True),
        op(kdisk(*STICK, 2.25), CAP_BOTTOM - 0.1, CAP_BOTTOM + 0.5, True),
    ]
    add("stick_cap", "スティックのキャップ（Orange Pill）", stick_cap, "#e5ac56", "button")
    for i, (x, y) in enumerate(KEYS, 1):
        key = [op(kbox(x - 5.85, y - 2.15, x + 5.85, y + 2.15), KEY_TOP, KEY_TOP + 0.4),
               op(kbox(x - 4, y - 2.35, x + 4, y + 2.35), KEY_TOP + 0.4, KEY_TOP + 4.8)]
        add(f"key_{i}", f"KEY{i} のキャップ（Orange Pill）", key, "#c96f5b" if i == 1 else "#cae0e1", "button")

    carrier = [op(Polygon([(x + O, D - y - O) for x, y in
                           [(1, 0), (BW - 1, 0), (BW, 1), (BW, BD - 1), (BW - 1, BD), (1, BD), (0, BD - 1), (0, 1)]]), PCB_Z, PCB_TOP)]
    carrier += [op(kdisk(x, y, 1.35), PCB_Z - 0.1, PCB_TOP + 0.1, True) for x, y in HAT_HOLES]
    carrier += [op(kdisk(x, y, 1.1), PCB_Z - 0.1, PCB_TOP + 0.1, True) for x, y in layout.CASE_SCREWS]
    add("carrier", "キャリア基板", carrier, "#287567", "board")
    add("j3", "J3 2x20 オスヘッダ", [op(kbox(*J3), PCB_TOP, PCB_TOP + 2.5)], "#252c32", "board")
    add("standoffs", "M2.5 x 10 スペーサーとねじ頭", [op(kdisk(x, y, 2.5), PCB_TOP, HAT_BOTTOM) for x, y in HAT_HOLES]
        + [op(kdisk(x, y, 2.25), PCB_Z - 1.7, PCB_Z) for x, y in HAT_HOLES]
        + [op(kdisk(x, y, 2.25), HAT_TOP, HAT_TOP + 1.7) for x, y in HAT_HOLES], "#a6b3b9", "board")

    hat = [op(kbox(hx, hy, hx + 65, hy + 30.2), HAT_BOTTOM, HAT_TOP)]
    hat += [op(kdisk(x, y, 1.375), HAT_BOTTOM - 0.1, HAT_TOP + 0.1, True) for x, y in HAT_HOLES + [HAT_CORNER]]
    add("hat", "1.3inch LCD HAT", hat, "#175989", "lcd")
    add("hat_socket", "HAT のソケット", [op(kbox(*J3), PCB_TOP + 2.5, HAT_BOTTOM)], "#252c32", "lcd")
    add("lcd_glass", "LCD ガラス", [op(kbox(hx + 17.7, hy + 1.85, hx + 47.2, hy + 28.35), HAT_TOP, LCD_TOP - 0.03)], "#131d27", "lcd")
    add("lcd_active", "表示域 23.4 mm 角", [op(kbox(ACTIVE[0] - 11.7, ACTIVE[1] - 11.7, ACTIVE[0] + 11.7, ACTIVE[1] + 11.7), LCD_TOP - 0.03, LCD_TOP)], "#91c7ce", "lcd")
    add("stick", "ジョイスティック・高さは Orange Pill から推定", [op(kbox(STICK[0] - 3.5, STICK[1] - 3.5, STICK[0] + 3.5, STICK[1] + 3.5), HAT_TOP, STICK_BODY),
                                       op(kbox(STICK[0] - 1, STICK[1] - 1, STICK[0] + 1, STICK[1] + 1), STICK_BODY, KNOB_TIP)], "#aeb8bb", "lcd")
    add("switches", "KEY1-3", [op(kbox(x - 3, y - 1.75, x + 3, y + 1.75), HAT_TOP, KEY_TOP) for x, y in KEYS], "#f1eade", "lcd")

    pico = [op(kbox(px, py, px + 51, py + 21), PICO_FACE, PICO_BACK)]
    pico += [op(kdisk(x, y, 1.05), PICO_FACE - 0.1, PICO_BACK + 0.1, True) for x, y in layout.PICO_HOLES]
    add("pico", "Pico 2 H・部品面は背面側", pico, "#32976d", "pico")
    rows = [py + 1.61, py + 19.39]
    add("pico_sockets", "Pico のヘッダと J1/J2 ソケット", [op(kbox(px + 0.1, y - 1.25, px + 50.9, y + 1.25), PICO_BACK, PCB_Z) for y in rows], "#343b42", "pico")
    add("usb", "Micro-USB・左の壁の開口へ", [op(kbox(px - 1.3, PICO_MID - 4, px + 4.2, PICO_MID + 4), PICO_FACE - USB_H, PICO_FACE)], "#aeb8bb", "pico")
    add("rp2350", "RP2350", [op(kbox(px + 22, PICO_MID - 3.5, px + 29, PICO_MID + 3.5), PICO_FACE - 0.9, PICO_FACE)], "#233038", "pico")
    add("bootsel", "BOOTSEL・背面の穴から押す", [op(kbox(BOOTSEL[0] - 2, BOOTSEL[1] - 1.5, BOOTSEL[0] + 2, BOOTSEL[1] + 1.5), PICO_FACE - 1.5, PICO_FACE)], "#f1eade", "pico")
    add("debug", "SWD コネクタ・カメラを外して使う", [op(kbox(px + 51 - 4.3, PICO_MID - 2.5, px + 51, PICO_MID + 2.5), PICO_FACE - USB_H, PICO_FACE)], "#f1eade", "pico")

    camera = [op(kbox(cx, cy, cx + 30.5, cy + 30.5), CAM_FRONT, CAM_BACK)]
    camera += [op(kdisk(x, y, 1.6), CAM_FRONT - 0.1, CAM_BACK + 0.1, True) for x, y in layout.CAMERA_HOLES]
    add("camera_board", "OV7675 B0070・レンズは背面向き", camera, "#d74238", "camera")
    add("camera_lens", "カメラモジュール・高さは要実測", [op(kbox(LENS[0] - 3.1, LENS[1] - 3.1, LENS[0] + 3.1, LENS[1] + 3.1), CAM_TIP + 0.15, CAM_FRONT)], "#202b36", "camera")
    add("camera_glass", "カメラ光学面", [op(kdisk(*LENS, 2.5), CAM_TIP, CAM_TIP + 0.15)], "#397986", "camera")
    add("camera_socket", "カメラのヘッダと J4 ソケット", [op(kbox(*J4), CAM_BACK, PCB_Z)], "#252c32", "camera")
    return parts


def main():
    parts = make_parts()
    report = {"units": "mm", "outline": [round(W, 2), round(D, 2), round(TOP, 2)], "parts": [], "interferences": []}
    for part in parts:
        part["layers"] = slices(part["ops"])
        mesh = mesh_slices(part["layers"])
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError(f"Invalid mesh: {part['name']}")
        part["mesh"] = mesh
        report["parts"].append({"name": part["name"], "volume_mm3": round(mesh.volume, 3), "bounds": mesh.bounds.round(3).tolist()})
        if part["printable"]:
            if len(mesh.split(only_watertight=False)) != 1:
                raise ValueError(f"Disconnected printable: {part['name']}")
            printed = mesh.copy()
            # the cover prints face down
            if part["name"] == "lid":
                printed.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
            printed.apply_translation(-printed.bounds[0])
            name = {"base": "back", "lid": "front"}[part["name"]]
            printed.export(OUT / f"hat_case_{name}.stl")
            if not trimesh.load_mesh(OUT / f"hat_case_{name}.stl").is_watertight:
                raise ValueError(f"STL roundtrip failed: {name}")
    pairs = list(combinations(parts, 2))
    for a, b in pairs:
        volume = overlap(a["layers"], b["layers"])
        if volume > 1e-4:
            report["interferences"].append({"a": a["name"], "b": b["name"], "volume_mm3": round(volume, 4)})
    report["checked_pairs"] = len(pairs)
    (OUT / "fit_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    # render_case draws y downwards like KiCad, so the previews get the y flip undone
    flip = np.diag([1.0, -1.0, 1.0, 1.0])
    flip[1, 3] = D
    shown = [{**p, "mesh": p["mesh"].copy().apply_transform(flip)} for p in parts]
    for mode, file in (("assembled", "preview.png"), ("inside", "inside.png"), ("exploded", "exploded.png")):
        render(shown, 1400, 900, mode).save(OUT / file)
    if report["interferences"]:
        raise ValueError(report["interferences"])
    print(f"PASS: {W:.1f} x {D:.1f} x {TOP:.1f} mm, {len(pairs)} pairs without overlap")


if __name__ == "__main__":
    main()

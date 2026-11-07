"""Writes the Rev E schematic, symbol library and mechanical PCB draft. Run from anywhere."""

import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parent
NS = uuid.UUID("6f1d2a8e-4b1c-4e55-9a51-3c1f0d7e2b40")
ROOT = str(uuid.uuid5(NS, "root"))
FONT = "(effects (font (size 1.27 1.27)))"

# Pico 2 H physical pins 1-20, then 40-21 from the USB end; None is left unconnected
PICO_LEFT = ["LCD_RES", "BTN_C", "GND", "CAM_D0", "CAM_D1", "CAM_D2", "CAM_D3", "GND", "CAM_D4", "CAM_D5",
             "CAM_D6", "CAM_D7", "GND", "CAM_PCLK", "CAM_HREF", "CAM_VSYNC", "BTN_UP", "GND", "CAM_SDA", "CAM_SCL"]
PICO_RIGHT = [None, None, "GND", None, "3V3", None, "BTN_B", None, "BTN_REJECT", "BTN_SELECT",
              None, "BTN_RIGHT", "GND", "CAM_XCLK", "BTN_LEFT", "LCD_MOSI", "LCD_SCK", "GND", "BTN_DOWN", "LCD_DC"]
PICO_RIGHT_NAMES = ["VBUS", "VSYS", "GND", "3V3_EN", "3V3_OUT", "ADC_VREF", "GP28", "AGND", "GP27", "GP26",
                    "RUN", "GP22", "GND", "GP21", "GP20", "GP19", "GP18", "GND", "GP17", "GP16"]
# The HAT's 40-pin socket, named after Waveshare's schematic. RST goes to GP0 as in seedsigner-pico, BL is tied
# high and CS low; 5V (pins 2 and 4) stays unconnected because the HAT runs from 3.3V
HAT = {1: ("3V3", "3V3"), 2: ("5V", None), 3: ("BCM2", None), 4: ("5V", None), 5: ("BCM3", None),
       6: ("GND", "GND"), 7: ("BCM4", None), 8: ("BCM14", None), 9: ("GND", "GND"), 10: ("BCM15", None),
       11: ("BCM17", None), 12: ("BCM18", None), 13: ("LCD_RST", "LCD_RES"), 14: ("GND", "GND"),
       15: ("BCM22", None), 16: ("BCM23", None), 17: ("3V3", "3V3"), 18: ("LCD_BL", "3V3"),
       19: ("LCD_DIN", "LCD_MOSI"), 20: ("GND", "GND"), 21: ("BCM9", None), 22: ("LCD_DC", "LCD_DC"),
       23: ("LCD_CLK", "LCD_SCK"), 24: ("LCD_CS", "GND"), 25: ("GND", "GND"), 26: ("BCM7", None),
       27: ("ID_SD", None), 28: ("ID_SC", None), 29: ("KEY_LEFT", "BTN_LEFT"), 30: ("GND", "GND"),
       31: ("KEY_UP", "BTN_UP"), 32: ("BCM12", None), 33: ("KEY_PRESS", "BTN_SELECT"), 34: ("GND", "GND"),
       35: ("KEY_DOWN", "BTN_DOWN"), 36: ("KEY3", "BTN_C"), 37: ("KEY_RIGHT", "BTN_RIGHT"),
       38: ("KEY2", "BTN_B"), 39: ("GND", "GND"), 40: ("KEY1", "BTN_REJECT")}
CAMERA = ["3V3", "GND", "CAM_SCL", "CAM_SDA", "CAM_VSYNC", "CAM_HREF", "CAM_PCLK", "CAM_XCLK", "CAM_D7", "CAM_D6",
          "CAM_D5", "CAM_D4", "CAM_D3", "CAM_D2", "CAM_D1", "CAM_D0", None, None, "3V3", "GND"]
CAMERA_NAMES = ["VCC", "GND", "SCL", "SDA", "VS", "HS", "PCLK", "XCLK", "D7", "D6",
                "D5", "D4", "D3", "D2", "D1", "D0", "NC", "NC", "PEN", "PDN"]


def uid(*key):
    return str(uuid.uuid5(NS, "/".join(map(str, key))))


def symbol(name, desc, fp_filter, names, two_columns, lib=""):
    """One column of pins on the left, or odd pins left and even pins right like a 2-row header."""
    rows = (len(names) + 1) // 2 if two_columns else len(names)
    top = (rows - 1) * 1.27
    half = 3.81 if two_columns else 1.27
    pins = []
    for i, pin_name in enumerate(names):
        right = two_columns and i % 2
        row = i // 2 if two_columns else i
        x = (half + 3.81) * (1 if right else -1)
        pins.append(f'    (pin passive line (at {x:.2f} {top - row * 2.54:.2f} {180 if right else 0}) (length 3.81)\n'
                    f'      (name "{pin_name}" {FONT}) (number "{i + 1}" {FONT}))')
    return "\n".join([
        f'(symbol "{lib}{name}" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)',
        f'  (property "Reference" "J" (at 0 0 0) {FONT})',
        f'  (property "Value" "{name}" (at 0 0 0) {FONT})',
        f'  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        f'  (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        f'  (property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        f'  (property "ki_fp_filters" "{fp_filter}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        f'  (symbol "{name}_1_1"',
        f'    (rectangle (start {-half} {top + 2.54:.2f}) (end {half} {-top - 2.54:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))',
        *pins, "  )", ")"])


SYMBOLS = [
    ("PicoLeft", "Pico 2 H header row, physical pins 1 to 20", "*1x20*",
     [f"GP{n}" if n is not None else "GND" for n in (0, 1, None, 2, 3, 4, 5, None, 6, 7, 8, 9, None, 10, 11, 12, 13, None, 14, 15)],
     False, PICO_LEFT),
    ("PicoRight", "Pico 2 H header row, physical pins 40 to 21 from the USB end", "*1x20*",
     PICO_RIGHT_NAMES, False, PICO_RIGHT),
    ("LCD_HAT_1in3", "Waveshare 1.3inch LCD HAT 2x20 socket, Raspberry Pi numbering", "*2x20*",
     [HAT[n][0] for n in range(1, 41)], True, [HAT[n][1] for n in range(1, 41)]),
    ("Camera_B0070", "Arducam B0070 2x10 header; odd pins are the lower row seen from the lens", "*2x10*",
     CAMERA_NAMES, True, CAMERA),
]
# ref, symbol, value, footprint, schematic position, dnp
PARTS = [
    ("J1", "PicoLeft", "Pico 2 H left row (pins 1-20)", "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical", (101.6, 96.52), False),
    ("J2", "PicoRight", "Pico 2 H right row (pins 40-21)", "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical", (190.5, 96.52), False),
    ("J3", "LCD_HAT_1in3", "Waveshare 1.3inch LCD HAT", "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical", (299.72, 104.14), False),
    ("J4", "Camera_B0070", "OV7675 / Arducam B0070", "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical", (109.22, 205.74), False),
]


def schematic():
    lib = {s[0]: s for s in SYMBOLS}
    out = ['(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0")',
           f'  (uuid "{ROOT}")', '  (paper "A3")',
           '  (title_block (title "bitwasm-signer HAT carrier") (date "2026-11-05") (rev "E"))', "  (lib_symbols"]
    out += [symbol(n, d, f, names, two, "HatCarrier:") for n, d, f, names, two, _ in SYMBOLS]
    out.append("  )")
    out.append(f'  (text "bitwasm-signer HAT carrier | connector-level schematic draft" (at 210 25 0) '
               f'(effects (font (size 2.54 2.54))) (uuid "{uid("title")}"))')
    out.append(f'  (text "Every board plugs in: Pico 2 H and B0070 into sockets on the back, the HAT onto J3 on the front. '
               f'Only J3 is a male header." (at 210 31 0) {FONT} (uuid "{uid("note")}"))')
    for ref, sym, value, fp, (sx, sy), dnp in PARTS:
        _, _, _, names, two, nets = lib[sym]
        rows = (len(names) + 1) // 2 if two else len(names)
        top = (rows - 1) * 1.27
        out += [f'  (symbol (lib_id "HatCarrier:{sym}") (at {sx} {sy} 0) (unit 1)',
                f'    (in_bom {"no" if dnp else "yes"}) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{uid(ref)}")',
                f'    (property "Reference" "{ref}" (at {sx + 8} {sy - top - 6:.2f} 0) {FONT[:-1]} (justify left)))',
                f'    (property "Value" "{value}" (at {sx + 8} {sy - top - 3.46:.2f} 0) {FONT[:-1]} (justify left)))',
                f'    (property "Footprint" "{fp}" (at {sx} {sy} 0) (effects (font (size 1.27 1.27)) hide))',
                f'    (property "Datasheet" "~" (at {sx} {sy} 0) (effects (font (size 1.27 1.27)) hide))']
        out += [f'    (pin "{i + 1}" (uuid "{uid(ref, i + 1)}"))' for i in range(len(names))]
        out += [f'    (instances (project "hat_carrier" (path "/{ROOT}" (reference "{ref}") (unit 1))))', "  )"]
        half = 3.81 if two else 1.27
        for i, net in enumerate(nets):
            right = two and i % 2
            row = i // 2 if two else i
            sign = 1 if right else -1
            px, py = sx + sign * (half + 3.81), round(sy - (top - row * 2.54), 2)
            if net is None:
                out.append(f'  (no_connect (at {px:.2f} {py:.2f}) (uuid "{uid(ref, i + 1, "nc")}"))')
                continue
            lx = px + sign * 7.62
            out.append(f'  (wire (pts (xy {px:.2f} {py:.2f}) (xy {lx:.2f} {py:.2f})) (stroke (width 0) (type default)) '
                       f'(uuid "{uid(ref, i + 1, "w")}"))')
            out.append(f'  (label "{net}" (at {lx:.2f} {py:.2f} 0) {FONT[:-1]} (justify {"left" if right else "right"} bottom)) '
                       f'(uuid "{uid(ref, i + 1, "l")}"))')
    out += ['  (sheet_instances (path "/" (page "1")))', ")"]
    return "\n".join(out) + "\n"


def library():
    return "\n".join(['(kicad_symbol_lib (version 20241209) (generator "hat_carrier_generate")',
                      *(symbol(n, d, f, names, two) for n, d, f, names, two, _ in SYMBOLS), ")"]) + "\n"


# Front-view carrier coordinates in mm (KiCad F side); B-side parts appear mirrored
BOARD = (86, 34)
HAT_XY, HAT_SIZE = (10.5, 0.5), (65, 30.2)
# Waveshare's drawing: holes 58 x 23.2 apart, 3.5 from the edges. The top right one sits over the camera socket
HAT_HOLES = [(3.5, 3.5), (3.5, 26.7), (61.5, 26.7)]
# With the stick on the left the socket runs along the bottom edge, pin 1 at the right end of the inner row
HAT_HEADER = (32.5, 26.7)
PICO_XY, CAMERA_XY = (0.75, 12.25), (54.75, 1.75)
# Pico holes from the datasheet; B0070 holes from its drawing, turned 180 degrees like the camera
PICO_HOLES = [(PICO_XY[0] + x, PICO_XY[1] + y) for x in (2, 49) for y in (4.8, 16.2)]
CAMERA_HOLES = [(CAMERA_XY[0] + x, CAMERA_XY[1] + 30.5 - y) for x in (3.745, 26.755) for y in (3.73, 21.23)]
# The case screws pass through the Pico and camera holes that lie outside the HAT
CASE_SCREWS = PICO_HOLES[:2] + CAMERA_HOLES[2:]
MECH = [
    ("HAT (FRONT, on J3 + M2.5x10 standoffs)", HAT_XY, HAT_SIZE),
    # Scaled from the drawing's render, so about 0.3 mm either way
    ("HAT LCD glass", (HAT_XY[0] + 17.7, HAT_XY[1] + 1.85), (29.5, 26.5)),
    ("HAT joystick", (HAT_XY[0] + 6.12 - 3.5, HAT_XY[1] + 15.18 - 3.5), (7, 7)),
    *((f"HAT KEY{i + 1}", (HAT_XY[0] + 57.1 - 3, HAT_XY[1] + y - 1.75), (6, 3.5)) for i, y in enumerate((9.23, 15.17, 21.11))),
    ("Pico 2 H (BACK, components to rear, USB left)", PICO_XY, (51, 21)),
    ("B0070 (BACK, lens to rear, header up)", CAMERA_XY, (30.5, 30.5)),
    ("J3 pin 1 upper right", (HAT_XY[0] + HAT_HEADER[0] - 9.5 * 2.54 - 1.27, HAT_XY[1] + HAT_HEADER[1] - 2.54), (50.8, 5.08)),
    ("J1 pin 1 left (USB end)", (PICO_XY[0] + 1.37 - 1.27, PICO_XY[1] + 1.61 - 1.27), (50.8, 2.54)),
    ("J2 pin 1 left (VBUS)", (PICO_XY[0] + 1.37 - 1.27, PICO_XY[1] + 19.39 - 1.27), (50.8, 2.54)),
    # Turned 180 degrees from Rev D so its socket clears J3; the OV7675's MVFP register turns the image back
    ("J4 pin 1 upper left", (CAMERA_XY[0] + 3.81 - 1.27, CAMERA_XY[1] + 1.27 - 1.27), (25.4, 5.08)),
]


def pcb():
    w, h = BOARD
    corners = [(1, 0), (w - 1, 0), (w, 1), (w, h - 1), (w - 1, h), (1, h), (0, h - 1), (0, 1)]
    out = ['(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")',
           "  (general (thickness 1.6))", '  (paper "A4")', "  (layers",
           *(f'    ({n} "{name}" {kind})' for n, name, kind in [
               (0, "F.Cu", "signal"), (31, "B.Cu", "signal"), (36, "B.SilkS", "user"), (37, "F.SilkS", "user"),
               (38, "B.Mask", "user"), (39, "F.Mask", "user"), (40, "Dwgs.User", "user"), (44, "Edge.Cuts", "user"),
               (46, "B.CrtYd", "user"), (47, "F.CrtYd", "user"), (48, "B.Fab", "user"), (49, "F.Fab", "user")]),
           "  )", "  (setup (pad_to_mask_clearance 0))", '  (net 0 "")']
    for i, (a, b) in enumerate(zip(corners, corners[1:] + corners[:1])):
        out.append(f'  (gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width 0.05) (type default)) '
                   f'(layer "Edge.Cuts") (uuid "{uid("edge", i)}"))')
    for i, (x, y) in enumerate(HAT_HOLES):
        x, y = round(HAT_XY[0] + x, 2), round(HAT_XY[1] + y, 2)
        out += [f'  (footprint "MountingHole:MountingHole_2.7mm_M2.5" (layer "F.Cu") (uuid "{uid("hole", i)}") (at {x} {y})',
                "    (attr board_only exclude_from_pos_files exclude_from_bom)",
                f'    (property "Reference" "H{i + 1}" (at 0 -2.8 0) (layer "F.SilkS") (hide yes) (uuid "{uid("hole-ref", i)}") (effects (font (size 1 1) (thickness 0.15))))',
                f'    (pad "" np_thru_hole circle (at 0 0) (size 2.7 2.7) (drill 2.7) (layers "*.Cu" "*.Mask")))']
    for i, (x, y) in enumerate(CASE_SCREWS):
        x, y = round(x, 3), round(y, 3)
        out += [f'  (footprint "MountingHole:MountingHole_2.2mm_M2" (layer "F.Cu") (uuid "{uid("screw", i)}") (at {x} {y})',
                "    (attr board_only exclude_from_pos_files exclude_from_bom)",
                f'    (property "Reference" "H{len(HAT_HOLES) + i + 1}" (at 0 -2.6 0) (layer "F.SilkS") (hide yes) (uuid "{uid("screw-ref", i)}") (effects (font (size 1 1) (thickness 0.15))))',
                f'    (pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers "*.Cu" "*.Mask")))']
    for i, (label, (x, y), (sw, sh)) in enumerate(MECH):
        out.append(f'  (gr_rect (start {x:.2f} {y:.2f}) (end {x + sw:.2f} {y + sh:.2f}) (stroke (width 0.12) (type default)) '
                   f'(fill none) (layer "Dwgs.User") (uuid "{uid("mech", i)}"))')
        out.append(f'  (gr_text "{label}" (at {x + sw / 2:.2f} {y - 0.6:.2f} 0) (layer "Dwgs.User") (uuid "{uid("mech-t", i)}") '
                   f'(effects (font (size 0.8 0.8) (thickness 0.12))))')
    out.append(f'  (gr_text "REV E DRAFT - FOOTPRINTS AND TRACKS COME FROM route.py" (at {w / 2} {h + 2.5} 0) '
               f'(layer "Dwgs.User") (uuid "{uid("draft")}") (effects (font (size 0.9 0.9) (thickness 0.12))))')
    out.append(")")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    (OUT / "HatCarrier.kicad_sym").write_text(library())
    (OUT / "hat_carrier.kicad_sch").write_text(schematic())
    (OUT / "hat_carrier.kicad_pcb").write_text(pcb())
    (OUT / "hat_carrier.kicad_pro").write_text("{}\n")
    (OUT / "sym-lib-table").write_text('(sym_lib_table (lib (name "HatCarrier") (type "KiCad") '
                                       '(uri "${KIPRJMOD}/HatCarrier.kicad_sym") (options "") (descr "HAT carrier symbols")))\n')

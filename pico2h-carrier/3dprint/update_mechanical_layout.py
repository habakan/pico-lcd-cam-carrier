import re
from uuid import NAMESPACE_URL, uuid5

from build_case_stl import BUTTONS, KEYS, OUT, OUTLINE, SCREWS, O, P


def uid(name):
    return str(uuid5(NAMESPACE_URL, f"pico-carrier-rev-d/{name}"))


def main():
    target = OUT.parent / "pico2h_carrier.kicad_pcb"
    original = target.read_text()
    if any(
        token in original for token in ("(segment ", "(via ", "(zone ")
    ) or re.search(r'\(pad\s+"[^"]*"\s+(thru_hole|smd|connect)\b', original):
        raise ValueError(
            "Electrical layout exists; update its mechanics manually in KiCad."
        )
    header = original[: original.index("  (gr_line")]
    elements = []
    for i, (a, b) in enumerate(zip(OUTLINE, OUTLINE[1:] + OUTLINE[:1])):
        elements.append(
            f'(gr_line (start {a[0] - O:g} {a[1] - O:g}) (end {b[0] - O:g} {b[1] - O:g}) (stroke (width 0.05) (type default)) (layer "Edge.Cuts") (uuid "{uid(f"edge-{i}")}"))'
        )
    for i, (x, y) in enumerate(SCREWS, 1):
        elements.append(f'''(footprint "MountingHole:MountingHole_2.2mm_M2" (layer "F.Cu") (uuid "{uid(f"hole-{i}")}") (at {x - O:g} {y - O:g})
          (attr board_only exclude_from_pos_files exclude_from_bom)
          (fp_text reference "H{i}" (at 0 -2.6) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
          (fp_text value "MountingHole_2.2mm_M2" (at 0 2.6) (layer "F.Fab") hide (effects (font (size 1 1) (thickness 0.15))))
          (pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers "*.Cu" "*.Mask")))''')
    lcd, cam, pico = P["lcd"], P["camera"], P["pico"]
    items = [
        ("LCD (FRONT, header soldered)", *lcd["xy"], *lcd["size"]),
        ("B0070 (BACK, lens to rear)", *cam["xy"], cam["size"], cam["size"]),
        ("Pico 2 H (BACK, USB down)", *pico["xy"], 21, 51),
    ]
    for i, (x, y) in enumerate(BUTTONS, 1):
        items.append((f"SW{i} (FRONT)", round(x - O - 3, 3), round(y - O - 3, 3), 6, 6))
    for name, x, y, width, height in items:
        elements.append(
            f'(gr_rect (start {x} {y}) (end {x + width:g} {y + height:g}) (stroke (width 0.12) (type default)) (fill (type none)) (layer "Dwgs.User") (uuid "{uid(name)}"))'
        )
        elements.append(
            f'(gr_text "{name}" (at {x + width / 2:g} {y - 1:g}) (layer "Dwgs.User") (uuid "{uid(name + "text")}") (effects (font (size 0.8 0.8) (thickness 0.12))))'
        )
    for category in ("case", "components"):
        elements.append(f'''(footprint "PicoCarrier:{category}_reference" (layer "F.Cu") (uuid "{uid(category)}") (at 0 0)
          (attr board_only exclude_from_pos_files exclude_from_bom)
          (fp_text reference "MECH_{category.upper()}" (at 0 -5) (layer "F.Fab") hide (effects (font (size 1 1) (thickness 0.15))))
          (model "${{KIPRJMOD}}/3dprint/{category}.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0))))''')
    elements.append(
        f'(gr_text "REV D MECHANICAL DRAFT - ELECTRICAL FOOTPRINTS / ROUTING PENDING" (at 38 56) (layer "Dwgs.User") (uuid "{uid("status")}") (effects (font (size 0.9 0.9) (thickness 0.12))))'
    )
    target.write_text(header + "\n".join("  " + e for e in elements) + "\n)\n")
    print(
        "Updated outline, four M2 case screw holes, placement envelopes and 3D references."
    )


if __name__ == "__main__":
    main()

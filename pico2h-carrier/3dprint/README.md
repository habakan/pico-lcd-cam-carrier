# Pico 2 H case Rev D

Outline **81.4 × 59.4 × 20.9 mm** (21.7 mm tall including the buttons). Landscape, with the D-pad on the left, the LCD in the center and the reject key on the right. Rev C (63.4 × 43.4 × 42.3 mm) stacked the camera, the Pico and the LCD front to back on sockets and harnesses, so it was thick, and it assumed a landscape LCD, so the window position did not match either. Rev D puts the camera behind the D-pad and the Pico behind the right end, and solders every part's header directly to remove the stacking. The LCD and camera dimensions come from the manufacturers' drawings.

## Preview

- [Assembled, internal layout](assembly_preview.png)
- [Exploded view](assembly_exploded.png)
- [Rotatable 3D view](assembly.html): open in a browser and switch between "Assembled", "Inside" and "Exploded".
- [Assembly GLB](assembly.glb): for viewing, includes the electronic parts. Use the 3MF/STL files below for printing.

## Stack-up (from the back)

| z (mm) | Part |
|---|---|
| 0–2.4 | Bottom of the back case. Camera window Ø12, BOOTSEL hole Ø3.2, counterbores for the screw heads |
| 3.0–6.5 | Camera module (3.5 mm tall, needs measuring) / the Pico's USB and SWD connectors |
| 6.5–8.1 | Camera board / 7.1–8.1 Pico board |
| 8.1–10.6 | Camera and Pico header plastic |
| 10.6–12.2 | Carrier board |
| 12.2–14.7 | LCD header plastic |
| 14.7–18.2 | LCD board and glass |
| 18.5–20.9 | Front cover |

## Files to print in Bambu Studio

| File | Contents | Print orientation |
|---|---|---|
| [bambu_plate_01_base.3mf](bambu_plate_01_base.3mf) | Back case | Outer bottom on the bed |
| [bambu_plate_02_front.3mf](bambu_plate_02_front.3mf) | Front cover | Screen side on the bed |
| [bambu_plate_03_small_parts.3mf](bambu_plate_03_small_parts.3mf) | Three camera spacers, six button caps | Caps head down on the bed |

The 3MFs contain only geometry. The defaults are PLA, a 0.4 mm nozzle, 0.20 mm layers, 4 walls and 20% infill. Slice and export a `.gcode.3mf` before printing. The top edges of the USB and SWD openings in the back case become bridges, so check them in the preview.

Individual STLs: [back case](pico2h_case_base.stl), [front cover](pico2h_case_front.stl), camera spacers ([for the screw](pico2h_case_camera_spacer.stl), [pinned 1](pico2h_case_camera_peg_1.stl), [pinned 2](pico2h_case_camera_peg_2.stl)), caps ([up](pico2h_case_button_1.stl), [down](pico2h_case_button_2.stl), [left](pico2h_case_button_3.stl), [right](pico2h_case_button_4.stl), [select](pico2h_case_button_5.stl), [reject](pico2h_case_button_6.stl))

## Assembly

Screws: **four M2 × 16 mm**. Insert them from the back and screw them into the front cover's posts (pilot holes Ø1.6).

1. Solder SW1–SW6 to the carrier's front, and the camera and the Pico 2 H to its back. Before fitting the camera, put the screw spacer (2.5 mm tall) at H1, and the pins of the pin spacers into the camera's two upper mounting holes.
2. Solder the LCD to the carrier's front.
3. Trim all leads to 1 mm or less. The switch leads come out right under the camera and the Pico, and the LCD, camera and Pico leads right under the LCD.
4. Turn the front cover over, put the six button caps into the holes (only the center select cap is a different color) and lay the assembled board on it. The front cover's pins go into the LCD's four holes.
5. Put on the back case and tighten the four screws. H1 passes through the camera board, and H3/H4 through the Pico's mounting holes. The back case's posts hold the pin spacers down together with the camera.
6. Check that USB plugs in, that an SWD cable (opening on the top edge) plugs in, and that the buttons spring back.

## To measure on the real parts

Fix [case_dimensions.json](case_dimensions.json) and regenerate. XY are carrier board (KiCad) coordinates; case coordinates add 2.7 mm to each.

| Parameter | Current value | Where to measure |
|---|---|---|
| `camera.lens_height` | 3.5 mm | From the lens side of the camera board to the tip of the module |
| `pico.bootsel` | [7.0, 11.7] | From the Pico's long edge on the pin 1 side and the USB end to the BOOTSEL center (converted from a photo) |
| `pico.usb_height` / `debug_height` | 2.9 / 2.9 mm | From the Pico's component side to the top of the connector |

## Regenerating

Run from the repository root in a Python 3.11 virtual environment.

```sh
uv venv -p 3.11 /tmp/pico-case-venv
VIRTUAL_ENV=/tmp/pico-case-venv uv pip install -r pico2h-carrier/3dprint/requirements.txt
/tmp/pico-case-venv/bin/python pico2h-carrier/3dprint/build_case_stl.py
```

It writes STL, 3MF, OpenSCAD, GLB, VRML for KiCad reference, images, HTML and a check report. STL, 3MF, OpenSCAD and GLB flip KiCad's y (downward) and are written right-handed, so the layout seen from the front matches the real thing (STLs up to 9bef5e1 were mirrored top to bottom). Images, HTML and VRML are drawn in KiCad's orientation as before. Run `update_mechanical_layout.py` as well only when updating the mechanical layout in KiCad. It refuses to overwrite a PCB that has electrical footprints or tracks.

## Check results

- All 33 parts are closed meshes, and each of the 11 printed parts is a single connected solid. Checked by reloading the STLs and 3MFs.
- Volume interference computed for 496 pairs at nominal dimensions: 0 overlaps (screw heads excluded). [fit_report.json](fit_report.json)
- The results of checking each part's dimensions against the manufacturers' drawings and datasheets are in `checks` in `case_dimensions.json` and in the 3D view. The LCD pin row, the switch shafts and the BOOTSEL position were fixed.
- Not yet sliced or printed; not yet loaded in KiCad or checked with ERC/DRC.

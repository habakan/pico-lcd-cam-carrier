# HAT carrier case (Rev E)

Outline **91.4 x 39.4 x 36.3 mm**. The key caps stand 3.8 mm and the stick cap 7.2 mm out of the front. The joystick is on the left, the LCD in the center and KEY1–3 on the right.

The HAT side of the front cover copies `OP_Upper.stl` from SeedSigner's [Orange Pill](https://github.com/SeedSigner/seedsigner/tree/dev/enclosures/orange_pill) (MIT), which uses the same HAT. The height above the HAT board, the window, the glass recess, the joystick and key holes, and the steps that hold the caps' flanges are all the same, so the Orange Pill caps fit as they are. The cover rests directly on the HAT board and is recessed only where there are parts. This is why the heights of the HAT's parts do not need to be measured.

- [Assembled](preview.png) / [With the front cover and back case removed](inside.png) / [Exploded view](exploded.png)

## What to print

In Bambu Studio, open the 3MF for each plate and slice it. The contents are the same as the STLs below, already oriented for printing.

| 3MF | Contents |
|---|---|
| [bambu_plate_01_back.3mf](bambu_plate_01_back.3mf) | Back case |
| [bambu_plate_02_front.3mf](bambu_plate_02_front.3mf) | Front cover |
| [bambu_plate_03_caps.3mf](bambu_plate_03_caps.3mf) | Three key caps, two stick caps (a spare in case the shaft hole is too tight). Layer height 0.08–0.12 mm |

The 3MFs contain only geometry, no print settings. To hand over on a microSD card, after slicing, export a `.gcode.3mf` with "Export plate sliced file".

| File | Qty | Orientation |
|---|---:|---|
| [hat_case_back.stl](hat_case_back.stl) | 1 | Back on the bed. The top edge of the USB opening in the left wall becomes a bridge |
| [hat_case_front.stl](hat_case_front.stl) | 1 | Screen side on the bed |
| [seedsigner/joystick.stl](seedsigner/joystick.stl) | 1 | From the Orange Pill. Suited to resin printing |
| [seedsigner/button.stl](seedsigner/button.stl) | 3 | From the Orange Pill. Suited to resin printing |

The two files in `seedsigner/` are copied as they are from `enclosures/orange_pill/print_files/` in SeedSigner (dev branch, ada81cde050e) and follow its [LICENSE.md](seedsigner/LICENSE.md). The shafts are 2 mm square, so community-made caps for the Orange Pill (2.05 mm square hole) can also be used instead.

As in Rev D, the defaults are PLA, a 0.4 mm nozzle, 0.20 mm layers, 4 walls and 20% infill.

## Screws and spacers

| Part | Qty | Use |
|---|---:|---|
| M2.5 x 10 mm female-female spacer | 3 | Between the carrier and the HAT (H1–H3) |
| M2.5 x 5 mm pan head machine screw | 6 | Top and bottom of the spacers |
| M2 x 25 mm pan head machine screw | 4 | From the back case into the front cover's posts (H4–H7) |

## Assembly

1. Fix the spacers to the carrier's H1–H3 with M2.5 x 5 screws from the back. The screw heads are later hidden under the Pico and the camera.
2. Plug the HAT into J3 and fix it to the spacers with M2.5 x 5 screws. The top-right hole takes no screw.
3. Plug the Pico 2 H and the camera into the back. Seen from the back, the Pico's USB is on the right and the camera's header is on the top edge.
4. Place the front cover screen side down and put the three key caps into their holes. Lay the assembled boards on it with the HAT facing the cover, passing the pin of the top-right post through the HAT's hole.
5. Push the stick cap through the front hole onto the joystick's shaft.
6. Put on the back case and tighten the four M2 x 25 screws. The screws pass through the mounting holes of the Pico and the camera, and the back case's posts press each board into its socket.
7. Check that USB plugs in, that BOOTSEL can be pressed through the hole in the back, and that the caps spring back. To use SWD, open the case and unplug the camera.

## Values copied from the Orange Pill

`opz()` and `opxy()` in `build_case.py` convert `OP_Upper.stl` coordinates to this case's coordinates.

| Item | Value (from the top of the HAT board) | Orange Pill shape |
|---|---|---|
| Front face | 4.0 mm | Front cover thickness |
| LCD top | 1.7 mm or less | Depth of the glass recess |
| Key top | About 3.0 mm | Underside of the button flange. If the keys are lower than this, the caps stop at a sunken position |
| Joystick center | (7.16, 15.45) within the HAT | Hole center. 1 mm off from (6.1, 15.2) in Waveshare's dimension drawing, but matched to the proven Orange Pill |

## To measure on the real parts

| Parameter (`build_case.py`) | Current value | Basis |
|---|---|---|
| HAT socket height | 7.5 mm | Worked back from the Orange Pill's 10 mm spacers |
| Camera lens height | 3.5 mm | Same provisional value as Rev D |

The joystick and key heights are estimates for checking interference on the drawings (`STICK_BODY`, `KNOB_TIP`, `KEY_TOP`) and are not used for the front cover's shape.

## Regenerating

Run from the repository root, with the same packages as Rev D.

```sh
uv run --no-project --with-requirements pico2h-carrier/3dprint/requirements.txt \
  python hat-carrier/3dprint/build_case.py
```

It takes the placement from the values in `../generate.py`, and imports the shape-building functions and the image rendering from Rev D's `build_case_stl.py` and `render_case.py`. The STLs flip KiCad's y (downward) and are written right-handed, so the layout seen from the front matches the real thing.

## Check results

- All 25 parts are closed meshes, and each of the two printed parts is a single solid. Checked by reloading the STLs, and by rereading the part count of the 3MFs. The caps are placed with the Orange Pill shapes at their nominal dimensions to check interference.
- Volume interference computed for 300 pairs at nominal dimensions: 0 overlaps. [fit_report.json](fit_report.json)
- Not yet sliced or printed.

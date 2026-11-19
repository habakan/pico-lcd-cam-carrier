# HAT carrier (KiCad draft, Rev E)

A draft carrier board for building a Waveshare 1.3inch LCD HAT, a Pico 2 H and an OV7675 (Arducam B0070) **by plugging them in, without soldering**. The board is ordered with its four connectors already fitted, so the builder only plugs in three boards and tightens the screws. It is a separate line from [Rev D](../pico2h-carrier/README.md), which is assembled by soldering.

The GPIO assignment matches `src/board_pins.h` in bitwasm-signer-pico (the table in the [README](../README.md)).

## Files

- `generate.py`: writes the four files below. To change the wiring or the placement, edit it and run `python3 generate.py`.
- `route.py`: run after `generate.py` with the Python bundled with KiCad. It places J1–J4, assigns the nets, autoroutes on two layers and pours GND on both sides.
  `~/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 route.py`
- `hat_carrier.kicad_sch`: schematic at the connector level.
- `HatCarrier.kicad_sym` / `sym-lib-table`: symbols for this design.
- `hat_carrier.kicad_pcb`: 86 x 34 mm outline with 1 mm chamfers at the corners, three M2.5 holes for the HAT and four M2 holes for the case, mechanical areas for the parts and pin rows (Dwgs.User), J1–J4 and the tracks. Do not edit it by hand; regenerate it from the two scripts.
- `3dprint/`: case generation script and print files. [3dprint/README.md](3dprint/README.md)

## Connectors

| Ref | For | Side | Footprint |
|---|---|---|---|
| J1 | Pico 2 H left row, physical pins 1–20 | B | 1x20 2.54 mm pin socket |
| J2 | Pico 2 H right row, physical pins 40–21 from the USB end | B | 1x20 2.54 mm pin socket |
| J3 | 1.3inch LCD HAT (Raspberry Pi 40-pin numbering) | F | 2x20 2.54 mm pin header (male) |
| J4 | OV7675 / Arducam B0070 | B | 2x10 2.54 mm pin socket (pad numbers use the pin header footprint) |

At J4's position, seen from the front, the pin numbers are mirrored left to right against how KiCad numbers its socket, so the numbering is matched by using the pin header footprint with the same pad layout. Checked with the real camera (2026-11-07). Seen from the pin side with the header at the top, pin 1 is the left end of the top row (the board-edge side).

The HAT-side connections were checked against Waveshare's schematic (`1.3inch-LCD-HAT-Schematic.pdf`).

| J3 pin | HAT signal | Net | Pico |
|---|---|---|---|
| 1, 17 | 3.3V | 3V3 | physical 36 |
| 13 | LCD RST | LCD_RES (the firmware resets it at boot, as in seedsigner-pico) | GP0 |
| 18 | LCD BL | 3V3 (also pulled up with 10k on the HAT) | - |
| 24 | LCD CS | GND (SPI mode 3) | - |
| 6, 9, 14, 20, 25, 30, 34, 39 | GND | GND | - |
| 23 / 19 / 22 | LCD CLK / DIN / DC | LCD_SCK / LCD_MOSI / LCD_DC | GP18 / GP19 / GP16 |
| 31 / 35 / 29 / 37 / 33 | up / down / left / right / press | BTN_UP / DOWN / LEFT / RIGHT / SELECT | GP13 / GP17 / GP20 / GP22 / GP26 |
| 40 / 38 / 36 | KEY1 / KEY2 / KEY3 | BTN_REJECT / BTN_B / BTN_C | GP27 / GP28 / GP1 |
| 2, 4 | 5V | **not connected** | - |

The camera is connected as in Rev D, with PEN tied to 3V3 and PDN tied to GND. Buttons pull to GND when pressed, and use the RP2350's internal pull-ups.

## Placement

PCB coordinates (KiCad coordinates seen from the front, mm). B-side parts are placed mirrored left to right as seen from the front.

| Part | Side | Position | Orientation |
|---|---|---|---|
| HAT | F | (10.5, 0.5)–(75.5, 30.7) | Joystick on the left, LCD in the center, KEY1–3 on the right. Socket on the bottom edge |
| J3 | F | center (43, 27.2) | Pin 1 is at the right end of the top (inner) row (67.13, 25.93) |
| Pico 2 H | B | (0.75, 12.25)–(51.75, 33.25) | Component side faces the back, USB on the left edge |
| J1 / J2 | B | rows y = 13.86 / 31.64, x = 2.12–50.38 | Both have pin 1 at the USB end (left) |
| B0070 | B | (54.75, 1.75)–(85.25, 32.25) | Lens faces the back, center (69.99, 19.60). Header on the top edge (upside down from Rev D) |
| J4 | B | rows y = 3.02 (odd) / 5.56 (even), x = 58.56–81.42 | Pin 1 at the left end |
| H1–H3 | - | (14, 4.0), (14, 27.2), (72, 27.2) | Coaxial with the HAT's mounting holes. M2.5 x 10 mm female-female spacers support the HAT (as in SeedSigner's Orange Pill) |
| H4–H7 | - | (2.75, 17.05), (2.75, 28.45), (81.505, 28.52), (81.505, 11.02) | Coaxial with the mounting holes of the Pico and the camera. The case's M2 screws pass through them |

- The HAT's top-right mounting hole (72, 4.0) has no hole in the carrier, because a screw head there would overlap the camera socket on the back. The front cover's post holds that corner.
- The camera is upside down from Rev D because with the header on the bottom edge, J4 would overlap J3. The image can be rotated 180° with the OV7675's MVFP register (0x1E). The current firmware does not set this register, so decide after assembly by checking the preview orientation.
- The screw heads of H1–H3 (Ø4.5) sit under the Pico and the camera. Both are raised by the socket and header plastic (11 mm), so they do not touch, but tighten the screws before plugging in the Pico and the camera. The gap between H2's screw head and J2's socket is 0.9 mm, and the spacing between the pins of J3 and J2 is 3.3 mm.
- The Pico's SWD connector at the right end is only 3 mm from the camera. To use SWD, open the case and unplug the camera.

## Stack-up (from the back, estimated)

| z (mm) | Part |
|---|---|
| 0–2.4 | Back case |
| 3.0–6.5 | Camera lens (the Pico's USB and SWD are 2.9 mm, lower than this) |
| 6.5–8.1 | Camera board |
| 8.1–19.1 | Camera header plastic 2.5 + socket 8.5 |
| 19.1–20.7 | Carrier board |
| 20.7–30.7 | J3 plastic 2.5 + HAT socket 7.5 |
| 30.7–32.3 | HAT board |
| 32.3–34.0 | LCD module (1.7 mm or less) |
| 32.3–36.3 | Front cover (rests directly on the HAT board, recessed only at the parts) |

The case is expected to be about **91.4 x 39.4 x 36.3 mm**. With low-profile sockets of about 5 mm for J1, J2 and J4, it gets down to about 32.8 mm. Most of the thickness is the two levels of sockets, and the 10 mm on the HAT side is set by the HAT's socket, so it cannot be reduced.

## Source of the HAT dimensions

No 3D CAD data is published. The values below come from the [dimension drawing](https://www.waveshare.com/img/devkit/LCD/1.3inch-LCD-HAT/1.3inch-LCD-HAT-size.jpg) and product photos on Waveshare's product page, and from the STLs of SeedSigner's [Orange Pill case](https://github.com/SeedSigner/seedsigner/tree/dev/enclosures/orange_pill) (MIT), which uses the same HAT. Coordinates within the HAT have their origin at the top left, seen from the LCD side with the joystick on the left.

| Item | Value | Basis |
|---|---|---|
| Outline | 65 x 30.2, corner R1.5 | Dimension drawing |
| Mounting holes | (3.5, 3.5), (61.5, 3.5), (3.5, 26.7), (61.5, 26.7), M2.5 | Spacing 58 x 23.2 in the dimension drawing |
| Socket | Bottom edge, center (32.5, 26.7), pin 1 at the inner side of the right end | Photos (underside, mounted on a Pi Zero and a Pi 3) and the Pi HAT spec |
| LCD glass | (17.7, 1.85)–(47.2, 28.35) | Measured to scale from the dimension drawing image, ±0.3 mm |
| Joystick center | (7.16, 15.45) | Center of the Orange Pill hole. The dimension drawing reads (6.1, 15.2), but the hole was matched because the Orange Pill caps are used |
| KEY1 / KEY2 / KEY3 centers | (57.1, 9.2) / (57.1, 15.2) / (57.1, 21.1) | Same as above. Also matches the Orange Pill key holes (57.0, spacing 5.9) |
| LCD active area center | (31.25, 15.35) | Center of the Orange Pill window (24 x 24.5). About 1 mm toward the joystick from the glass center |
| LCD height | 1.7 mm or less | Depth of the Orange Pill's recess for the glass |
| Joystick and key height | Not measured | The front cover has the same shape as the Orange Pill and uses its caps ([3dprint/README.md](3dprint/README.md)) |
| Socket height | About 7.5 mm | The Orange Pill fixes the Pi Zero and the HAT with 10 mm spacers. This is that minus the 2.5 mm header plastic on the Pi side |

## To measure on the real parts

| Item | Current assumption | Used for |
|---|---|---|
| Socket height, HAT board thickness | 7.5 / 1.6 mm | Thickness. Checking the estimate above |
| Height of parts on the HAT's underside | Unknown | Interference around J3 |

## Routing

Maze routing on `route.py`'s grid (0.1 mm). Track width 0.25 mm, clearance 0.15 mm and vias 0.6/0.3 mm, which fit JLCPCB's standard process. One track passes between pads at 2.54 mm pitch.

- No copper within a 3.0 mm radius of the HAT's M2.5 holes (spacers and screw heads), within a 2.3 mm radius of the case's M2 holes, or within 0.5 mm of the board edge.
- Signals are routed shortest first, and 3V3 and GND last. GND is also connected through the pours on both sides.
- The current result is 28 nets, 7 vias, 0 unrouted.

## Next steps

1. Measure the items in "To measure on the real parts", fix the constants in `generate.py` and rerun the two scripts.
2. Test-print the case (`3dprint/`) and check that the Orange Pill caps move.
3. Get a quote for ordering the board with the connectors fitted. Also check here whether low-profile sockets can be chosen.

## Checks

Checked with `kicad-cli` from KiCad 10.0.7.

- Schematic ERC has 0 errors. The only warnings are 4 saying the footprint library is not registered in the CLI environment.
- In the exported netlist, the pins of each net match the table above and `board_pins.h`. 3V3 has 6 pins, GND has 18 pins, and every signal, including LCD_RES, has 2 pins.
- PCB DRC has 0 violations and 0 unconnected items. The remaining findings are warnings that the mounting hole library is not registered (one per hole) and too few thermal relief spokes on two GND pads (both are connected to GND by tracks).

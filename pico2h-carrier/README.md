# Pico 2 H carrier (KiCad draft, Rev D)

A KiCad draft for moving bitwasm-signer-pico's breadboard wiring (`docs/hardware.md`, `src/board_pins.h`) onto a carrier board with the Pico 2 H, the LCD and the OV7675 soldered on directly.

## Files

- `pico2h_carrier.kicad_sch`: schematic at the connector level. Net labels match the actual wiring and `board_pins.h`.
- `pico2h_carrier.kicad_pcb`: 76 x 54 mm outline with 1 mm chamfers at the corners, four M2 mounting holes, and mechanical areas for the parts. Electrical footprints are not placed yet.
- `PicoCarrier.kicad_sym`: connector symbols for this design.
- `sym-lib-table`: project registration of the symbol library above.
- `3dprint/`: case generation script and print files. [3dprint/README.md](3dprint/README.md)

## Connectors

| Ref | For | Side | Footprint |
|---|---|---|---|
| J1 | Pico 2 H left row, physical pins 1–20 | B | 1x20 2.54 mm through-hole (Pico header soldered directly) |
| J2 | Pico 2 H right row, physical pins 40–21 from the USB end | B | 1x20 2.54 mm through-hole |
| J3 | M154-240240-RGB | F | 1x8 2.54 mm through-hole (LCD header soldered directly) |
| J4 | OV7675 / Arducam B0070 | B | 2x10 2.54 mm through-hole (camera header soldered directly) |
| SW1–SW5 | D-pad: up (GP13), down (GP17), left (GP20), right (GP22), select (GP26) | F | 6 mm THT tactile switch |
| SW6 | reject (GP27) | F | 6 mm THT tactile switch |

The LCD's RES (J3 pin 5) goes to GP0, and the firmware resets it at boot (as in seedsigner-pico; logs go over RTT through SWD). The LCD's J3 pin 1 is GND, and on the camera's J4 the odd pins are the bottom row seen from the lens side. The Pico right row's J2 pin 1 is the VBUS position at the USB end.

## Placement

PCB coordinates (KiCad coordinates seen from the front, mm). B-side parts are placed mirrored left to right as seen from the front.

| Part | Side | Position | Orientation |
|---|---|---|---|
| SW1–SW5 | F | center (14, 25.3), pitch 8.5 | Cross layout left of the LCD, SW5 in the center |
| LCD | F | (27.5, 5)–(59.5, 48.72) | Portrait, header on the top edge |
| SW6 | F | (66.2, 25.3) | Right of the LCD |
| B0070 | B | (1.5, 22)–(32, 52.5) | Behind the D-pad, lens faces the back, header on the bottom edge |
| Pico 2 H | B | (53.5, 1.7)–(74.5, 52.7) | Right end, vertical, USB on the bottom edge, component side faces the back |
| Mounting holes H1–H4 | - | (5.245, 43.23), (4, 4), (69.7, 3.7), (69.7, 50.7) | H1 coaxial with the camera's mounting hole, H3/H4 with the Pico's |

Everything is soldered directly with the header plastic (2.5 mm) in between, so each board sits 2.5 mm off the carrier. The Pico's left row is 2.72 mm from the LCD's pin row, and the camera header is moved down, below the D-pad, out of the way. The switch leads come out under the camera and the Pico, and the LCD, camera and Pico leads come out under the LCD, so trim them to 1 mm or less after soldering.

Dimensions are based on Akizuki Denshi's [LCD drawing](https://akizukidenshi.com/goodsaffix/M154-240240-RGB-8_20261020.pdf), [B0070 drawing](https://akizukidenshi.com/goodsaffix/b0070_dim.pdf) and [switch drawing](https://akizukidenshi.com/goodsaffix/TVDP01-G73BB.pdf), and the [Pico 2 datasheet](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf).

## Next steps

1. Measure the camera lens height, the header orientation (whether the plastic is on the lens side or the back side) and the LCD pin row position on the real parts, and fix `3dprint/case_dimensions.json`.
2. Test-print the case, and line up the part positions with a 1:1 paper print of the board outline.
3. In KiCad, place the footprints on the mechanical areas, sync the nets and route. J1/J2/J4 are on the B side, so their pin order is mirrored.
4. Check ERC/DRC and the case dimensions before exporting manufacturing data.

## Checks

KiCad is not available in this work environment, so loading in KiCad, ERC, DRC and Gerber export have not been done.

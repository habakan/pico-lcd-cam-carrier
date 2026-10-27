# Pico 2 H carrier (KiCad draft, Rev D)

ブレッドボードの配線（`docs/hardware.md`、`src/board_pins.h`）を、Pico 2 H・LCD・OV7675 を直接はんだ付けするキャリア基板へ移すための KiCad 下書きです。

## ファイル

- `pico2h_carrier.kicad_sch`: コネクタ単位の回路図。ネットラベルは実配線と `board_pins.h` に合わせています。
- `pico2h_carrier.kicad_pcb`: 56 x 54 mm・四隅1 mm面取りの外形、M2固定穴4つ、部品の機械領域。電気フットプリントは未配置です。
- `PicoCarrier.kicad_sym`: この設計用のコネクタシンボル。
- `sym-lib-table`: 上記シンボルライブラリのプロジェクト登録。
- `3dprint/`: ケースの生成スクリプトと印刷データ。[3dprint/README.md](3dprint/README.md)

## コネクタ

| Ref | 対象 | 面 | フットプリント |
|---|---|---|---|
| J1 | Pico 2 H 左列、物理ピン1–20 | B | 1x20 2.54 mm スルーホール（Pico のヘッダを直付け） |
| J2 | Pico 2 H 右列、USB側から物理ピン40–21 | B | 1x20 2.54 mm スルーホール |
| J3 | M154-240240-RGB | F | 1x8 2.54 mm スルーホール（LCD のヘッダを直付け） |
| J4 | OV7675 / Arducam B0070 | B | 2x10 2.54 mm スルーホール（カメラのヘッダを直付け） |
| SW1, SW2, SW3 | 次へ (GP17)、承認 (GP26)、拒否 (GP27) | F | 6 mm THT タクトスイッチ |
| J5 | Debug Probe UART RX/GND | F | 1x2 2.54 mm パッド。部品は載せない |

LCDのJ3 pin 1はGND、カメラJ4は奇数ピンがレンズ面から見て下列です。Pico右列J2 pin 1はUSB側のVBUS位置です。

## 配置

PCB座標（前面から見た KiCad 座標、mm）。B面部品は前面から見て左右反転して置きます。

| 部品 | 面 | 位置 | 向き |
|---|---|---|---|
| LCD | F | (8, 1.5)–(40, 45.22) | 縦長、ヘッダが上辺 |
| SW1–SW3 | F | x = 44、y = 14 / 27 / 40 | LCD の右に縦一列 |
| B0070 | B | (1.5, 1.5)–(32, 32) | レンズは背面へ、ヘッダが下辺 |
| Pico 2 H | B | (33.5, 1.7)–(54.5, 52.7) | 縦置き、USB が下辺、部品面は背面へ |
| 固定穴 H1–H4 | - | (5.245, 5.23)、(4, 48.5)、(49.7, 3.7)、(49.7, 50.7) | H1 はカメラ、H3/H4 は Pico の取付穴と同軸 |

すべてヘッダの樹脂（2.5 mm）を挟んで直付けするため、各基板はキャリアから2.5 mm浮きます。LCD・カメラ・Pico・スイッチのリードは隣の基板の真下に出るので、はんだ付け後に1 mm以下へ切りそろえます。

寸法の根拠は秋月電子の [LCD図面](https://akizukidenshi.com/goodsaffix/M154-240240-RGB-8_20261020.pdf)、[B0070図面](https://akizukidenshi.com/goodsaffix/b0070_dim.pdf)、[スイッチ図面](https://akizukidenshi.com/goodsaffix/TVDP01-G73BB.pdf)、[Pico 2 データシート](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf) です。

## 次の作業

1. カメラのレンズ高さ、ヘッダの向き（樹脂がレンズ側か裏側か）、LCD のピン列位置を実物で測り、`3dprint/case_dimensions.json` を直す。
2. ケースを試し刷りし、基板外形を1:1印刷した紙で部品の位置を合わせる。
3. KiCadでフットプリントを機械領域に合わせて配置し、ネットを同期して配線する。J1/J2/J4はB面配置でピン配列が反転する。
4. ERC/DRCとケース寸法を確認してから製造データを出力する。

## 確認

この作業環境には KiCad がないため、KiCad上での読込確認、ERC、DRC、Gerber出力は未実施です。

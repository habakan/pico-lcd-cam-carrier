# Pico 2 H ケース Rev D

外形 **61.4 × 59.4 × 20.9 mm**（ボタンを含む高さ21.7 mm）。Rev C（63.4 × 43.4 × 42.3 mm）は、カメラ・Pico・LCD をソケットやハーネスで前後に積んでいたため厚くなり、LCD を横長と仮定していたため窓の位置も合いませんでした。Rev D では Pico とカメラをキャリア裏に並べ、全部品のヘッダを直接はんだ付けして積み重ねをなくしています。LCD・カメラの寸法はメーカー図面から取っています。

## 完成イメージ

- [完成・内部配置](assembly_preview.png)
- [分解図](assembly_exploded.png)
- [回して確認する3Dビュー](assembly.html)：ブラウザーで開き、「完成」「内部」「分解」を切り替えます。
- [組立GLB](assembly.glb)：電子部品を含む閲覧用。印刷には下記の3MF/STLを使います。

## 積み重ね（背面から）

| z (mm) | 部品 |
|---|---|
| 0–2.4 | 背面ケースの底。カメラ窓 Ø12、BOOTSEL穴 Ø3.2、ねじ頭の座ぐり |
| 3.0–6.5 | カメラモジュール（高さ3.5 mm、要実測）/ Pico の USB・SWD コネクタ |
| 6.5–8.1 | カメラ基板 / 7.1–8.1 Pico 基板 |
| 8.1–10.6 | カメラ・Pico のヘッダ樹脂 |
| 10.6–12.2 | キャリア基板 |
| 12.2–14.7 | LCD のヘッダ樹脂 |
| 14.7–18.2 | LCD 基板とガラス |
| 18.5–20.9 | 前カバー |

## Bambu Studioで印刷するファイル

| ファイル | 内容 | 印刷方向 |
|---|---|---|
| [bambu_plate_01_base.3mf](bambu_plate_01_base.3mf) | 背面ケース | 外側底面がベッド |
| [bambu_plate_02_front.3mf](bambu_plate_02_front.3mf) | 前カバー | 画面側がベッド |
| [bambu_plate_03_small_parts.3mf](bambu_plate_03_small_parts.3mf) | カメラ用スペーサー1個、ボタンキャップ3個 | キャップは頭がベッド |

3MFは形状のみを含みます。PLA・0.4 mmノズル・積層0.20 mm・壁4周・インフィル20%を初期値とし、スライスして`.gcode.3mf`を書き出してから印刷します。背面ケースの USB 開口と SWD 開口の上辺はブリッジになるので、プレビューで確認します。

個別STL：[背面ケース](pico2h_case_base.stl)、[前カバー](pico2h_case_front.stl)、[カメラ用スペーサー](pico2h_case_camera_spacer.stl)、[次へ](pico2h_case_button_1.stl)・[承認](pico2h_case_button_2.stl)・[拒否](pico2h_case_button_3.stl)のキャップ

## 組立

ねじは **M2 × 16 mm を4本**。背面から差し、前カバーの柱（下穴 Ø1.6）へねじ込みます。

1. キャリア表面に SW1–SW3 を、裏面にカメラと Pico 2 H をはんだ付けする。カメラの左上の取付穴とキャリアの H1 の間に、印刷したスペーサー（高さ2.5 mm）を挟んでから付ける。
2. キャリア表面に LCD をはんだ付けする。
3. すべてのリードを1 mm以下に切りそろえる。LCD とカメラのリードは互いの基板の真下に、スイッチのリードは Pico の真下に出る。
4. 前カバーを裏返し、ボタンキャップ3個を穴へ入れ、組んだ基板を載せる。LCD の4つの穴に前カバーのピンが入る。
5. 背面ケースをかぶせ、4本のねじで締める。H1 はカメラ基板、H3/H4 は Pico の取付穴を通る。
6. USB が挿せること、SWD ケーブル（上辺の開口）が挿せること、ボタンが戻ることを確認する。

## 実物で測る項目

[case_dimensions.json](case_dimensions.json) を直して再生成します。XY はキャリア基板（KiCad）の座標、ケース座標は各2.7 mm足した値です。

| パラメータ | 現在値 | 測る箇所 |
|---|---|---|
| `camera.lens_height` | 3.5 mm | カメラ基板のレンズ面からモジュール先端まで |
| `camera.standoff` | 2.5 mm | カメラのヘッダ樹脂の厚さ。樹脂がレンズ側にある場合は、裏面部品の高さに置き換える |
| `lcd.pins.first` | [7.11, 2.5] | LCD 左端・上端から1番ピン中心 |
| `pico.bootsel` | [10.5, 10.5] | Pico の長辺・USB端から BOOTSEL 中心 |
| `pico.usb_height` / `debug_height` | 2.9 / 2.9 mm | Pico 部品面からコネクタ上端 |
| `buttons.body_height` | 3.5 mm | スイッチ本体の高さ（ステム除く） |

## 再生成

Python 3.11の仮想環境で、リポジトリ直下から実行します。

```sh
uv venv -p 3.11 /tmp/pico-case-venv
VIRTUAL_ENV=/tmp/pico-case-venv uv pip install -r hardware/kicad/pico2h-carrier/3dprint/requirements.txt
/tmp/pico-case-venv/bin/python hardware/kicad/pico2h-carrier/3dprint/build_case_stl.py
```

STL、3MF、OpenSCAD、GLB、KiCad参照用VRML、画像、HTML、検査レポートを出力します。KiCadの機械配置を更新するときだけ `update_mechanical_layout.py` も実行します。電気フットプリントや配線があるPCBへの上書きは拒否します。

## 確認結果

- 全25パーツが閉じたメッシュで、印刷する6パーツは各1つの連結した立体。STLと3MFを再読込して確認。
- 公称寸法で276組の体積干渉を計算し、重なり0件（ねじ頭は対象外）。[fit_report.json](fit_report.json)
- スライス・実機印刷、KiCadでの読込・ERC/DRCは未実施。

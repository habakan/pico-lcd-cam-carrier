# HAT キャリアのケース（Rev E）

外形 **91.4 x 39.4 x 36.3 mm**。キーのキャップは前面から 3.8 mm、スティックのキャップは 7.2 mm 出ます。左にジョイスティック、中央に LCD、右に KEY1–3 が来ます。

前カバーの HAT 側は、同じ HAT を使う SeedSigner の [Orange Pill](https://github.com/SeedSigner/seedsigner/tree/dev/enclosures/orange_pill)（MIT）の `OP_Upper.stl` を写しています。HAT の基板面からの高さ、窓、ガラスの凹み、ジョイスティックとキーの穴、キャップのつばを受ける段がすべて同じなので、Orange Pill のキャップがそのまま使えます。カバーは HAT の基板に直接当たり、部品のある所だけ凹ませています。HAT の部品の高さを測らずに済むのはこのためです。

- [完成](preview.png) / [前カバーと背面ケースを外した状態](inside.png) / [分解図](exploded.png)

## 印刷するもの

Bambu Studio では、プレートごとにまとめた 3MF を開いてスライスします。中身は下の STL と同じで、向きも印刷用に揃えてあります。

| 3MF | 中身 |
|---|---|
| [bambu_plate_01_back.3mf](bambu_plate_01_back.3mf) | 背面ケース |
| [bambu_plate_02_front.3mf](bambu_plate_02_front.3mf) | 前カバー |
| [bambu_plate_03_caps.3mf](bambu_plate_03_caps.3mf) | キーのキャップ3個、スティックのキャップ2個（軸の穴がきつかったときの予備）。積層 0.08〜0.12 mm |

3MF は形状だけで、印刷設定は含みません。microSD で渡すときは、スライスしたあと「プレートのスライスファイルをエクスポート」で `.gcode.3mf` を書き出します。

| ファイル | 数 | 向き |
|---|---:|---|
| [hat_case_back.stl](hat_case_back.stl) | 1 | 背面がベッド。左の壁の USB 開口の上辺はブリッジになる |
| [hat_case_front.stl](hat_case_front.stl) | 1 | 画面側がベッド |
| [seedsigner/joystick.stl](seedsigner/joystick.stl) | 1 | Orange Pill のもの。光造形が向く |
| [seedsigner/button.stl](seedsigner/button.stl) | 3 | Orange Pill のもの。光造形が向く |

`seedsigner/` の2つは SeedSigner（dev ブランチ、ada81cde050e）の `enclosures/orange_pill/print_files/` からそのまま持ってきたもので、[LICENSE.md](seedsigner/LICENSE.md) に従います。軸が 2 mm 角なので、Open Pill 向けにコミュニティが作ったキャップ（穴 2.05 mm 角）も差し替えて使えます。

Rev D と同じく PLA・0.4 mm ノズル・積層 0.20 mm・壁4周・インフィル 20% を初期値にします。

## ねじとスペーサー

| 部品 | 数 | 用途 |
|---|---:|---|
| M2.5 x 10 mm メス-メス スペーサー | 3 | キャリアと HAT の間（H1–H3） |
| M2.5 x 5 mm なべ小ねじ | 6 | スペーサーの上下 |
| M2 x 25 mm なべ小ねじ | 4 | 背面ケースから前カバーの柱へ（H4–H7） |

## 組立

1. キャリアの H1–H3 に、背面から M2.5 x 5 でスペーサーを留める。ねじ頭はあとで Pico とカメラの下に隠れる。
2. HAT を J3 に差し、M2.5 x 5 でスペーサーに留める。右上の穴はねじを使わない。
3. 背面に Pico 2 H とカメラを差す。背面から見ると、Pico の USB は右、カメラのヘッダは上辺に来る。
4. 前カバーを画面側を下にして置き、キーのキャップ3個を穴に入れる。組んだ基板を HAT 側から載せ、右上の柱のピンを HAT の穴に通す。
5. スティックのキャップを、前面の穴からジョイスティックの軸に押し込む。
6. 背面ケースをかぶせ、M2 x 25 を4本締める。ねじは Pico とカメラの取付穴を通り、背面ケースの柱がそれぞれの基板をソケットへ押さえる。
7. USB が挿せること、BOOTSEL を背面の穴から押せること、キャップが戻ることを確かめる。SWD を使うときはケースを開けてカメラを抜く。

## Orange Pill から写した値

`build_case.py` の `opz()` と `opxy()` が、`OP_Upper.stl` の座標をこのケースの座標に直します。

| 項目 | 値（HAT 基板の上面から） | Orange Pill の形 |
|---|---|---|
| 前面 | 4.0 mm | 前カバーの厚さ |
| LCD の上面 | 1.7 mm 以下 | ガラスの凹みの深さ |
| キーの上面 | 約 3.0 mm | ボタンのつばの下面。キーがこれより低ければ、キャップが沈んだ位置で止まる |
| ジョイスティックの中心 | HAT 内の (7.16, 15.45) | 穴の中心。Waveshare の寸法図の (6.1, 15.2) とは 1 mm ずれるが、実績のある Orange Pill に合わせた |

## 実物で測る項目

| パラメータ（`build_case.py`） | 今の値 | 根拠 |
|---|---|---|
| HAT のソケットの高さ | 7.5 mm | Orange Pill の 10 mm スペーサーから逆算 |
| カメラのレンズの高さ | 3.5 mm | Rev D と同じ仮の値 |

ジョイスティックとキーの高さは、図の上で干渉を確かめるための推定値（`STICK_BODY`、`KNOB_TIP`、`KEY_TOP`）で、前カバーの形には使っていません。

## 再生成

リポジトリ直下から、Rev D と同じパッケージで実行します。

```sh
uv run --no-project --with-requirements hardware/kicad/pico2h-carrier/3dprint/requirements.txt \
  python hardware/kicad/hat-carrier/3dprint/build_case.py
```

配置は `../generate.py` の値を、形状を作る関数と画像の描画は Rev D の `build_case_stl.py` と `render_case.py` を読み込んで使います。STL は KiCad の y（下向き）を反転して右手系で出力するので、前から見た配置が実物と一致します。

## 確認結果

- 全25部品が閉じたメッシュで、印刷する2部品はそれぞれ1つの立体。STL を読み込み直し、3MF は部品の数を読み直して確認。キャップは Orange Pill の形を寸法どおりに置いて干渉を見ている。
- 公称寸法で300組の体積干渉を計算し、重なりは0件。[fit_report.json](fit_report.json)
- スライス・実機印刷は未実施。

# HAT キャリアのケース（Rev E）

外形 **91.4 x 39.4 x 37.0 mm**（キャップを含む高さ 39.0 mm）。左にジョイスティック、中央に LCD、右に KEY1–3 が来ます。前面の作り（窓、キャップを抜けなくするつば、キー穴の間隔）は、同じ HAT を使う SeedSigner の [Orange Pill](https://github.com/SeedSigner/seedsigner/tree/dev/enclosures/orange_pill)（MIT）を参考にしています。

- [完成](preview.png) / [前カバーと背面ケースを外した状態](inside.png) / [分解図](exploded.png)

## 印刷するもの

| ファイル | 数 | 向き |
|---|---:|---|
| [hat_case_back.stl](hat_case_back.stl) | 1 | 背面がベッド。左の壁の USB 開口の上辺はブリッジになる |
| [hat_case_front.stl](hat_case_front.stl) | 1 | 画面側がベッド |
| [hat_case_stick.stl](hat_case_stick.stl) | 1 | つばがベッド |
| [hat_case_key.stl](hat_case_key.stl) | 3 | つばがベッド |

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
4. 前カバーを画面側を下にして置き、キャップ4個を穴に入れる。組んだ基板を HAT 側から載せ、右上の柱のピンを HAT の穴に通す。
5. 背面ケースをかぶせ、M2 x 25 を4本締める。ねじは Pico とカメラの取付穴を通り、背面ケースの柱がそれぞれの基板をソケットへ押さえる。
6. USB が挿せること、BOOTSEL を背面の穴から押せること、キャップが戻ることを確かめる。SWD を使うときはケースを開けてカメラを抜く。

## 実物で測る項目

| パラメータ（`build_case.py`） | 今の値 | 根拠 |
|---|---|---|
| ジョイスティックの高さ `STICK_BODY` / `KNOB_TIP` | HAT 基板から 1.2 / 3.0 mm | 仮の値。キャップの凹みの位置が決まる |
| キーの高さ `KEY_TOP` | HAT 基板から 1.5 mm | Orange Pill のキャップから逆算 |
| HAT のソケット、LCD の高さ | 7.5 / 2.0 mm | Orange Pill から逆算 |
| カメラのレンズの高さ | 3.5 mm | Rev D と同じ仮の値 |

## 再生成

リポジトリ直下から、Rev D と同じパッケージで実行します。

```sh
uv run --no-project --with-requirements hardware/kicad/pico2h-carrier/3dprint/requirements.txt \
  python hardware/kicad/hat-carrier/3dprint/build_case.py
```

配置は `../generate.py` の値を、形状を作る関数と画像の描画は Rev D の `build_case_stl.py` と `render_case.py` を読み込んで使います。STL は KiCad の y（下向き）を反転して右手系で出力するので、前から見た配置が実物と一致します。

## 確認結果

- 全25部品が閉じたメッシュで、印刷する4部品はそれぞれ1つの立体。STL を読み込み直して確認。
- 公称寸法で300組の体積干渉を計算し、重なりは0件。[fit_report.json](fit_report.json)
- スライス・実機印刷は未実施。

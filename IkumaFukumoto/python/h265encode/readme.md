# encode_h265.py コマンドオプション解説

このスクリプトは、FFmpeg を Python から呼び出して H.265/HEVC にエンコードするためのツールです。  
単体ファイル・ディレクトリ一括処理、CPU(libx265)・GPU(NVENC/VideoToolbox/QSV) に対応します。
FFmpegがインストールされているかわからない場合は[注意事項](#注意事項)に進んでください。

## 目次

- [基本構文](#基本構文)
- [主なオプション一覧](#主なオプション一覧)
- [使用例](#使用例)
- [推奨設定の目安](#推奨設定の目安)
- [注意事項](#注意事項)
- [FFmpegのインストール](#ffmpegのインストール)

---

## 基本構文

プロジェクトディレクトリに移動し、以下のコマンドを実行してください。

```bash
python encode_h265.py INPUT [オプション]
```

- `INPUT` : 入力ファイルまたはディレクトリ

---

## 主なオプション一覧

### 出力関連

- `-o, --out-dir <DIR>`  
  出力先ディレクトリ（デフォルト: `./out_h265`）

- `--ext <mp4|mkv>`  
  出力ファイル形式（デフォルト: `mp4`）

- `--overwrite`  
  出力ファイルが既に存在する場合に上書きする（デフォルトはスキップ）

---

### エンコーダ関連

- `-e, --encoder <libx265|hevc_nvenc|hevc_videotoolbox|hevc_qsv>`  
  使用する映像エンコーダ（デフォルト: `libx265`）

- `--quality <int>`  
  画質指標（libx265 用: CRF, NVENC/QSV/VTB 用: CQ）。
  - libx265 の場合: 18〜28が目安、低いほど高画質・大容量（デフォルト: 18）。
  - NVENC/QSV/VideoToolbox の場合: 18〜28が目安、低いほど高画質・大容量（デフォルト: 18）。

- `--preset <string>`  
  エンコード速度と圧縮効率のバランス指定。  
  - libx265: `ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo`  
  - hevc_nvenc: `p1〜p7`  
  - hevc_qsv / hevc_videotoolbox: 各種 ffmpeg ドキュメント参照  
  デフォルトは `ultrafast`。

- `--x265-params <string>`  
  x265 の追加パラメータ（例: `"no-sao=1:ref=4"` のようにコロン区切りで指定）。

---

### 並列処理関連

- `--threads <int>`  
  ディレクトリ指定時に複数ファイルを並列処理する数（デフォルト: 1）

---

## 使用例

### 単一ファイルを libx265 で変換する最小コマンド

```bash
python encode_h265.py "input.mpg" 
```

### 単一ファイルを libx265 で変換

```bash
python encode_h265.py "input.mpg" -o out -e libx265 --quality 18 --preset ultrafast --ext mp4
```

### ディレクトリ内を NVENC で一括変換

```bash
python encode_h265.py "./videos" -o out -e hevc_nvenc --quality 18 --preset p5 --ext mp4 --threads 2
```

スクリプトは`Ctrl + C`で強制終了できます。

---

## 推奨設定の目安

- **SD画質 (640×480)** : Quality 22 ±2  
- **HD画質 (1280×720, 1920×1080)** : Quality 20〜22  
- **4K (3840×2160)** : Quality 18〜20  

---

## 注意事項

- FFmpeg がインストールされている必要があります (`ffmpeg -version` で確認)。  
- 出力ファイル名は入力と同じベース名で拡張子のみ変更されます。  
- GPU エンコーダの可否は環境依存です。

## FFmpegのインストール

### Mac

- Homebrewを使いインストールする方法  
https://fukatsu.tech/install-ffmpeg

- Homebrewを使わずインストールする方法  
https://cyber-tenchou.com/tips/20200904/

### Windows

https://qiita.com/Tadataka_Takahashi/items/9dcb0cf308db6f5dc31b


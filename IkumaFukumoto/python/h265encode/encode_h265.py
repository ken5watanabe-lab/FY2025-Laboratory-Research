#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Watanabe Lab (MAIDS & MSBS @ Tokushima University)
# Copyright (c) Ikuma Fukumoto
# Licensed under the MIT License. See LICENSE file in the project root for details.

"""
encode_h265_no_subs.py
----------------------
FFmpeg を Python から呼び出して H.265/HEVC にエンコードするユーティリティ。
"""

import argparse
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

VIDEO_EXTS = {".mpg", ".mpeg", ".mp4", ".mov", ".mkv", ".avi", ".mts", ".m2ts", ".ts", ".wmv", ".flv", ".webm"}

def which(cmd: str) -> Optional[str]:
    from shutil import which as _which
    return _which(cmd)

def build_ffmpeg_cmd(
    src: Path,
    dst: Path,
    encoder: str,
    quality: Optional[int],
    preset: str,
    extra_x265: Optional[str],
) -> List[str]:
    common = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats", "-i", str(src)]
    maps = ["-map", "0:v:0"]

    v = []
    if encoder == "libx265":
        v = ["-c:v", "libx265", "-preset", preset]
        if quality is None:
            quality = 18
        v += ["-crf", str(quality)]
        x265_params = ["strong-intra-smoothing=1", "rect=1", "amp=1", "aq-mode=3"]
        if extra_x265:
            x265_params.extend([p.strip() for p in extra_x265.split(":" ) if p.strip()])
        v += ["-x265-params", ":".join(x265_params)]
    elif encoder in {"hevc_nvenc", "hevc_qsv", "hevc_videotoolbox"}:
        v = ["-c:v", encoder, "-preset", preset]
        if quality is None:
            quality = 18
        if encoder == "hevc_nvenc":
            v += ["-rc", "vbr", "-cq", str(quality)]
        elif encoder == "hevc_qsv":
            v += ["-global_quality", str(quality)]
        elif encoder == "hevc_videotoolbox":
            v += ["-q", str(quality)]
    else:
        raise ValueError(f"Unsupported encoder: {encoder}")

    cmd = common + maps + v + [str(dst)]
    return cmd

def transcode_one(
    src: Path,
    out_dir: Path,
    ext: str,
    encoder: str,
    quality: Optional[int],
    preset: str,
    overwrite: bool,
    extra_x265: Optional[str],
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / (src.stem + f".{ext}")
    if dst.exists() and not overwrite:
        print(f"[SKIP] {dst} already exists", flush=True)
        return dst

    cmd = build_ffmpeg_cmd(
        src=src,
        dst=dst,
        encoder=encoder,
        quality=quality,
        preset=preset,
        extra_x265=extra_x265,
    )

    print("$ " + " ".join(shlex.quote(c) for c in cmd), flush=True)
    try:
        subprocess.run(cmd, check=True)
        print(f"[OK] {src.name} -> {dst.name}", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERR] {src} failed with code {e.returncode}", file=sys.stderr)
        raise
    return dst

def gather_inputs(path: Path):
    if path.is_file():
        return [path]
    return [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
   

def main():
    parser = argparse.ArgumentParser(description="FFmpeg-based H.265/HEVC transcoder (no subtitle handling)")
    parser.add_argument("input", type=Path, help="入力ファイルまたはディレクトリ")
    parser.add_argument("-o", "--out-dir", type=Path, default=Path("./out_h265"), help="出力ディレクトリ")
    parser.add_argument("--ext", default="mp4", choices=["mp4", "mkv"], help="出力コンテナ拡張子")
    parser.add_argument("-e", "--encoder", default="libx265",
                        choices=["libx265", "hevc_nvenc", "hevc_videotoolbox", "hevc_qsv"],
                        help="映像エンコーダ（CPU/GPU）")
    parser.add_argument("--quality", type=int, default=None, help="画質指標 (libx265 用: CRF, NVENC/QSV/VTB 用: CQ)")
    parser.add_argument("--preset", default="ultrafast", help="速度/圧縮バランスプリセット")
    parser.add_argument("--overwrite", action="store_true", help="既存ファイルを上書き")
    parser.add_argument("--threads", type=int, default=1, help="並列処理数（ディレクトリ時のみ）")
    parser.add_argument("--x265-params", dest="x265_params", default=None,
                        help="x265 追加パラメータ（例: 'no-sao=1:ref=4'）")
    args = parser.parse_args()

    if not which("ffmpeg"):
        print("エラー: ffmpeg が見つかりません。PATH を確認してください。", file=sys.stderr)
        sys.exit(1)

    inputs = gather_inputs(args.input)
    if not inputs:
        print("入力ファイルが見つかりませんでした。", file=sys.stderr)
        sys.exit(1)

    if len(inputs) == 1:
        transcode_one(
            src=inputs[0],
            out_dir=args.out_dir,
            ext=args.ext,
            encoder=args.encoder,
            quality=args.quality,
            preset=args.preset,
            overwrite=args.overwrite,
            extra_x265=args.x265_params,
        )
    else:
        print(f"{len(inputs)} 本の動画を処理します（並列 {args.threads}）")
        with ThreadPoolExecutor(max_workers=max(1, args.threads)) as ex:
            futures = []
            for src in inputs:
                futures.append(ex.submit(
                    transcode_one,
                    src, args.out_dir, args.ext, args.encoder, args.quality, args.preset,
                    args.overwrite, args.x265_params
                ))
            for f in as_completed(futures):
                _ = f.result()

if __name__ == "__main__":
    main()

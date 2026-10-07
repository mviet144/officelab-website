#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/lam-anh.py
Render OG images và favicons cho website Office Lab bằng Microsoft Edge headless và Pillow.
Chạy từ thư mục gốc của repo:
    python scripts/lam-anh.py
"""

import sys
import subprocess
import time
from pathlib import Path
from PIL import Image

def find_edge_path() -> Path:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in candidates:
        if p.is_file():
            return p
    # Fallback: kiểm tra xem có trên PATH không
    return candidates[0]

def render_page(edge_path: Path, html_path: Path, out_path: Path, width: int, height: int):
    file_uri = html_path.resolve().as_uri()
    # Profile riêng: nếu Edge của người dùng đang mở, lệnh headless sẽ không bị "gộp" vào phiên đó.
    profile = out_path.resolve().parent / "edge-profile"
    out_path.unlink(missing_ok=True)
    cmd = [
        str(edge_path),
        "--headless=new",
        f"--user-data-dir={profile}",
        "--no-first-run",
        "--hide-scrollbars",
        "--disable-gpu",
        "--allow-file-access-from-files",
        "--virtual-time-budget=5000",
        f"--window-size={width},{height}",
        f"--screenshot={str(out_path.resolve())}",
        file_uri,
    ]
    print(f"-> Dang render {html_path.name} ({width}x{height})...")
    subprocess.run(cmd, check=True, timeout=60, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Edge có thể trả về trước khi ghi xong ảnh: chờ tối đa 60 giây.
    for _ in range(120):
        if out_path.is_file() and out_path.stat().st_size > 0:
            time.sleep(1)
            break
        time.sleep(0.5)
    if not out_path.is_file():
        raise RuntimeError(f"Edge khong tao duoc file anh tai {out_path}")

def get_resample_filter():
    if hasattr(Image, "Resampling"):
        return Image.Resampling.LANCZOS
    return Image.LANCZOS

def main():
    root = Path.cwd().resolve()
    tmp_dir = root / "_tmp"
    site_dir = root / "site"
    img_dir = site_dir / "assets" / "img"

    tmp_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    edge_path = find_edge_path()
    if not edge_path.is_file():
        print(f"[CANH-BAO] Khong tim thay Edge tai {edge_path}. Vui long kiem tra lai duong dan Edge.")

    resample = get_resample_filter()

    # 1. Render OG VI
    src_dir = root / "scripts" / "anh"
    og_vi_html = src_dir / "og-vi.html"
    og_vi_raw = tmp_dir / "og-vi-raw.png"
    og_vi_out = img_dir / "og-vi.png"
    render_page(edge_path, og_vi_html, og_vi_raw, 1200, 630)
    with Image.open(og_vi_raw) as im:
        if im.size != (1200, 630):
            if im.width >= 1200 and im.height >= 630:
                im_cropped = im.crop((0, 0, 1200, 630))
            else:
                im_cropped = im.resize((1200, 630), resample=resample)
            im_cropped.save(og_vi_out, format="PNG", optimize=True)
        else:
            im.save(og_vi_out, format="PNG", optimize=True)

    # 2. Render OG EN
    og_en_html = src_dir / "og-en.html"
    og_en_raw = tmp_dir / "og-en-raw.png"
    og_en_out = img_dir / "og-en.png"
    render_page(edge_path, og_en_html, og_en_raw, 1200, 630)
    with Image.open(og_en_raw) as im:
        if im.size != (1200, 630):
            if im.width >= 1200 and im.height >= 630:
                im_cropped = im.crop((0, 0, 1200, 630))
            else:
                im_cropped = im.resize((1200, 630), resample=resample)
            im_cropped.save(og_en_out, format="PNG", optimize=True)
        else:
            im.save(og_en_out, format="PNG", optimize=True)

    # 3. Render icon 256
    icon_html = src_dir / "icon-256.html"
    icon_raw = tmp_dir / "icon-256-raw.png"
    render_page(edge_path, icon_html, icon_raw, 256, 256)
    with Image.open(icon_raw) as im:
        if im.size != (256, 256):
            if im.width >= 256 and im.height >= 256:
                im_icon = im.crop((0, 0, 256, 256))
            else:
                im_icon = im.resize((256, 256), resample=resample)
        else:
            im_icon = im.copy()

        # a. apple-touch-icon.png 180x180
        apple_touch_out = site_dir / "apple-touch-icon.png"
        icon_180 = im_icon.resize((180, 180), resample=resample)
        icon_180.save(apple_touch_out, format="PNG", optimize=True)

        # b. favicon.ico (16, 32)
        favicon_out = site_dir / "favicon.ico"
        im_icon.save(favicon_out, format="ICO", sizes=[(16, 16), (32, 32)])

    # 4. In thong tin ket qua
    outputs = [
        ("OG VI", og_vi_out),
        ("OG EN", og_en_out),
        ("Apple Touch Icon", apple_touch_out),
        ("Favicon ICO", favicon_out),
    ]

    print("\n--- KET QUA XUAT ANH ---")
    for label, path in outputs:
        if path.is_file():
            size_bytes = path.stat().st_size
            try:
                with Image.open(path) as img:
                    dim = f"{img.width}x{img.height}"
            except Exception:
                dim = "ICO"
            print(f"- {label} ({path.relative_to(root)}): {dim}, {size_bytes:,} bytes")
        else:
            print(f"- [LOI] Khong tim thay {path}")

if __name__ == "__main__":
    main()

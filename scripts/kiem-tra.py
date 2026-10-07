#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/kiem-tra.py
Kiểm tra cấu trúc, SEO, CSP, tính toàn vẹn liên kết và nội dung cho website Office Lab.
Chạy từ thư mục gốc:
    python scripts/kiem-tra.py [--site site]
"""

import sys
import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse

# Ký tự emoji theo dải Unicode chỉ định
EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]')
# Hashtag: dấu # đứng trước chữ/số
HASHTAG_PATTERN = re.compile(r'#[A-Za-z0-9_\u00C0-\u1EF9]+')
# Mã lỗi Excel: không phải hashtag
EXCEL_ERROR_PATTERN = re.compile(r'#(?:N/A|REF!|VALUE!|DIV/0!|NAME\?|NUM!|NULL!)')
# Placeholder: [IN_HOA]
PLACEHOLDER_PATTERN = re.compile(r'\[[A-Z][A-Z0-9_\s-]*\]')
# Lorem ipsum
LOREM_PATTERN = re.compile(r'\blorem\b', re.IGNORECASE)

BUZZWORDS = [
    "giải pháp toàn diện",
    "cách mạng",
    "vượt trội",
    "đột phá",
    "tối ưu hoá toàn diện",
    "revolutionary",
    "cutting-edge",
    "game-changer",
    "seamless",
    "unlock",
    "empower",
    "leverage",
    "next-level",
]

class HTMLPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html_lang = None
        self.titles = []
        self._in_title = False
        self._current_title = []
        self.meta_descriptions = []
        self.canonical = None
        self.og_tags = {}
        self.hreflang_links = {}
        self.internal_links = []  # (tag, attr, url, line)
        self.scripts = []         # (line, col)
        self.inline_styles = []   # (tag, style_val, line)
        self.visible_text = []
        self._in_script = False
        self._in_style = False
        self.comments = []        # (comment_text, line)

    def handle_starttag(self, tag, attrs):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_lower = tag.lower()
        pos = self.getpos()

        if tag_lower == "html":
            self.html_lang = attr_dict.get("lang")

        if "style" in attr_dict:
            self.inline_styles.append((tag_lower, attr_dict["style"], pos[0]))

        if tag_lower == "script":
            self.scripts.append(pos)
            self._in_script = True

        if tag_lower == "style":
            self._in_style = True

        if tag_lower == "title":
            self._in_title = True
            self._current_title = []

        if tag_lower == "meta":
            name = attr_dict.get("name", "").lower()
            prop = attr_dict.get("property", "").lower()
            content = attr_dict.get("content", "")
            if name == "description":
                self.meta_descriptions.append(content)
            if prop.startswith("og:"):
                self.og_tags[prop] = content

        if tag_lower == "link":
            rel = attr_dict.get("rel", "").lower()
            href = attr_dict.get("href", "")
            if rel == "canonical":
                self.canonical = href
            if "alternate" in rel and "hreflang" in attr_dict:
                self.hreflang_links[attr_dict["hreflang"].lower()] = href

        for a in ("href", "src"):
            if a in attr_dict:
                val = attr_dict[a].strip()
                if val.startswith("/"):
                    self.internal_links.append((tag_lower, a, val, pos[0]))

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower == "title":
            self._in_title = False
            self.titles.append("".join(self._current_title).strip())
        elif tag_lower == "script":
            self._in_script = False
        elif tag_lower == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_title:
            self._current_title.append(data)
        if not self._in_script and not self._in_style:
            self.visible_text.append(data)

    def handle_comment(self, data):
        pos = self.getpos()
        self.comments.append((data, pos[0]))

def get_expected_canonical(site_dir: Path, file_path: Path) -> str:
    rel_posix = file_path.relative_to(site_dir).as_posix()
    if rel_posix == "index.html":
        url_path = "/"
    elif rel_posix.endswith("/index.html"):
        url_path = "/" + rel_posix[:-len("index.html")]
    else:
        url_path = "/" + rel_posix
    return f"https://officelab.site{url_path}"

def url_to_local_file(site_dir: Path, url: str) -> Path:
    parsed = urlparse(url)
    path = parsed.path
    if not path or path == "/":
        return site_dir / "index.html"
    path = path.lstrip("/")
    if path.endswith("/"):
        return site_dir / path / "index.html"
    candidate = site_dir / path
    if candidate.is_dir():
        return candidate / "index.html"
    return candidate

def main():
    parser = argparse.ArgumentParser(description="Kiem tra tinh hop le cua website Office Lab")
    parser.add_argument("--site", default="site", help="Duong dan thu muc site can kiem tra (mac dinh: site)")
    args = parser.parse_args()

    site_dir = Path(args.site).resolve()
    if not site_dir.is_dir():
        print(f"[LOI] Thu muc site khong ton tai: {site_dir}")
        sys.exit(1)

    html_files = sorted(site_dir.rglob("*.html"))
    if not html_files:
        print(f"[CANH-BAO] Khong tim thay file HTML nao trong {site_dir}")

    loi_count = 0
    canh_bao_count = 0

    def bao_loi(file_rel: str, mo_ta: str):
        nonlocal loi_count
        loi_count += 1
        print(f"[LOI] {file_rel}: {mo_ta}")

    def bao_canh_bao(file_rel: str, mo_ta: str):
        nonlocal canh_bao_count
        canh_bao_count += 1
        print(f"[CANH-BAO] {file_rel}: {mo_ta}")

    # Thu thap thong tin parse cua tung file
    page_data = {}
    for html_file in html_files:
        rel_posix = html_file.relative_to(site_dir).as_posix()
        try:
            content = html_file.read_text(encoding="utf-8")
        except Exception as e:
            bao_loi(rel_posix, f"Khong doc duoc file: {e}")
            continue

        p = HTMLPageParser()
        p.feed(content)
        page_data[html_file] = p

    # Doc sitemap.xml
    sitemap_file = site_dir / "sitemap.xml"
    sitemap_urls = set()
    if not sitemap_file.is_file():
        bao_loi("sitemap.xml", "Khong tim thay file sitemap.xml trong thu muc site")
    else:
        try:
            tree = ET.parse(sitemap_file)
            root = tree.getroot()
            # Ho tro ca co namespace lan khong co namespace
            for elem in root.iter():
                if elem.tag.endswith("loc") and elem.text:
                    sitemap_urls.add(elem.text.strip())
        except Exception as e:
            bao_loi("sitemap.xml", f"Loi parse XML: {e}")

    # 1 - 6, 8 - 11: Kiem tra tung trang HTML
    for html_file, p in page_data.items():
        rel_posix = html_file.relative_to(site_dir).as_posix()
        is_404 = (rel_posix == "404.html")
        is_en = rel_posix.startswith("en/")

        # 1. Kiem tra lang
        if is_en:
            if p.html_lang != "en":
                bao_loi(rel_posix, f"Trang thuoc en/ phai co lang=\"en\" (hien tai: lang=\"{p.html_lang}\")")
        elif is_404:
            if p.html_lang not in ("vi", "en"):
                bao_loi(rel_posix, f"Trang 404.html phai co lang=\"vi\" hoac lang=\"en\" (hien tai: lang=\"{p.html_lang}\")")
        else:
            if p.html_lang != "vi":
                bao_loi(rel_posix, f"Trang phai co lang=\"vi\" (hien tai: lang=\"{p.html_lang}\")")

        # 2. Kiem tra <title> va <meta name="description">
        if len(p.titles) == 0:
            bao_loi(rel_posix, "Thieu the <title>")
        elif len(p.titles) > 1:
            bao_loi(rel_posix, f"Co nhieu hon 1 the <title> ({len(p.titles)})")
        elif not p.titles[0]:
            bao_loi(rel_posix, "The <title> bi rong")

        if len(p.meta_descriptions) == 0:
            bao_loi(rel_posix, "Thieu the <meta name=\"description\">")
        elif len(p.meta_descriptions) > 1:
            bao_loi(rel_posix, f"Co nhieu hon 1 the <meta name=\"description\"> ({len(p.meta_descriptions)})")
        elif not p.meta_descriptions[0]:
            bao_loi(rel_posix, "The <meta name=\"description\"> bi rong")
        else:
            desc = p.meta_descriptions[0]
            if len(desc) > 170:
                bao_canh_bao(rel_posix, f"Meta description dai qua 170 ky tu ({len(desc)} ky tu)")

        # 3. Kiem tra canonical (bo qua 404)
        expected_canonical = get_expected_canonical(site_dir, html_file)
        if not is_404:
            if not p.canonical:
                bao_loi(rel_posix, f"Thieu the <link rel=\"canonical\"> (ky vong: {expected_canonical})")
            elif p.canonical != expected_canonical:
                bao_loi(rel_posix, f"Canonical khong khop: co '{p.canonical}', ky vong '{expected_canonical}'")

        # 4. Kiem tra Open Graph (bo qua 404)
        if not is_404:
            required_og = ["og:title", "og:description", "og:url", "og:image", "og:type", "og:locale"]
            for rog in required_og:
                if rog not in p.og_tags or not p.og_tags[rog]:
                    bao_loi(rel_posix, f"Thieu the Open Graph '{rog}'")

            og_img = p.og_tags.get("og:image", "")
            if og_img:
                if not og_img.startswith("https://"):
                    bao_loi(rel_posix, f"og:image phai la URL tuyet doi (hien tai: '{og_img}')")
                else:
                    target_img_file = url_to_local_file(site_dir, og_img)
                    if not target_img_file.is_file():
                        bao_loi(rel_posix, f"File anh og:image khong ton tai tai '{target_img_file.relative_to(site_dir).as_posix()}'")

        # 5. Kiem tra hreflang (bo qua 404)
        if not is_404:
            for req_lang in ("vi", "en", "x-default"):
                if req_lang not in p.hreflang_links:
                    bao_loi(rel_posix, f"Thieu the hreflang='{req_lang}'")

            for hlang, hurl in p.hreflang_links.items():
                target_f = url_to_local_file(site_dir, hurl)
                if not target_f.is_file():
                    bao_loi(rel_posix, f"URL hreflang '{hlang}' ({hurl}) tro toi trang khong ton tai ({target_f.name})")
                else:
                    # Kiem tra cap doi 2 chieu (reciprocal check)
                    target_parser = page_data.get(target_f)
                    if target_parser:
                        # Trang dich phai co hreflang tro nguoc lai trang hien tai
                        if expected_canonical not in target_parser.hreflang_links.values():
                            bao_loi(rel_posix, f"Hreflang khong doi xung: '{rel_posix}' tro toi '{hurl}', nhung trang dich khong tro nguoc lai '{expected_canonical}'")

        # 6. Kiem tra link noi bo (href/src bat dau bang /)
        for tag, attr, url_val, line_no in p.internal_links:
            clean_url = url_val.split("?")[0].split("#")[0]
            if clean_url == "":
                target_file = site_dir / "index.html"
            else:
                target_file = url_to_local_file(site_dir, clean_url)

            if not target_file.is_file():
                bao_loi(rel_posix, f"Dong {line_no}: <{tag} {attr}=\"{url_val}\"> tro toi file khong ton tai")

        # 7. Kiem tra sitemap (bo qua 404)
        if not is_404 and sitemap_file.is_file():
            if expected_canonical not in sitemap_urls:
                bao_loi(rel_posix, f"Trang chua duoc khai bao trong sitemap.xml ({expected_canonical})")

        # 8. Script va Style inline
        if len(p.scripts) > 0:
            bao_canh_bao(rel_posix, f"Co {len(p.scripts)} the <script> (site khong nen dung script theo CSP)")

        for tag, sval, line_no in p.inline_styles:
            bao_loi(rel_posix, f"Dong {line_no}: Co thuoc tinh style inline tren <{tag}>: style=\"{sval}\" (CSP chan style inline)")

        # 9, 10. Van ban hien thi (loai bo tag, comment)
        full_text = " ".join(p.visible_text)

        # 9a. Emoji
        emojis = EMOJI_PATTERN.findall(full_text)
        if emojis:
            unique_emojis = list(dict.fromkeys(emojis))
            bao_loi(rel_posix, f"Chua emoji trong van ban: {' '.join(unique_emojis)}")

        # 9b. Hashtag (bỏ qua mã lỗi Excel như #N/A, #REF! — site cố ý dùng làm chi tiết thiết kế)
        hashtags = HASHTAG_PATTERN.findall(EXCEL_ERROR_PATTERN.sub(" ", full_text))
        if hashtags:
            unique_ht = list(dict.fromkeys(hashtags))
            bao_loi(rel_posix, f"Chua hashtag trong van ban: {', '.join(unique_ht)}")

        # 9c. Buzzwords
        text_lower = full_text.lower()
        found_bw = []
        for bw in BUZZWORDS:
            # Dung regex de khong bat nham tu con
            pattern = rf'(?<![\w\u00C0-\u1EF9]){re.escape(bw.lower())}(?![\w\u00C0-\u1EF9])'
            if re.search(pattern, text_lower):
                found_bw.append(bw)
        if found_bw:
            bao_loi(rel_posix, f"Chua cum tu sao rong: {', '.join(found_bw)}")

        # 10. Placeholder va Lorem
        placeholders = PLACEHOLDER_PATTERN.findall(full_text)
        if placeholders:
            unique_ph = list(dict.fromkeys(placeholders))
            bao_canh_bao(rel_posix, f"Chua placeholder: {', '.join(unique_ph)}")

        if LOREM_PATTERN.search(full_text):
            bao_canh_bao(rel_posix, "Chua chu lorem / van ban gia lap")

        # 11. Comment chua TODO
        for ctext, cline in p.comments:
            if "TODO" in ctext:
                bao_canh_bao(rel_posix, f"Dong {cline}: Comment chua TODO: {ctext.strip()}")

    # 7b. Kiem tra nguoc: moi URL trong sitemap phai co file tuong ung
    if sitemap_file.is_file():
        for sm_url in sorted(sitemap_urls):
            local_target = url_to_local_file(site_dir, sm_url)
            if not local_target.is_file():
                bao_loi("sitemap.xml", f"URL trong sitemap khong co file tuong ung: {sm_url} -> {local_target.name}")

    print("\n--- TONG KET KIEM TRA ---")
    print(f"Tong so LOI: {loi_count}")
    print(f"Tong so CANH-BAO: {canh_bao_count}")

    if loi_count > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()

# Office Lab Website

Website tĩnh của Office Lab — nơi giới thiệu các công cụ tự động hoá và file Excel giúp kế toán và dân văn phòng cắt giảm những thao tác thủ công lặp đi lặp lại.

## Cấu trúc thư mục

```text
├── .github/workflows/
│   └── azure-static-web-apps.yml   # Workflow tự động deploy lên Azure Static Web Apps
├── site/                           # Thư mục chính chứa toàn bộ mã nguồn deploy
│   ├── assets/
│   │   ├── css/                    # Stylesheet dùng chung (style.css)
│   │   ├── fonts/                  # Font tự host (WOFF2, OFL): Newsreader, Be Vietnam Pro, IBM Plex Mono
│   │   └── img/                    # Ảnh Open Graph (og-vi.png, og-en.png)
│   ├── cong-cu/                    # Các trang công cụ tiếng Việt
│   │   └── invoicextract/
│   ├── en/                         # Toàn bộ phiên bản tiếng Anh
│   │   ├── tools/invoicextract/
│   │   ├── privacy/
│   │   └── index.html
│   ├── privacy/                    # Chính sách quyền riêng tư tiếng Việt
│   ├── index.html                  # Trang chủ tiếng Việt
│   ├── 404.html                    # Trang thông báo không tìm thấy (song ngữ)
│   ├── favicon.svg                 # Favicon vector
│   ├── favicon.ico                 # Favicon đa kích thước (16x16, 32x32)
│   ├── apple-touch-icon.png        # Icon dành cho thiết bị Apple (180x180)
│   ├── robots.txt                  # Cấu hình bot tìm kiếm
│   ├── sitemap.xml                 # Sơ đồ website đa ngôn ngữ
│   └── staticwebapp.config.json    # Cấu hình routing, security headers và CSP cho Azure
├── templates/                      # Mẫu tạo thẻ và trang công cụ mới
│   ├── the-cong-cu.html
│   ├── trang-cong-cu.vi.html
│   └── trang-cong-cu.en.html
├── scripts/                        # Script tự động hoá nội bộ
│   ├── kiem-tra.py                 # Kiểm tra SEO, link nội bộ, CSP và văn phong
│   ├── lam-anh.py                  # Render ảnh OG và favicon bằng Edge headless
│   ├── anh/                        # Trang HTML nguồn để render ảnh OG và icon
│   └── test-kiem-tra/              # Trang cố tình sai, để thử kiem-tra.py
├── _tmp/                           # Thư mục chứa file tạm (được bỏ qua bởi .gitignore)
├── HUONG-DAN-THEM-CONG-CU.md       # Hướng dẫn chi tiết quy trình thêm công cụ
└── README.md
```

## Chạy thử trên máy cá nhân (Local)

Khởi động web server tĩnh bằng lệnh:

```bash
python -m http.server 8080 --directory site
```

Mở trình duyệt truy cập: `http://localhost:8080/`.

## Kiểm tra chất lượng website

Chạy script kiểm tra từ thư mục gốc của dự án:

```bash
python scripts/kiem-tra.py
```

Script sẽ rà soát:
- Cấu trúc thẻ `<html lang>`, `<title>`, `<meta name="description">`, `<link rel="canonical">`.
- Khai báo Open Graph và kiểm tra file ảnh `og:image`.
- Cặp thẻ `hreflang` hai chiều (`vi`, `en`, `x-default`).
- Tính toàn vẹn của liên kết nội bộ (`href`, `src` bắt đầu bằng `/`).
- Khai báo đồng bộ với `sitemap.xml`.
- Không sử dụng thẻ `<script>` hoặc thuộc tính `style` inline (tuân thủ Content Security Policy).
- Phát hiện emoji, hashtag, từ ngữ quảng cáo sáo rỗng hoặc placeholder chưa điền.

Để kiểm tra một thư mục khác (ví dụ bộ kiểm thử):
```bash
python scripts/kiem-tra.py --site scripts/test-kiem-tra
```

## Làm lại ảnh OG và favicon

Sửa `scripts/anh/*.html` hoặc `site/favicon.svg`, rồi chạy (cần Microsoft Edge và Pillow):

```bash
python scripts/lam-anh.py
```

## Triển khai (Deploy)

Website được cấu hình triển khai tự động qua GitHub Actions lên Azure Static Web Apps mỗi khi có commit được push vào nhánh `main`.

## Thêm công cụ mới

Khi cần bổ sung một công cụ mới vào website, vui lòng xem hướng dẫn chi tiết từng bước tại [HUONG-DAN-THEM-CONG-CU.md](HUONG-DAN-THEM-CONG-CU.md).

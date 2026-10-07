# Hướng dẫn thêm một công cụ mới

Ví dụ dưới đây thêm công cụ tên **BaoCaoThang**, slug `bao-cao-thang`.

Slug là phần đường dẫn: chữ thường, không dấu, nối bằng gạch ngang, không đổi sau khi đã đăng (đổi slug là link cũ chết). Dùng cùng một slug cho cả hai bản ngôn ngữ.

Mọi trang dùng chung `site/assets/css/style.css`. Không viết `style="..."` trong HTML và không thêm `<script>`: chính sách bảo mật (CSP) của site chặn cả hai.

---

## Bước 1. Chuẩn bị nội dung

Trước khi đụng vào file, viết sẵn cho cả tiếng Việt và tiếng Anh:

| Mục | Ghi chú |
|---|---|
| Tên công cụ | |
| Một câu: công cụ giải quyết việc gì | dùng cho thẻ ở trang chủ |
| Đối tượng dùng | ví dụ "kế toán tổng hợp" |
| Trạng thái | Đang dùng thật / Thử nghiệm / Sắp ra mắt |
| Vấn đề | 1–2 đoạn |
| Công cụ làm gì | 3–6 gạch đầu dòng |
| Đầu vào, đầu ra | |
| Giới hạn hiện tại | nói thẳng, kể cả điều chưa kiểm chứng |
| Mô tả meta | dưới 160 ký tự |

Giọng văn: xưng "mình", gọi "bạn". Không emoji, không hashtag, không "giải pháp toàn diện", "cách mạng", "vượt trội". **Không ghi con số nào chưa đo thật.** Bản tiếng Anh viết lại cho tự nhiên, không dịch từng chữ.

## Bước 2. Thêm thẻ vào trang chủ

Danh mục ở trang chủ là một bảng (`<table class="catalog">`), mỗi công cụ là một dòng. Trên điện thoại, CSS tự chuyển mỗi dòng thành một khối dọc.

1. Mở `templates/the-cong-cu.html`.
2. Copy khối `<tr class="is-tool">` bản tiếng Việt, dán vào `<tbody>` của bảng trong `site/index.html`, ngay **trên** dòng `<tr class="is-next">`.
3. Làm tương tự với khối bản tiếng Anh trong `site/en/index.html`.
4. Thay mọi `{{...}}`. Mã công cụ đánh tiếp theo thứ tự (`OL-02`, `OL-03`...), rồi tăng mã ở dòng `is-next` lên một số ở cả hai file.
5. Chọn đúng class con dấu trạng thái:

| Trạng thái | Class | Chữ VI | Chữ EN |
|---|---|---|---|
| Đang dùng thật | `stamp--dang-dung` | Đang dùng thật | In real use |
| Thử nghiệm | `stamp--thu-nghiem` | Thử nghiệm | Experimental |
| Sắp ra mắt | `stamp--sap-ra-mat` | Sắp ra mắt | Coming soon |

Công cụ "Sắp ra mắt" chưa có trang chi tiết thì bỏ thẻ `<a>` trong ô `name` (chỉ để tên), rồi bỏ qua bước 3 và 4.

## Bước 3. Tạo trang chi tiết

1. Tạo thư mục và copy template:
   - `templates/trang-cong-cu.vi.html` → `site/cong-cu/bao-cao-thang/index.html`
   - `templates/trang-cong-cu.en.html` → `site/en/tools/bao-cao-thang/index.html`
2. Trong cả hai file, thay toàn bộ `{{...}}`:
   - `{{SLUG}}` → `bao-cao-thang` (xuất hiện ở canonical, hreflang, og:url, link đổi ngôn ngữ)
   - `{{TEN_CONG_CU}}` → `BaoCaoThang`
   - `{{MA}}` → mã đã dùng ở bước 2, ví dụ `OL-02`
   - `{{TEN_CONG_CU_URL}}` → tên công cụ dùng làm tiêu đề email; dấu cách viết thành `%20`
   - các ô nội dung còn lại theo bước 1
3. Cần thêm gạch đầu dòng thì nhân bản thẻ `<li>`. Cần thêm đoạn thì nhân bản `<p>`.
4. Tìm trong file xem còn sót `{{` không. Không được còn.

## Bước 4. Cập nhật sitemap

Mở `site/sitemap.xml`, thêm **hai** khối `<url>` (một cho bản VI, một cho bản EN), copy theo khối của InvoiceXtract rồi đổi slug:

```xml
<url>
  <loc>https://officelab.site/cong-cu/bao-cao-thang/</loc>
  <lastmod>YYYY-MM-DD</lastmod>
  <xhtml:link rel="alternate" hreflang="vi" href="https://officelab.site/cong-cu/bao-cao-thang/"/>
  <xhtml:link rel="alternate" hreflang="en" href="https://officelab.site/en/tools/bao-cao-thang/"/>
  <xhtml:link rel="alternate" hreflang="x-default" href="https://officelab.site/cong-cu/bao-cao-thang/"/>
</url>
<url>
  <loc>https://officelab.site/en/tools/bao-cao-thang/</loc>
  <lastmod>YYYY-MM-DD</lastmod>
  <xhtml:link rel="alternate" hreflang="vi" href="https://officelab.site/cong-cu/bao-cao-thang/"/>
  <xhtml:link rel="alternate" hreflang="en" href="https://officelab.site/en/tools/bao-cao-thang/"/>
  <xhtml:link rel="alternate" hreflang="x-default" href="https://officelab.site/cong-cu/bao-cao-thang/"/>
</url>
```

Nếu sửa nội dung trang chủ, đổi luôn `<lastmod>` của `/` và `/en/`.

## Bước 5. Kiểm tra trước khi đẩy lên

Từ thư mục gốc của repo:

```bash
python scripts/kiem-tra.py
```

Script báo `[LOI]` nếu thiếu title/description/canonical/OG, hreflang không đi thành cặp, link nội bộ gãy, trang không có trong sitemap, có `style=` inline, có emoji hoặc từ sáo rỗng. `[CANH-BAO]` là nhắc nhở (ví dụ còn comment TODO), không chặn.

Xem thử trên máy:

```bash
python -m http.server 8080 --directory site
```

Mở `http://localhost:8080/cong-cu/bao-cao-thang/`, xem cả khổ điện thoại lẫn máy tính, và bấm thử link đổi ngôn ngữ.

## Bước 6. Đăng

Commit rồi push lên nhánh `main`. GitHub Actions tự deploy lên Azure Static Web Apps, thường mất vài phút. Xem tiến độ ở tab **Actions** của repo.

## Danh sách kiểm nhanh

- [ ] Thẻ có ở cả `site/index.html` và `site/en/index.html`
- [ ] Hai trang chi tiết đã tạo, không còn `{{`
- [ ] Nhãn trạng thái giống nhau ở thẻ và ở trang chi tiết, cả hai ngôn ngữ
- [ ] Sitemap có thêm 2 khối `<url>`
- [ ] `python scripts/kiem-tra.py` không còn `[LOI]`
- [ ] Không có con số nào chưa đo thật, không có ảnh dữ liệu thật của khách

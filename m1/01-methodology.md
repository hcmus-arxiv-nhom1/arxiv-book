# Phương pháp thu thập

<!-- Owner: Đăng, Thiên. Phần kỹ thuật crawler do Thiên viết với sự hỗ trợ của AI assistant (Claude, Anthropic), ghi nguồn theo quy định môn học. -->

Chương này mô tả cách nhóm thu thập corpus của Milestone 1: tìm các bài trong dải ID được giao, tải **mọi version** mã nguồn LaTeX, chỉ giữ `.tex` và `.bib`, và lấy metadata reference từ Semantic Scholar {cite}`hcmus-statement`. Code nằm trong [code repo](https://github.com/hcmus-arxiv-nhom1/CodeRepo) (`src/crawler/`, `src/run_pipeline.py`); schema dữ liệu nằm trong `docs/data_contract.md` của repo đó.

## Phạm vi dữ liệu

Nhóm phụ trách 20.000 arXiv ID, chia thành 4 dải × 5.000 ID theo bảng đăng ký:

| Thành viên | Dải ID |
| --- | --- |
| Cao Tiến Thiên | `2606.30734` → `2607.03693` |
| Trần Minh Tiến | `2606.25734` → `2606.30733` |
| Trương Lê Trung Hiếu | `2606.05734` → `2606.10733` |
| Lý Huỳnh Minh Đăng | `2604.20535` → `2604.25534` |

Số thứ tự arXiv bắt đầu lại từ `00001` ở mỗi tháng, nên dải `2606.30734` → `2607.03693` không phải một dãy số liên tục. Crawler sinh ID **theo từng tháng** (`iter_id_range`), dùng số thứ tự cuối của tháng 6. Số này được tìm bằng arXiv API: `2606.32040` tồn tại, `2606.32041` trở đi thì không. Vậy dải có đúng 1.307 + 3.693 = 5.000 ID.

## Quy trình crawl

```{mermaid}
flowchart LR
    R["Dải ID"] --> G["Sinh ID theo tháng"]
    G --> D["Discovery<br/>arXiv API id_list"]
    D -->|metadata.json| C[("corpus/&lt;yymm-id&gt;/")]
    D --> V["Hàng đợi version<br/>bỏ qua version đã xong"]
    V --> DL["Tải /src/{id}vN"]
    DL --> X["Nhận diện loại file<br/>chỉ giữ .tex, .bib"]
    X -->|vN/| C
    X -->|1 dòng / version| J[("work/versions.jsonl")]
    D -. thread riêng .-> S["Semantic Scholar<br/>POST /paper/batch"]
    S -->|references.json| C
```

1. **Discovery** {cite}`arxiv-api`. Gọi arXiv API `id_list` với 100 ID mỗi request, tức khoảng 50 request cho 5.000 ID. Kết quả cho title, authors, `journal_ref` (venue), DOI, và **ID của version mới nhất**: hậu tố `vN` cho biết bài có bao nhiêu version. `published` là ngày của v1, `updated` là ngày của version mới nhất. Bài có từ 3 version trở lên thì lấy ngày của v2…v(N-1) bằng truy vấn ID có version (`2606.30762v2`). OAI-PMH `arXivRaw` {cite}`arxiv-oai` là đường dự phòng cho ID mà API không trả về.
2. **Tải source.** Mỗi version được tải riêng qua `https://export.arxiv.org/src/{id}vN`, kể cả bài chỉ có `v1`. Body được ghi ra file `.part` và chỉ đổi tên khi đủ `Content-Length`.
3. **Nhận diện loại file bằng magic bytes**, không tin đuôi file {cite}`arxiv-mimetypes`:

   | Byte đầu | Loại | Xử lý |
   | --- | --- | --- |
   | `1f 8b` + header tar | `tar.gz` | Đọc từng member, chỉ ghi `.tex` và `.bib` |
   | `1f 8b`, bên trong là TeX | `gz` một file | Ghi thành một file `.tex` |
   | `1f 8b`, bên trong là HTML | `html.gz` | Bài nộp bằng HTML (vd. kỷ yếu EPTCS) → record rỗng |
   | `%PDF`, `%!PS` | Chỉ có PDF/PS | Record rỗng |
   | HTML không nén, HTTP 200 | Trang lỗi | `failed`, thử lại ở lần chạy sau |
   | HTTP 404/410 | Version không còn source | `unavailable`, record rỗng |

4. **Xoá hình bằng cách trích xuất** đúng như đề yêu cầu: chỉ ghi `.tex` và `.bib`, nên file hình không bao giờ vào corpus. Nội dung `.tex` giữ nguyên byte, môi trường `figure` và lệnh `\includegraphics` vẫn còn cho Milestone 2. Member có đường dẫn tuyệt đối, `..`, symlink hoặc tên không hợp lệ đều bị bỏ qua. Mỗi version ghi lại kích thước trước/sau khi lọc và danh sách đuôi file bị bỏ (`dropped`) vào `work/versions.jsonl`.
5. **Reference metadata** {cite}`s2-api`. Một thread riêng gọi `POST /paper/batch` của Semantic Scholar với 100 bài mỗi request. API trả về **toàn bộ** danh sách reference của từng bài, nên 20.000 bài chỉ cần khoảng 200 request. Mọi reference đều được lưu, có hay không có arXiv ID. Bài có danh sách quá dài được lấy lại đầy đủ qua endpoint `/paper/{id}/references` theo trang.

## Politeness

Terms of Use của arXiv yêu cầu *"no more than 1 request every 3 seconds"* và một kết nối tại một thời điểm, tính trên mọi máy của nhóm {cite}`arxiv-tou`.

- **Một `RateLimiter` dùng chung** cho mọi request tới arXiv (API, OAI-PMH, `/src/`). Khoá được giữ suốt request, nên không bao giờ có hai request arXiv cùng lúc. Các lần bắt đầu request cách nhau ≥ 3 s cộng jitter ngẫu nhiên 0–0,1 s. `run.log` ghi `gap` của từng request để kiểm chứng; lần chạy thử ngày 27/10 đo được khoảng cách nhỏ nhất là 3,015 s.
- Chỉ gọi mirror `export.arxiv.org` và `oaipmh.arxiv.org`, không bao giờ gọi `arxiv.org`. User-Agent mô tả rõ đây là đồ án môn học.
- **Một lần chạy cho mỗi thư mục làm việc:** `run_pipeline` giữ khoá cấp hệ điều hành trên `work/run.lock`. Corpus được thu thập bằng **một** instance, chia ca giữa các thành viên, không chạy hai máy cùng lúc.
- **Retry:** lỗi kết nối, timeout, đứt kết nối giữa chừng, 429 và 5xx được thử lại tối đa 5 lần, backoff `2^n` giây cộng jitter, ưu tiên `Retry-After`. Ba lần 403 liên tiếp → dừng 15–30 phút và giảm nhịp còn 5 s; lặp lại quá 3 lần thì dừng hẳn để chạy lại sau.
- **Semantic Scholar có limiter riêng:** 1,1 s mỗi request khi có API key, 3 s khi không có, tương ứng giới hạn 100 request mỗi 5 phút.

## Cấu trúc dữ liệu đầu ra

```text
data/corpus/
  2606-30734/                # arXiv ID dạng yymm-id
    metadata.json            # arxiv_id, title, authors[], submission_date, revised_dates[], venue, num_versions
    references.json          # mọi reference S2 trả về: title, authors, ngày, arXiv ID (nếu có), S2 ID
    v1/                      # chỉ .tex/.bib; rỗng nếu version không có TeX
    v2/
work/
  versions.jsonl             # mỗi version một dòng: trạng thái, loại file, kích thước, file bị bỏ, thời gian
  discovery.jsonl  failed.csv  run_summary.json  run.log
```

`metadata.json` có đủ các cột của bảng `papers`; reference có arXiv ID trong `references.json` là nguồn của bảng `references` ở Milestone 3.

## Resume

Mỗi version xong được ghi ngay một dòng vào `work/versions.jsonl` (flush và fsync), nên dừng cứng cũng không mất dòng đã ghi. Chạy lại **đúng lệnh cũ** thì crawler bỏ qua version đã ở trạng thái cuối và thử lại version `failed`; `metadata.json` và `references.json` đã có cũng được bỏ qua. Trong lần chạy thử, dừng cứng sau 16 version rồi chạy lại: 16/16 version được bỏ qua, không có dòng ghi trùng.

## Định nghĩa "thành công"

- **Bài thành công:** bài có trên arXiv và **mọi version** đều ở trạng thái cuối `ok`, `no_tex` hoặc `unavailable`, kèm thư mục `vN/`. Version không có TeX vẫn được tính là đã crawl xong, vì đề yêu cầu giữ record rỗng chứ không bỏ bài. Định nghĩa này trùng với `papers_complete` trong `run_summary.json` và cột `n_versions_ok == n_versions` của notebook thống kê.
- **Success rate của reference metadata:** tỉ lệ bài mà Semantic Scholar trả về được (`status = ok`). Notebook báo thêm tỉ lệ reference S2 resolve được metadata (`s2_id` khác `null`).

## Quan sát từ lần chạy thử (4 × 200 ID, 19–20/10/2026, laptop)

Đây chưa phải benchmark chính thức; số đo hiệu năng ở chương [Hiệu năng](03-performance.ipynb) chạy trên Google Colab CPU-only.

- Sau khi chạy lại một lần, cả 4 dải đạt 200/200 bài đầy đủ. 57/1.061 version (5,4 %) không có TeX: PDF/HTML hoặc arXiv trả 404.
- Lỗi thường gặp nhất là arXiv đóng kết nối giữa chừng khi tải file lớn, và HTTP 429 vào giờ cao điểm. Cả hai đều được retry và resume xử lý.
- Giải nén chỉ mất 19 ms ở trung vị (p90 là 66 ms), không đáng kể so với nhịp 3 s. Vì vậy nhóm không tách giải nén ra process riêng; phần chạy song song có lợi là Semantic Scholar.
- Semantic Scholar: 700 bài đầu tiên chỉ cần 18 request batch. Trung bình 35,6 reference mỗi bài, 49,9 % reference có arXiv ID.

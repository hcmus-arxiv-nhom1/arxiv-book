# Milestone 1 — Thu thập dữ liệu

Milestone 1 thu thập mã nguồn LaTeX (chỉ giữ `.tex`, `.bib`) của mọi version cho dải ID arXiv được giao, cùng metadata bài báo và metadata reference từ Semantic Scholar {cite}`hcmus-statement`.

Các chương:

1. [Phương pháp](01-methodology.md): cách crawl, công cụ, politeness, cấu trúc dữ liệu, định nghĩa "thành công".
2. [Thống kê dữ liệu](02-data-stats.ipynb): success rate, kích thước trước/sau khi xoá hình, số reference.
3. [Hiệu năng](03-performance.ipynb): thời gian, RAM, disk trên Colab CPU-only.
4. [Thảo luận](04-discussion.md): kết quả, hạn chế, hướng cải thiện.

```{note}
Các số liệu hiện tại sinh từ **CSV giả** (`scripts/make_fake_data.py`) để book build được. Sẽ thay bằng CSV thật export từ code repo sau khi crawl và benchmark xong.
```

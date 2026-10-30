# arxiv-book — Nhóm 1

> **KHÔNG đổi tên org/repo đến hết hạn poster.** URL book nằm trong link nộp Moodle, đổi tên là link chết.

- Book: <https://hcmus-arxiv-nhom1.github.io/arxiv-book/>
- Code repo: <https://github.com/hcmus-arxiv-nhom1/CodeRepo>

Book dùng **Jupyter Book 2** (nền MyST). Cấu hình và mục lục nằm trong `myst.yml`.

## Build ở máy

```bash
pip install -r requirements.txt
pip install pre-commit && pre-commit install   # nbstripout: xoá output notebook trước khi commit
jupyter book start --execute                    # xem trực tiếp ở http://localhost:3000
jupyter book build --html --execute             # build tĩnh vào _build/html
```

## Notebook crawl và benchmark M1

Book nhúng `m1/arxiv_nhom1_crawl_benchmark.ipynb` như một trang chỉ đọc, có link mở đúng phiên bản trên Colab và tải notebook. Notebook có metadata `skip-execution`: CI vẫn execute các notebook phân tích CSV, nhưng không crawl, mount Drive hay đọc Secrets.

Bản gốc nằm ở `CodeRepo/src/notebooks/arxiv_nhom1_crawl_benchmark.ipynb`. Không sửa code cell của bản nhúng bằng tay. Để cập nhật từ một commit CodeRepo đã kiểm tra:

```bash
python scripts/sync_benchmark_notebook.py --code-repo ../CodeRepo --revision <COMMIT_SHA>
python scripts/check_benchmark_notebook.py --code-repo ../CodeRepo
jupyter book build --html --execute
```

Script lưu commit và SHA-256 của nguồn trong metadata; build Book không fetch notebook từ một branch thay đổi liên tục. Final benchmark cần toàn bộ 20.000 ID; số liệu sample và CSV giả không được ghi là final. Corpus/checkpoint lưu trên Drive của tài khoản crawl chung để dùng cho M2, không commit vào Book.

Trên Windows, nếu Node báo `fetch failed` khi kết nối Jupyter ở localhost, đặt `$env:NODE_OPTIONS = "--dns-result-order=ipv4first"` trong phiên PowerShell rồi build lại. Bản HTML tĩnh nằm tại `_build/html/index.html`; trang notebook nằm tại `_build/html/arxiv-nhom1-crawl-benchmark/index.html`.

## Quy tắc

- **Notebook không chứa output.** nbstripout xoá output khi commit; CI build với `--execute`, nên mọi figure/table sinh lúc compile.
- **Book chỉ đọc CSV trong `data/`**, không đọc dữ liệu thô. Schema chốt trong `docs/data_contract.md` của code repo.
- Dữ liệu trong `data/m1/` hiện là **CSV giả** sinh bởi `python scripts/make_fake_data.py`. Khi có số liệu thật, chỉ cần thay file, không sửa notebook.
- Cập nhật CSV thật: commit message ghi commit của code repo đã dùng, ví dụ `data: update m1 stats from CodeRepo@abc1234`.
- Mọi thay đổi vào `main` đi qua PR. CODEOWNERS tự gán reviewer; workflow `check` phải pass; người merge không phải tác giả.

## Cài đặt GitHub (một lần)

1. Settings → Pages → Source: **GitHub Actions**.
2. Settings → Branches: protect `main`, cần 1 approve, bắt buộc check `check`, không cho tác giả tự merge.

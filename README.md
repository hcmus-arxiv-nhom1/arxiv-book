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

## Quy tắc

- **Notebook không chứa output.** nbstripout xoá output khi commit; CI build với `--execute`, nên mọi figure/table sinh lúc compile.
- **Book chỉ đọc CSV trong `data/`**, không đọc dữ liệu thô. Schema chốt trong `docs/data_contract.md` của code repo.
- Dữ liệu trong `data/m1/` hiện là **CSV giả** sinh bởi `python scripts/make_fake_data.py`. Khi có số liệu thật, chỉ cần thay file, không sửa notebook.
- Cập nhật CSV thật: commit message ghi commit của code repo đã dùng, ví dụ `data: update m1 stats from CodeRepo@abc1234`.
- Mọi thay đổi vào `main` đi qua PR. CODEOWNERS tự gán reviewer; workflow `check` phải pass; người merge không phải tác giả.

## Cài đặt GitHub (một lần)

1. Settings → Pages → Source: **GitHub Actions**.
2. Settings → Branches: protect `main`, cần 1 approve, bắt buộc check `check`, không cho tác giả tự merge.

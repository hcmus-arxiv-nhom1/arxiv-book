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

Các notebook crawl và benchmark được duy trì trong [CodeRepo/src/notebooks](https://github.com/hcmus-arxiv-nhom1/CodeRepo/tree/main/src/notebooks). Book chứa báo cáo và notebook phân tích kết quả.

Final benchmark cần toàn bộ 20.000 ID; số liệu sample và CSV giả không được ghi là final. Corpus giữ dạng raw tại `runs/<RUN_ID>/data/corpus/` trên Drive. Smoke dùng run ID riêng với full crawl; restore và xác minh sau runtime loss. Không commit corpus vào Book.

Trên Windows, nếu Node báo `fetch failed` khi kết nối Jupyter ở localhost, đặt `$env:NODE_OPTIONS = "--dns-result-order=ipv4first"` trong phiên PowerShell rồi build lại. Bản HTML tĩnh nằm tại `_build/html/index.html`.

## Quy tắc

- **Notebook không chứa output.** nbstripout xoá output khi commit; CI build với `--execute`, nên mọi figure/table sinh lúc compile.
- **Book chỉ đọc CSV trong `data/`**, không đọc dữ liệu thô. Schema chốt trong `docs/data_contract.md` của code repo.
- Notebook Data Statistics và Performance đọc evidence đã đối chiếu trong `data/m1/final/`; các CSV giả cũ ở `data/m1/` không phải kết quả chính thức. Tái tạo bộ dữ liệu bằng `python scripts/collect_final_m1.py --workspace ..` khi workspace có đủ evidence và snapshot, sau đó kiểm tra `provenance.json` và các giới hạn QA/measurement.
- Cập nhật CSV thật: commit message ghi commit của code repo đã dùng, ví dụ `data: update m1 stats from CodeRepo@abc1234`.
- Mọi thay đổi vào `main` đi qua PR. CODEOWNERS tự gán reviewer; workflow `check` phải pass; người merge không phải tác giả.

## Cài đặt GitHub (một lần)

1. Settings → Pages → Source: **GitHub Actions**.
2. Settings → Branches: protect `main`, cần 1 approve, bắt buộc check `check`, không cho tác giả tự merge.

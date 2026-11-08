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

Book nhúng `m1/arxiv_nhom1_only_v1_benchmark.ipynb` và `m1/arxiv_nhom1_multi_version_benchmark.ipynb` như hai trang chỉ đọc, có link mở phiên bản đã pin trên Colab và tải notebook. Cả hai có metadata `skip-execution`: CI vẫn execute các notebook phân tích CSV, nhưng không crawl, mount Drive hay đọc Secrets.

Bản gốc nằm trong `CodeRepo/src/notebooks/` với cùng tên. Không sửa code cell của bản nhúng bằng tay. Để cập nhật từ một commit CodeRepo đã kiểm tra:

```bash
python scripts/sync_split_notebooks.py --code-repo ../CodeRepo --revision <COMMIT_SHA> --repository <OWNER/REPO>
python scripts/test_split_notebook_mirrors.py
jupyter book build --html --execute
```

Script lưu commit và SHA-256 của nguồn trong metadata; build Book không fetch notebook từ một branch thay đổi liên tục. Final benchmark cần toàn bộ 20.000 ID; số liệu sample và CSV giả không được ghi là final. Corpus giữ dạng raw tại `runs/<RUN_ID>/data/corpus/` trên Drive, hoặc theo shard trên HF và khôi phục về cây local phẳng cho M2. Smoke dùng run ID riêng với full crawl; restore và xác minh sau runtime loss. Không commit corpus vào Book.

Trên Windows, nếu Node báo `fetch failed` khi kết nối Jupyter ở localhost, đặt `$env:NODE_OPTIONS = "--dns-result-order=ipv4first"` trong phiên PowerShell rồi build lại. Bản HTML tĩnh nằm tại `_build/html/index.html`; hai notebook có trang riêng trong mục lục M1.

## Quy tắc

- **Notebook không chứa output.** nbstripout xoá output khi commit; CI build với `--execute`, nên mọi figure/table sinh lúc compile.
- **Book chỉ đọc CSV trong `data/`**, không đọc dữ liệu thô. Schema chốt trong `docs/data_contract.md` của code repo.
- Notebook Data Statistics và Performance đọc evidence đã đối chiếu trong `data/m1/final/`; các CSV giả cũ ở `data/m1/` không phải kết quả chính thức. Tái tạo bộ dữ liệu bằng `python scripts/collect_final_m1.py --workspace ..` khi workspace có đủ evidence và snapshot, sau đó kiểm tra `provenance.json` và các giới hạn QA/measurement.
- Cập nhật CSV thật: commit message ghi commit của code repo đã dùng, ví dụ `data: update m1 stats from CodeRepo@abc1234`.
- Mọi thay đổi vào `main` đi qua PR. CODEOWNERS tự gán reviewer; workflow `check` phải pass; người merge không phải tác giả.

## Cài đặt GitHub (một lần)

1. Settings → Pages → Source: **GitHub Actions**.
2. Settings → Branches: protect `main`, cần 1 approve, bắt buộc check `check`, không cho tác giả tự merge.

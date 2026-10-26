# Phương pháp thu thập

```{note}
Chương này đang soạn (owner: Đăng, Thiên).
```

## Phạm vi dữ liệu

`TODO`: dải ID của từng thành viên (xem `src/config.py` trong code repo).

## Quy trình crawl

`TODO`: discovery qua arXiv API {cite}`arxiv-api` (OAI-PMH dự phòng), tải `/src/{id}vN`, nhận diện loại file, chỉ giữ `.tex`/`.bib`; reference metadata từ Semantic Scholar {cite}`s2-api`.

## Politeness

`TODO`: một `RateLimiter` dùng chung, ≥ 3 s giữa các request + jitter, retry/backoff, tôn trọng `Retry-After` theo Terms of Use {cite}`arxiv-tou`.

## Cấu trúc dữ liệu đầu ra

`TODO`: cây thư mục `data/corpus/<yymm-id>/{metadata.json, references.json, vN/}`.

## Định nghĩa "thành công"

`TODO — chốt trước khi viết số liệu`. Đề xuất: một bài **thành công** khi **mọi version** của bài đều có trạng thái cuối `ok`, `no_tex` hoặc `unavailable` (trùng với `papers_complete` trong `run_pipeline.py`). Notebook 02 hiện dùng `n_versions_ok == n_versions`; nếu đổi định nghĩa ở đây phải sửa cả notebook.

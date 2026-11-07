# 1. Problem and Dataset

Milestone 1 collects paper metadata, reference metadata and the available LaTeX source of every version of the arXiv papers assigned to the group. Only `.tex` and `.bib` source files are retained {cite}`hcmus-statement`.

## 1.1. Assigned ID ranges

| Member | Inclusive assigned range | IDs |
| --- | --- | ---: |
| Cao Tiến Thiên | `2606.30734` → `2607.03693` | 5,000 |
| Trần Minh Tiến | `2606.25734` → `2606.30733` | 5,000 |
| Trương Lê Trung Hiếu | `2606.05734` → `2606.10733` | 5,000 |
| Lý Huỳnh Minh Đăng | `2604.20535` → `2604.25534` | 5,000 |

*Table 1.1. Inclusive arXiv ID ranges assigned to the four group members.*

The final benchmark must cover all 20,000 assigned IDs. Samples validate the pipeline but do not replace the full benchmark. Thiên's range crosses a month boundary: the ID generator uses the configured last June sequence (`2606.32040`) and restarts July at `00001`.

## 1.2. Snapshot scope

The filtered metadata snapshot contains **20,000 assigned papers and 26,491 recorded versions**: 14,913 papers have one version and 5,087 have multiple versions. These counts describe the expected scope according to the snapshot, not the number of papers or versions successfully crawled. Among its assigned records, the latest `update_date` is **23 October 2026**; the precise publication date of the Kaggle snapshot has not been verified. The filtered snapshot is identified by SHA-256 `033d7bded327d3aa1595f5502ebfc44bcfe353a89a2011b297742d287ba4de15`.

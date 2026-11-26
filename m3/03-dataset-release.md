# 3. Dataset release

<!-- Drafted with the help of OpenAI Codex, disclosed per course rules. -->

Each assigned range is distributed as a separate Hugging Face dataset with six Parquet tables.

| Stage | Tables |
| --- | --- |
| M1 | `papers`, `references` |
| M2 | `elements`, `hierarchy`, `bibtex` |
| M3 | `predictions` |

The prediction table records the citing paper, partition, citation key, ground-truth arXiv ID and up to five ranked candidates. Candidate fields are null when the ranker abstains.

## Datasets by range

- [Đăng](https://huggingface.co/datasets/PancakeDang/arxiv-nhom1-dang)
- [Hiếu](https://huggingface.co/datasets/HIULAPTOP/arxiv-nhom1-hieu)
- [Thiên](https://huggingface.co/datasets/ThienCao/arxiv-nhom1-thien)
- [Tiến](https://huggingface.co/datasets/tientrm/arxiv-nhom1-tien)

# arXiv Citation Pipeline — Group 1

Project report for the course Introduction to Data Science (University of Science, VNU-HCM). Every table and figure in this book is generated at build time from the CSV files in `data/`.

## Members

| Name | Student ID | GitHub | Role |
|---|---|---|---|
| Cao Tiến Thiên | 24127122 | [@CaoThien1402](https://github.com/CaoThien1402) | Data pipeline and crawler |
| Trần Minh Tiến | 24127130 | [@tien140406](https://github.com/tien140406) | Preprocessing, EDA and QA |
| Trương Lê Trung Hiếu | 24127169 | [@Hiulaptop](https://github.com/Hiulaptop) | Infrastructure, benchmark and book |
| Lý Huỳnh Minh Đăng | 24127272 | [@DankDaPancake](https://github.com/DankDaPancake) | Methodology, modeling and submission |

## Links

- **Code repository:** <https://github.com/hcmus-arxiv-nhom1/CodeRepo>
- **This book (Moodle submission link):** <https://hcmus-arxiv-nhom1.github.io/arxiv-book/>
- [Group crawl and benchmark notebook](m1/arxiv_nhom1_crawl_benchmark.ipynb): embedded source, pinned Colab launch and download

## Contents

- **Section 1 — Milestone 1: Data Crawling**
  - [Overview](m1/index.md)
  - [Crawling methodology](m1/01-methodology.md)
  - [Data statistics](m1/02-data-stats.ipynb)
  - [Performance](m1/03-performance.ipynb)
  - [Discussion](m1/04-discussion.md)
  - [Colab crawl and benchmark](m1/arxiv_nhom1_crawl_benchmark.ipynb)
- **Section 2 — Milestone 2: Hierarchical Parsing and Standardization**
  - [Overview](m2/index.md)

Last updated: 2026-10-30.

## Use of AI and external sources

Part of the group's code and text was drafted with the help of an AI assistant (Claude, Anthropic) {cite}`anthropic-claude`; the files concerned carry a note at the top. Data was collected through the arXiv API {cite}`arxiv-api` and the Semantic Scholar API {cite}`s2-api`. Each chapter lists its full references.

The unified Colab notebook, checkpoint orchestration and updated M1 documentation were drafted with assistance from OpenAI Codex; affected files disclose this assistance. Quantitative observations still require their recorded run evidence.

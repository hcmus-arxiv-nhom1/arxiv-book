# Milestone 2 — Hierarchical Parsing and Standardization

<!-- Drafted with the help of an AI assistant (Claude, Anthropic), disclosed per course rules. -->

Milestone 2 reads the corpus of Milestone 1 and turns every version of every publication into a hierarchy of sections, sentences, formulas and figures, with its references converted to BibTeX and the duplicates across versions merged. The result is three tables, `elements`, `hierarchy` and `bibtex`, written as Parquet shards; they are the input of Milestone 3 {cite}`hcmus-statement-m2`.

Chapters:

1. [Methodology](01-methodology.md): multi-file gathering, the hierarchy, sentence splitting, cleanup and math normalization, `\bibitem`/`.bib`/`.bbl` to BibTeX, deduplication, the tables, resumable runs.
2. [Parsing statistics](02-data-stats.ipynb): success rate, version coverage per publication, elements and references before and after deduplication.
3. [Performance](03-performance.ipynb): running time, memory and output size.
4. [Quality audit and limitations](04-quality.ipynb): integrity checks, agreement with the source, a reading of random papers, known limits.

```{important}
**What the numbers are.** The statistics, performance and audit pages are computed at build time from the CSV files in `data/m2/`. Until the full crawl has been parsed on Google Colab, those files hold the output of the real pipeline on the **100-paper M1 smoke crawl**, run on a local machine. They are a small subset and not the official benchmark; each page says so, and the files are replaced by the official export without changing the pages.
```

Code: [`src/parser/`](https://github.com/hcmus-arxiv-nhom1/CodeRepo/tree/main/src/parser) (stages and runner), [`src/qa/`](https://github.com/hcmus-arxiv-nhom1/CodeRepo/tree/main/src/qa) (checks and audits), [`src/benchmark/m2_benchmark.py`](https://github.com/hcmus-arxiv-nhom1/CodeRepo/blob/main/src/benchmark/m2_benchmark.py) (measurement).

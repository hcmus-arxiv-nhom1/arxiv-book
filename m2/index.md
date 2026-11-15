# Milestone 2 — Hierarchical Parsing and Standardization

<!-- Drafted with the help of an AI assistant (Claude, Anthropic), disclosed per course rules. -->

Milestone 2 reads the corpus of Milestone 1 and turns every version of every publication into a hierarchy of sections, sentences, formulas and figures, with its references converted to BibTeX and the duplicates across versions merged. The result is three tables, `elements`, `hierarchy` and `bibtex`, written as Parquet shards; they are the input of Milestone 3 {cite}`hcmus-statement-m2`.

Chapters:

1. [Methodology](01-methodology.md): multi-file gathering, the hierarchy, sentence splitting, cleanup and math normalization, `\bibitem`/`.bib`/`.bbl` to BibTeX, deduplication, the tables, resumable runs.
2. [Parsing statistics](02-data-stats.ipynb): success rate, version coverage per publication, elements and references before and after deduplication.
3. [Performance](03-performance.ipynb): running time, memory and output size.
4. [Quality audit and limitations](04-quality.ipynb): integrity checks, agreement with the source, a reading of random papers, known limits.

```{important}
**What the numbers are.** The statistics, performance and integrity numbers are computed at build time from the CSV and JSON files in `data/m2/`, which are the export of the official run `m2-full-01`: the **20,000 assigned publications and their 26,491 versions**, parsed on a Google Colab CPU runtime (see [Performance](03-performance.ipynb)). Two things are still a sample: the official output was compared with source for 2,407 versions of 1,079 publications in the multi-Thiên run (1,114 publications have source available); an earlier reading used 30 papers from a separate 100-publication sample, and the human score sheet is not filled yet. [Quality audit and limitations](04-quality.ipynb) says which is which.
```

Code: [`src/parser/`](https://github.com/hcmus-arxiv-nhom1/CodeRepo/tree/main/src/parser) (stages and runner), [`src/qa/`](https://github.com/hcmus-arxiv-nhom1/CodeRepo/tree/main/src/qa) (checks and audits), [`src/benchmark/m2_benchmark.py`](https://github.com/hcmus-arxiv-nhom1/CodeRepo/blob/main/src/benchmark/m2_benchmark.py) (measurement).

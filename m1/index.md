# Milestone 1 — Data Crawling

Milestone 1 collects the LaTeX sources (keeping only `.tex` and `.bib` files) of every version of every paper in the arXiv ID ranges assigned to the group, together with the paper metadata and the reference metadata from Semantic Scholar {cite}`hcmus-statement`.

Chapters:

1. [Methodology](01-methodology.md): how the crawler works, tools, politeness, output layout, definition of success.
2. [Data statistics](02-data-stats.ipynb): success rate, size before and after removing figures, references.
3. [Performance](03-performance.ipynb): running time, RAM and disk on Google Colab (CPU-only).
4. [Discussion](04-discussion.md): results, limitations, possible improvements.
5. [Group crawl and benchmark notebook](arxiv_nhom1_crawl_benchmark.ipynb): inspect the operational notebook, download it or open the pinned version in Colab. It is not executed during Book builds.

```{note}
The numbers currently come from **placeholder CSV files** (`scripts/make_fake_data.py`) so that the book builds. They will be replaced by the CSV files exported from the code repository once the crawl and the benchmark are done.

The final benchmark covers all 20,000 assigned IDs and their discovered versions on Colab CPU. Sample measurements validate the pipeline only. Source/reference QA, checkpoint provenance and complete timing evidence accompany the final CSVs.
```

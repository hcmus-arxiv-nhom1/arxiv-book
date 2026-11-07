# Milestone 1 — Data Crawling

Milestone 1 collects the LaTeX sources (keeping only `.tex` and `.bib` files) of every version of every paper in the arXiv ID ranges assigned to the group, together with the paper metadata and the reference metadata from Semantic Scholar {cite}`hcmus-statement`.

Chapters:

1. [Problem and Dataset](00-problem-dataset.md): objective, assigned ID ranges and snapshot scope.
2. [Methodology](01-methodology.md): how the crawler works, tools, politeness, output layout, definition of success.
3. [Data statistics](02-data-stats.ipynb): success rate, size before and after removing figures, references.
4. [Performance](03-performance.ipynb): running time, RAM and disk on Google Colab (CPU-only).
5. [Discussion](04-discussion.md): results, limitations, possible improvements.
6. [Attempts and effort](05-attempts-effort.ipynb): audited historical experiments, failed attempts and lessons; real sample evidence, separate from final statistics.
7. [Only-v1 crawl and benchmark notebook](arxiv_nhom1_only_v1_benchmark.ipynb) and [multi-version crawl and benchmark notebook](arxiv_nhom1_multi_version_benchmark.ipynb): view or open the pinned operational notebooks in Colab. Neither is executed during Book builds.

```{note}
The data-statistics and performance pages use the five-run evidence reconciled under `data/m1/final/`. Terminal coverage is not the same as usable TeX or complete reference metadata; the reports describe the remaining audit and measurement limits.

The final selection covers all 20,000 assigned IDs and their snapshot versions on Colab CPU. Historical sample measurements are separate. The reported session sampler excludes work outside its recorded interval, including previously prepared S3 bulk downloads.
```

<!-- Drafted with the help of an AI assistant (Claude, Anthropic), cited per the course rules. -->
# Data of the M2 chapter

Read by `m2/02-data-stats.ipynb`, `m2/03-performance.ipynb` and `m2/04-quality.ipynb`. The book reads only these CSV files, never the corpus.

**Provisional.** Until the full crawl is parsed on Colab, these files come from the **100-paper smoke crawl of M1** (`2606.25734`–`2606.25833`, 130 versions, CodeRepo commit of the M2 stages), parsed on a local Windows machine with 2 worker processes. They are real outputs of the real pipeline, but they are a small subset, they were not produced on Colab, and they say nothing about the full corpus. Replace every file in this folder with the export of the official run.

| File | Produced by |
| --- | --- |
| `m2_papers.csv`, `m2_versions.csv` | `src.parser.run` (`--work-dir`): one row per paper / per version |
| `m2_benchmark_summary.csv`, `m2_resource_timeseries.csv` | `python -m src.benchmark.m2_benchmark` |
| `structure_audit.csv` | `python -m src.qa.audit_structure`: counts in the source versus counts in the tree |
| `audit_findings.csv`, `sentence_flags.csv` | reading of 30 random papers (seed 2026) and an automatic scan of the sentences |

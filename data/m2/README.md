<!-- Drafted with the help of an AI assistant (Claude, Anthropic), cited per the course rules. -->
# Data of the M2 chapter

Read by `m2/02-data-stats.ipynb`, `m2/03-performance.ipynb` and `m2/04-quality.ipynb`. The book reads only these files, never the corpus.

## Official run `m2-full-01` (the whole corpus)

Export of the run on a Google Colab CPU runtime (2 vCPUs, 13.6 GB RAM): 20,000 publications, 26,491 versions, one session, 2 workers. The files come from `m2_evidence.zip` of the run, and the QA files from the separate QA run `qa-full-01`, both on the team Drive.

| File | What it is |
| --- | --- |
| `m2_papers.csv`, `m2_versions.csv` | one row per paper / per version (`src.parser.run`) |
| `m2_benchmark_summary.csv`, `m2_resource_timeseries.csv`, `m2_sessions.jsonl`, `environment.json`, `measurement_audit.json` | `python -m src.benchmark.m2_benchmark`: wall time, RAM, disk, the log of each session, the machine |
| `run_summary.json`, `assigned_check.json` | the parser's own summary of the run, and the check that the papers are exactly the 20,000 assigned IDs |
| `check_tables.json`, `qa_status.json` | the table integrity check of the QA run over the 200 committed shards (0 problems); `qa_status.json` records that the structural comparison and the manual review were skipped |

## Sample of 100 publications (not the official run)

These three files come from the first, local run on the 100-paper M1 smoke crawl (`2606.25734`–`2606.25833`, 121 versions) and are historical evidence from a previous revision. A later source comparison was performed separately on a subset of the official output, described below.

| File | What it is |
| --- | --- |
| `structure_audit.csv` | `python -m src.qa.audit_structure`: counts in the source versus counts in the tree |
| `audit_findings.csv`, `sentence_flags.csv` | a reading of 30 random papers (seed 2026) and an automatic scan of the sentences |

The manual score sheet (`src.qa.audit_sample`) is still to be filled by a team member.

## Official source subset `qa-thien-01`

The `structure_subset_*` CSV and JSON files are from [QA evidence on Drive](https://drive.google.com/drive/folders/1f6AsmOwSaq70vcgoRWUsbKZbfrfhI2Ye), using parser revision `fc0d00042e6d47378a6076383b6261a4aa5065f3` and QA revision `6c0f04bb5f9ae415d1604ba2989fc6222ab66745`. The subset comprises source run `multi-thien-0000-4999`, 1,114 papers and 2,407 parsed versions; 22,625 parsed versions were outside this source subset. Counts compare structures, not semantic correctness. The status records manual review pending. The official full-table QA files above remain unchanged.

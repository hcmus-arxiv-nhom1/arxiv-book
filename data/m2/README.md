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

These three files come from the first, local run on the 100-paper M1 smoke crawl (`2606.25734`–`2606.25833`, 121 versions) and were **not** recomputed on the official output: the structural comparison needs the source corpus, which the QA of the official run did not restore. The pages that show them say so.

| File | What it is |
| --- | --- |
| `structure_audit.csv` | `python -m src.qa.audit_structure`: counts in the source versus counts in the tree |
| `audit_findings.csv`, `sentence_flags.csv` | a reading of 30 random papers (seed 2026) and an automatic scan of the sentences |

The manual score sheet (`src.qa.audit_sample`) is still to be filled by a team member.

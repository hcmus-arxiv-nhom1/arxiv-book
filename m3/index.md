# Milestone 3 — Citation Matching

<!-- Drafted with the help of OpenAI Codex, disclosed per course rules. -->

Milestone 3 matches each standardized BibTeX citation from [Milestone 2](../m2/index.md) to candidate references collected in [Milestone 1](../m1/index.md). A classical ranker returns up to five arXiv IDs per citation and can abstain when no candidate meets the matching threshold.

The release includes the five M1/M2 tables for the 20,000 assigned papers and a `predictions` table covering the 2,020 papers in the frozen Train, Valid and Test split.

1. [Methodology](01-methodology.md) covers candidate construction, labels, features and model selection.
2. [Evaluation](02-evaluation.md) covers metrics, held-out results and error analysis.
3. [Dataset release](03-dataset-release.md) covers the package schema and links by assigned range.

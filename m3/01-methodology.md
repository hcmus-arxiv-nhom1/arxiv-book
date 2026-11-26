# 1. Methodology

<!-- Drafted with the help of OpenAI Codex, disclosed per course rules. -->

## Candidates and labels

For each citing paper, the candidate set contains its arXiv-keyed references from M1. The labels identify a matching candidate or record no match for each standardized BibTeX entry. The split is frozen at the citing-paper level. Train contains 2,004 papers. Valid and Test each contain four manually labeled and four automatically labeled papers.

## Feature engineering

The ranker uses normalized title similarity and directional title coverage, surname overlap, publication-year difference, explicit arXiv IDs, and missing-metadata indicators.

## Training and selection

The final logistic regression uses all feature groups with `C = 0.1` and equal total weight per citation. The no-match threshold was selected on Valid, then frozen before Test. The reference baseline ranks candidates by title similarity.

[Code and feature evidence](https://github.com/hcmus-arxiv-nhom1/CodeRepo#data-cleaning--feature-engineering)

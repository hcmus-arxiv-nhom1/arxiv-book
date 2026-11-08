# Parsing and standardization methodology

<!-- Drafted with the help of an AI assistant (Claude, Anthropic), disclosed per course rules. -->

Milestone 2 turns the M1 corpus (`.tex` and `.bib` of every version of every paper, plus the `.bbl` of the versions that have no other reference list) into three tables: `elements`, `hierarchy` and `bibtex` {cite}`hcmus-statement-m2`. Implementation lives in [CodeRepo](https://github.com/hcmus-arxiv-nhom1/CodeRepo) under `src/parser/`; the runner and its stage interfaces are specified in `specs/0005-m2-runner.md`.

## Pipeline

One command parses a whole corpus: `python -m src.parser.run --data-root data/corpus --out-dir data/m2 --work-dir work/m2`. For every paper and every version it runs, in this order:

1. **Gather** (`gather.py`): find the files that make up the compiled document.
2. **Normalize** (`normalize.py`): remove what has no meaning and give math one spelling.
3. **Build the tree** (`hierarchy.py`, with `sentences.py`): the hierarchy of the version.
4. **References** (`bibitem.py`): `\bibitem`, `.bib` and `.bbl` to BibTeX rows.
5. **Deduplicate** (`dedup.py`): one paper, all versions, to the rows of the three tables.
6. **Write** (`writer.py`): Parquet shards with the types of the statement.

A version that has no TeX is **recorded as empty, never skipped**: it appears in `hierarchy` as a root with nothing below it, and in the coverage statistics with its reason (`pdf-only`, `unavailable`, no `\documentclass`, parse error, or no folder at all).

## Multi-file gathering

The root of a version is the `.tex` file that contains `\documentclass`; `\input` and `\include` are followed transitively and everything else in the folder is ignored, because LaTeX would not compile it either. Text that LaTeX never typesets is removed first (`comment` environments, `\iffalse ... \fi` with its nesting), so a commented-out `\input` is not an include. When several files declare `\documentclass` (about 2.5 % of versions: main paper plus supplementary material, unedited templates), the root is the candidate that no other candidate includes, has `\begin{document}`, is not a `standalone` piece, has a `\title` matching the arXiv title, sits highest in the tree and reaches the most text, in that order; the other candidates are reported (`n_other_roots` in `m2_versions.csv`), as are includes that point to a missing file. The include depth is capped at 40 (TeX itself allows 15).

## Hierarchy

The document is the root. The level of a heading is **inferred**, not fixed: a heading is the child of the closest earlier heading of lower rank (`\chapter` < `\section` < `\subsection` < `\subsubsection` < `\paragraph`). A document without chapters therefore has its sections right under the root, and a `\subsection` before any `\section` hangs from the root.

| Kind of element | What it is | Children |
| --- | --- | --- |
| `document`, `chapter`, `section`, `subsection`, `subsubsection`, `paragraph` | A heading with its text as content (`\section*` included) | sentences, formulas, figures, lists, deeper headings |
| `itemize`, `item` | `itemize`, `enumerate` and `description`; each `\item` is a branch one level deeper | sentences, formulas, nested lists |
| `sentence` | One sentence of prose (leaf) | none |
| `equation` | One displayed formula (leaf) | none |
| `figure` | A float, **tables included** (leaf): the cleaned LaTeX of the environment, caption and `\includegraphics` kept | none |

The **References** section, `thebibliography` and `\bibliography` are left out. The abstract becomes a section "Abstract", an acknowledgements environment a section "Acknowledgements", and everything after `\appendix` is kept. Title blocks, `\newcommand` definitions, verbatim code and the commands of journal templates (`\affil`, `\preprint`, `\markboth`...) are dropped. Theorem-like environments (`theorem`, `proof`, `quote`...) are flattened into the text of the section that holds them. A footnote becomes sentences placed after the paragraph that cites it.

## Sentence splitting

A sentence ends at `.`, `?` or `!` followed by a space and the start of a new sentence (a capital letter, a command, a math span, an opening bracket or a quote). It does **not** end inside math (`$...$`, `\(...\)`), inside the argument of a command (`\cite{a.b}`, `\url{...}`), after an abbreviation (`e.g.`, `i.e.`, `et al.`, `Fig.`, `Eq.`, `Sec.`...), inside a URL, an e-mail address or a file name, in a decimal number, after an initial (`J. Smith`) or after a bare list number. A citation that follows the period stays with its sentence (`works.\cite{a}`).

## Cleanup and math normalization

- Comments are removed. Formatting commands without meaning are removed: `\centering`, placement options such as `[htbp]`, `\midrule`, `\vspace`, `\label`, `\noindent`, size switches. Text styling is unwrapped: `\textbf{x}` becomes `x`.
- **Inline math** is always `$...$` (from `\(...\)` and the `math` environment).
- **Block math** is always `\begin{equation} ... \end{equation}`: from `$$...$$`, `\[...\]`, `equation*` and `displaymath`; the multi-line `align`, `gather`, `multline` and `eqnarray` keep their lines inside an `aligned` or `gathered` block in the equation. `\label`, `\nonumber` and `\notag` are removed.

Normalizing twice changes nothing, so the same text always yields the same cleaned form, which is what the deduplication compares.

## References: `\bibitem`, `.bib` and `.bbl` to BibTeX

Entries come from three sources, in this order of preference: `\bibitem` lists in the `.tex`, the `.bib` files that the compilation path names (`\bibliography`, `\addbibresource`, `filecontents`), and the `.bbl`. Only the entries the text cites are kept, as BibTeX prints only those. A `\bibitem` is parsed with a style-aware heuristic (BibTeX `\newblock`, natbib labels, IEEE quotes, LNCS, Elsevier, ACM, revtex, AMS, hand-written lists): `citation_key`, `year`, `doi` and `url` are reliable, `authors`, `title`, `journal` and `entry_type` are heuristics, and authors are stored as "Given Family" strings.

**The `.bbl` fallback.** The M1 statement keeps only `.tex` and `.bib`, so a paper whose references exist only as a compiled `.bbl` would lose them. The lecturer's answer on the course Q&A sheet {cite}`hcmus-qa` is to turn the `.bbl` back into BibTeX and, if that fails, to keep the `.bbl`. The crawler therefore keeps a `.bbl` **only** when its version has no `.bib` and no `\bibitem` in its `.tex`; M2 reads a kept `.bbl` with the same `\bibitem` parser (`source = "bbl"`). Every other `.bbl` is still left out. Versions crawled before this rule have no `.bbl`: they keep an empty reference list, counted as a limitation in the statistics. This concerns the whole official corpus: its five crawl runs were made before the rule and are not re-downloaded (the group accepts the limitation for now). In the four multi-version runs, 1,061 of the 11,086 versions with TeX (9.6 %) had a `.bbl` dropped and no `.bib` kept, an upper bound for the versions without references; the only-v1 run could not be measured the same way.

## Deduplication across versions

**References.** Entries are matched by DOI, arXiv ID or normalized title, inside a version and across versions (`vaswani2017` in v1 and `vit_transformer` in v2 are one reference). The matched entries become one: the key used in the most versions is kept, the other keys are renamed in every `\cite{...}` of the text, and the fields are **united** (a field one version lacks is taken from another). Two different references that happen to share a key get distinct keys instead of being merged.

**Content.** An element whose cleaned text is equal shares one row of `elements` and one ID, whatever version it comes from; `hierarchy` has one row per version and parent, so a shared element can hang from different parents in different versions. Because citations are renamed before the text is compared, two sentences that differ only by the key of a citation are equal. Sentences, formulas and figures are matched by their kind and content. A section, list or item is matched by its kind, title, parent and rank among equal siblings, so that every element ID has exactly one parent and the tree of each version can be rebuilt from `hierarchy`. Two identical elements under the same parent in one version are stored as one edge.

IDs start with the publication key and end with a discriminant that is unique in the publication (`2310-12345#s7`): `s` sentence, `e` equation, `f` figure, `h` heading, `l` list, `i` item and `#rootN` for the document node of version N, whose parent is the publication key.

## Tables

| Table | Columns |
| --- | --- |
| `elements` | `element_id` (string, not null), `arxiv_id` (string, not null), `kind` (dictionary string), `content` (string) |
| `hierarchy` | `arxiv_id` (string, not null), `version` (int), `element_id` (string, not null), `parent_id` (string, not null) |
| `bibtex` | `arxiv_id` (string, not null), `citation_key` (string, not null), `entry_type` (dictionary string), `title`, `authors` (list of strings), `year` (int, nullable), `doi`, `journal`, `url` |

They are written as zstd-compressed Parquet shards (`shard-00000/`, ...). `python -m src.qa.check_tables` checks the types, the uniqueness of the IDs, that every parent exists, that each version has exactly one root and that every node is reachable from it, and that a branch has a single parent.

## Running a whole corpus: shards, resume, workers

Papers are written in shards (100 papers by default): a shard is built in `.staging/`, renamed to `shard-NNNNN/` (a directory rename is atomic, so the three files appear together), and only then recorded in the fsynced journal `shards.jsonl`. After an interruption the same command resumes: a half-written shard is deleted, committed papers are skipped, and at most one shard of work is lost. `--workers N` parses papers in N processes while the results are consumed in folder order, so the shards do not depend on N. `--scan` runs only gather and references, to see where the parser will have trouble before a long run. The statistics of the next chapter come from the files the runner writes as it goes (`m2_versions.csv`, `m2_papers.csv`), not from re-reading the corpus.

```{note}
Everything above is computed from the corpus of the M1 smoke crawl (100 papers) until the official crawl is complete; the next chapters say which data each number comes from.
```

# Historical effort evidence

These are real historical sample/partition summaries, separate from the placeholder final CSVs in the parent directory. They are not a controlled A/B benchmark.

Rebuild from the retained local debug bundles:

```sh
python scripts/collect_effort_evidence.py --evidence-root ../debug
```

`provenance.json` records relative input paths and SHA-256. No raw corpus or logs are committed. `attempts.csv` preserves measurement scopes, revisions, incomplete timing flags and assigned-ID denominators. The incomplete 1,000-ID run uses its observed session value, not a claim of complete end-to-end timing. Rescue duplicates are not counted as new runs. The HF quota traceback is an operator-provided observation described in the notebook, not an independently archived metric.

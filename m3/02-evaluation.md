# 2. Evaluation

<!-- Drafted with the help of OpenAI Codex, disclosed per course rules. -->

## Metrics

MRR@5 measures the reciprocal rank of the correct candidate within the first five results. The all-entry view assigns zero to entries with no labeled match. The matched-only view includes only entries with a labeled match. Precision, recall and F1 treat no-match as the positive class.

## Held-out results

The frozen ranker produced 85,350 prediction rows across Train, Valid and Test. The held-out evaluation covers 346 labeled citations.

| Test labels | Entries | MRR@5, all entries | MRR@5, matched only | No-match F1 |
| --- | ---: | ---: | ---: | ---: |
| Manual | 183 | 0.5027 | 0.9485 | 0.9659 |
| Auto | 163 | 0.5031 | 0.9880 | 0.9938 |

## Error analysis and limitations

The ranker abstained on six labeled matches and returned candidates for one manual entry labeled no-match. The held-out sets have four citing papers per label source. The automatic subset is evaluated against heuristic labels.

[Final run evidence](https://drive.google.com/file/d/1KS2cU3pRbvoqzBKCcCdAwMNV-OpLQQZL/view)

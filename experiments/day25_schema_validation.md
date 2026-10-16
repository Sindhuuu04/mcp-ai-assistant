# Day 25 — Schema Validation (pilot, synthetic, mock tools)

Environment: Python 3.12, mcp 1.30.0 (stdio), jsonschema Draft 2020-12. Date: 2026-10-16.
Reproduce: `python -m src.run_day25 && pytest -q` -> `results/raw/day25.jsonl`, `results/summary.csv`

## Pipeline order (decision)
authorize -> schema validate -> semantic check -> execute. Authorization first so unauthorized callers
get no schema feedback. (Source doc was inconsistent: sec 5.2 vs 8.1.)

## Results (12 cases x 2 arms)
| Check | Traditional | MCP |
|---|---|---|
| Cases behaving as expected | 12/12 | 12/12 |
| Invalid-argument rate (rejected pre-execution) | 6/12 | 6/12 |
| Forbidden executions (unauthorized/unknown tool/no-confirm) | 0 | 0 |
| Outputs identical for executed calls | yes | yes |

## Paper note: three separate outcomes
1. **Schema validity** — args match types/ranges/required/no extra fields (machine-checkable).
2. **Semantic correctness** — `project_id="nope"` is schema-valid but names no real project; caught only at
   execution (`external_service` category). `confirm=false` on delete is schema-valid but semantically refused.
3. **Execution success** — tool actually ran and returned a result.

## Caveats
- 12 hand-written cases is a functional check, not statistical evidence. No LLM is in the loop yet, so the
  "invalid-argument rate" here measures the validator on crafted inputs, NOT how often a model produces bad args.
  Next step: feed model-generated calls through the same gateway.
- Guard runs client-side for both arms for equivalence; a production MCP server should also validate (defense in depth).
- Latency numbers in the log are single runs, including cold start for MCP; do not compare yet (Day 28).

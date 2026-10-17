# MCP vs Traditional API Integration: Research Prototype

An enterprise AI assistant prototype built to answer one research question:

> How does **Model Context Protocol (MCP)** tool integration compare with **traditional direct API integration** in development effort, interoperability, latency, reliability, task success, and security?

The same tools, validation, and security policy are run through **two integration paths** (direct function adapter and MCP server/client), so any difference can be attributed to the integration boundary and nothing else.

---

## Status (through Day 25)

| Area | Status |
|---|---|
| Shared mock tools (2 read-only, 1 write-like) | Implemented, tested |
| JSON Schema argument validation (Day 25) | Implemented, tested |
| Local authorization policy, deny-by-default (Day 24) | Implemented, tested |
| Traditional arm (direct adapter) | Implemented, tested |
| MCP arm (stdio server + client) | Implemented, tested |
| Result logging (JSONL + CSV) | Implemented |
| RAG, embeddings, retrieval metrics (Days 16-20) | Planned |
| Conversation memory, query rewriting (Day 21) | Planned |
| Agent loop (Day 22) | Planned |
| Reliability: timeouts, retries (Day 23) | Planned |
| LLM in the loop, tool-selection experiments (Day 15, 26) | Planned |
| Effort, latency, interoperability measurement (Days 27-29) | Planned |

"Implemented, tested" means the code runs and passes the local test suite. The planned items are described in the research documentation but do not exist in this repository yet.

---

## Quick start

Requires Python 3.10+.

```bash
pip install -r requirements.txt
python -m src.run_day25      # run 12 cases through both arms
pytest -q                    # 14 tests
```

Expected output:

```
MCP tools discovered: ['get_project_status', 'get_experiment_results', 'delete_experiment']
traditional: 12/12 cases as expected | invalid-arg rate 6/12 | unauthorized/forbidden executions: 0
mcp:         12/12 cases as expected | invalid-arg rate 6/12 | unauthorized/forbidden executions: 0
```

Outputs are written to `results/raw/day25.jsonl` (one record per call) and `results/summary.csv`.

> **Version pin:** the project requires `mcp>=1.30,<2`. MCP SDK 2.x renamed `FastMCP` to `MCPServer` and breaks `src/mcp_arm/server.py`. Always record the SDK version in experiment notes.

---

## Architecture

```
            request (role, tool, args)
                      |
                      v
              +---------------+
              |  ToolGateway  |   identical for both arms
              +---------------+
              | 1. authorize  |  src/security/policy.py
              | 2. validate   |  src/core/schemas.py
              | 3. semantic   |  e.g. delete needs confirm=true
              | 4. execute    |---------------+
              | 5. log        |               |
              +---------------+               |
                                    +---------+----------+
                                    |                    |
                              Arm A: Direct         Arm B: MCP
                          src/traditional/        src/mcp_arm/
                          adapters.py             client.py -> server.py
                                    |                    |
                                    +---------+----------+
                                              v
                                   src/core/tools.py
                              (same business logic, both arms)
```

### Design decisions

- **Authorize first, then validate.** Unauthorized callers receive no schema feedback.
- **Authorization is independent of the LLM.** The model may propose a tool, but code decides whether it runs. Unknown tools and roles are denied.
- **Guard runs client-side for both arms** to keep the comparison equivalent. A production MCP server should also validate its own inputs (defense in depth).
- **Package is named `mcp_arm`, not `mcp`,** to avoid shadowing the official SDK.
- **Mock tools only.** `delete_experiment` records intent and mutates nothing real.

---

## Project structure

```
mcp-ai-assistant/
├── README.md
├── requirements.txt
├── src/
│   ├── core/
│   │   ├── tools.py          shared business functions + REGISTRY
│   │   ├── schemas.py        JSON Schemas + validate_args()
│   │   └── gateway.py        ToolGateway: authorize -> validate -> execute -> log
│   ├── security/
│   │   └── policy.py         TOOL_PERMISSIONS, ROLE_SCOPES, authorize()
│   ├── traditional/
│   │   └── adapters.py       DirectBackend (Arm A)
│   ├── mcp_arm/
│   │   ├── server.py         FastMCP server exposing the same tools (Arm B)
│   │   └── client.py         MCPBackend: stdio client wrapper
│   └── run_day25.py          runs all cases through both arms, writes results
├── tests/
│   └── test_day25.py         per-case tests, arm equivalence, no-execution-on-invalid
├── experiments/
│   └── day25_schema_validation.md
└── results/
    ├── raw/day25.jsonl
    └── summary.csv
```

---

## Tools and permissions

| Tool | Required scope | Notes |
|---|---|---|
| `get_project_status(project_id)` | `research:read` | read-only |
| `get_experiment_results(experiment_id, limit=10)` | `research:read` | `experiment_id` must match `exp-###`, `limit` 1-100 |
| `delete_experiment(experiment_id, confirm)` | `research:write` | mock; requires `confirm=true` |

| Role | Scopes |
|---|---|
| `researcher` | `research:read` |
| `admin` | `research:read`, `research:write` |

Identities here are **simulated**. This is not production authentication. Before connecting real services, implement a proper OAuth/token flow, secret storage, audience validation, and least-privilege scopes.

---

## Result record schema

Each call appends one JSON line to `results/raw/`:

```json
{
  "run_id": "uuid",
  "arm": "traditional | mcp",
  "task_id": "valid_status",
  "role": "researcher",
  "selected_tool": "get_project_status",
  "authorization": "allow | deny:<reason>",
  "arguments_valid": true,
  "executed": true,
  "validation_latency_ms": 0.12,
  "tool_latency_ms": 0.4,
  "end_to_end_latency_ms": 0.9,
  "failure_category": null,
  "error": null,
  "result": {}
}
```

Failure categories in use: `authorization`, `argument`, `external_service`.

---

## Experimental rules (keep the comparison fair)

- Change only the integration boundary. Keep the model, prompts, data, permissions, retry/timeout policy, and success criteria identical across arms.
- Record SDK versions, transport, runtime, hardware, and date.
- Run repeated trials; report distributions, not single numbers.
- Log failures; never discard them.
- Treat small pilot datasets as functional checks, not statistical evidence.
- Do not claim MCP caused an effect if anything else changed.
- Write the paper's abstract and conclusion only after results are measured.

### Known limitations of the current results

- 12 hand-written cases per arm is a functional check only.
- No LLM is in the loop yet, so the invalid-argument rate measures the validator on crafted inputs, not model behavior.
- Latency values are single runs and include MCP process cold start. Do not compare them until the Day 28 methodology is in place.

---

## Roadmap

| Day | Topic | Planned module |
|---|---|---|
| 15 | Tool-selection accuracy vs catalog size/ambiguity | `experiments/tool_selection/` |
| 16-17 | RAG: chunking, keyword and semantic retrieval | `src/rag/` |
| 18 | MCP Resources | `src/mcp_arm/` resources |
| 19 | Retrieval metrics (Precision@K, Recall@K, MRR) | `src/rag/evaluation.py` |
| 20 | Grounded generation and abstention | `src/rag/generator.py` |
| 21 | Conversation memory, query rewriting | `src/agent/memory.py` |
| 22 | Bounded multi-step agent | `src/agent/agent.py` |
| 23 | Timeouts, retries, failure injection | `src/agent/reliability.py` |
| 26 | Unified evaluation harness (LLM-driven) | `src/run_*.py` consolidation |
| 27-29 | Effort, latency, interoperability | `experiments/` |
| 30 | Pilot run and protocol/version freeze | `docs/` |

---

## Security and privacy guardrails

- Never commit API keys, tokens, passwords, or private data.
- Use synthetic data unless access and handling are explicitly approved.
- Validate every tool's input and authorize every invocation.
- Use bounded retries; avoid retrying non-idempotent operations.
- Require confirmation for write/delete operations.
- Treat retrieved documents and tool outputs as untrusted data that cannot override system or security instructions.

---

## Glossary

- **MCP**: protocol standardizing how AI applications connect to tools and data.
- **Tool**: an operation the agent can invoke. **Resource**: addressable data exposed to the model.
- **RAG**: retrieve relevant information, then give it to a model to generate an answer.
- **Authorization**: what an identity may do. **Authentication**: who the caller is.
- **Idempotency**: repeating an operation has the same effect as doing it once.
- **Schema validity**: arguments match the declared structure. **Semantic correctness**: arguments make sense for the task.
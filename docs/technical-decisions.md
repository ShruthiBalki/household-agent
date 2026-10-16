# Household Agent V1 — Technical Decisions (October 16, 2026)

## Selected V1 stack
Python 3.12+, FastAPI, Pydantic v2, pytest, and a model-provider SDK. Plain Python functions orchestrate the sequential pipeline. No LangChain, LangGraph, or database for V1. Minimal web UI follows the API.

## Pipeline
Input validation → Research Agent → Research schema validation → Decision Agent → Final validation → API response.

## Research
Manufacturer-first. General fallback only if manufacturer guidance does not clearly resolve the question. Conservative early stop; configurable query/source budgets. Collect claims and provenance without assessing credibility. Internal ephemeral diagnostic logs track searches, budget exhaustion, and retrieval failures. Do not show diagnostic metadata to users.

## Decision
Assess credibility, source independence, conflicts, and applicability. General guidance requires two credible independent sources. Return claim IDs, not duplicated evidence. API joins claim IDs to validated research claims for display. Uncertainty is plain text.

## Failure semantics
Invalid input: HTTP 422. Malformed research/decision output: controlled HTTP 502 (no retry). Research unavailable: controlled HTTP 503 when no meaningful evaluation is possible. Valid empty evidence: `Insufficient evidence`, not an error. A partial retrieval can still produce a valid decision if enough evidence exists.

## Additional deterministic invariants
- Claim IDs unique and nonempty; referenced claim IDs must exist.
- `Insufficient evidence`, `Condition dependent`, `Insufficient product information`, and `Unresolved evidence conflict` require a nonempty uncertainty explanation.
- Evidence shown to the user must be exactly the referenced claims, with source links.
- `Not yet` must not be inferred solely from failure to meet a replacement trigger.
- Schema validators cannot verify credibility or logical correctness; evaluate those with fixtures.

## Contract assumptions to revisit
The six outcome labels above are taken from the original evaluation terminology and prior conversation; confirm against the latest requirements before locking API compatibility. The research `failed` status and HTTP codes are implementation proposals. JSON Schema `format` must be actively enforced in validation.

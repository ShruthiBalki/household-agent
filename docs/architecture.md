# Household Agent — V1 Architecture (Draft)

**Date:** October 16, 2026  
**Status:** Draft for review; technology and operational decisions remain open.

## Goal
Provide an evidence-backed replacement recommendation for a household item. Only product name is required; purchase date, product link, and notes are optional. Accept generic product names. Never invent missing product facts or ask follow-up questions in V1.

## Sequential pipeline

```text
User input
  → Input validation (deterministic code)
  → Research Agent (AI)
  → Research schema validator (deterministic code)
  → Decision Agent (AI)
  → Final schema and consistency validator (deterministic code)
  → Recommendation
```

The pipeline is strictly sequential with no inter-agent feedback loops. Research may perform multiple searches within its stage. Both validators fail fast on invalid output, returning a controlled **system error**, not an evidence-based recommendation. No retries or regeneration in V1.

## Component responsibilities

### Input validation (code)
Validate nonempty product name and types/formats of optional date, link, and notes. Preserve all known facts and unknowns. Never infer material, coating, age, condition, or usage.

### Research Agent (AI)
Search manufacturer guidance first; if absent, vague, or not directly applicable, continue to credible general guidance. Retrieve only evidence that directly informs replacement, including relevant maintenance or safety criteria. Preserve the exact direction, conditions, scope, and limitations of each claim. Return structured JSON. Do not decide whether the item needs replacement.

### Research schema validator (code)
Check required fields, JSON types, evidence IDs, and structural constraints. It does not establish source credibility, URL accessibility, or factual truth.

### Decision Agent (AI)
Assess source credibility, applicability, independence, claim fidelity, conflicts, and sufficiency. A directly applicable manufacturer claim may resolve the decision alone. Actionable general-guidance recommendations require two credible independent sources with compatible applicable claims. One credible general source alone yields **Insufficient evidence** for an actionable recommendation. Preserve unresolved material conflicts and abstain. Do not infer the reverse of a conditional claim. No research callbacks.

### Final validator (code)
Check required recommendation fields, one allowed outcome, cited evidence IDs existing in the research result, and mechanically checkable rules. Source-count checks cannot prove genuine independence, credibility, or correctness of reasoning; these remain Decision Agent responsibilities. Fail fast if invalid.

## Draft data contracts (proposed, not yet finalized)

**Input:** `product_name` (required string); `purchase_date`, `product_link`, `notes` (optional). Missing values remain unknown.

**Research output:** `evidence[]` with unique `evidence_id`, `source_url`, `source_type` (manufacturer/general), `claim`, `conditions_or_limitations`, `product_applicability`; optional contextual summary. Research should also represent no findings or retrieval limitations explicitly. Exact JSON schema remains to be finalized.

**Decision output:** `outcome`, `reasoning`, `evidence_ids`, `source_basis`, `uncertainty`, and `next_action` where useful. Exact JSON schema remains to be finalized.

## Supported outcomes

- **Replace**
- **Not yet**
- **Condition dependent** — relevant replacement trigger exists but necessary condition is unknown
- **Insufficient evidence** — available evidence does not support a defensible recommendation
- **Unresolved evidence conflict / abstain** — credible material disagreement remains
- **Insufficient product information** — cannot identify product sufficiently for applicable guidance

Keep lifecycle/evidence path (explicit expiration, lifespan, condition-based, no reliable guidance) separate from outcome. An inaccessible source is an access limitation, not evidence that guidance does not exist. System/validation errors are separate from these six outcomes.

## Output principles
Lead with outcome, then rationale, manufacturer-versus-general evidence basis, traceable sources, specific uncertainty, and useful next action. Do not use numeric confidence scores in V1.

## Boundaries
No automatic retailer purchase retrieval, persistent user accounts, saved household history, reminders, component-level lifecycle tracking, or agent feedback loops. Do not invent infrastructure, scale, latency, uptime, or retention targets.

## Open decisions
1. Finalize research and decision JSON schemas, including empty evidence and retrieval-error representation.
2. Choose search/retrieval provider and AI model(s); verify manufacturer identity and source accessibility.
3. Decide orchestration, timeouts, provider failures, logging, and privacy/retention controls.
4. Select stack, hosting, UI, and repository structure.
5. Reconcile the existing evaluation suite with revised no-follow-up and optional-purchase-date requirements; test credibility, conflicts, claim fidelity, and validator fail-fast behavior.

## Document alignment
This draft reflects decisions agreed on October 16, 2026. The updated `decision-log.md`, `project-overview.md`, and `requirements.md` supersede the older September 17 copies for changed input and clarification behavior.

## Accepted contract refinements (October 16, 2026)

**Research Agent:** Collect evidence, not credibility judgments. Search manufacturer guidance first. Only fall back to general evidence if manufacturer guidance is missing or not clearly decisive for the supplied facts. A conservative early stop is permitted only for directly applicable manufacturer guidance that clearly resolves the decision. Respect configurable search-query and source limits; the numeric defaults are TBD. No `fallback_reason` field is required.

**ResearchResult contract (draft, field names not frozen):** `research_status` (completed/limited), `evidence` (array of `{claim_id, source_name, source_type, source_url, claim_text, applicable_product, conditions, summary?}`), and `retrieval_errors` (array). Each claim has a unique ID. The summary is optional. Empty evidence is valid. Source type is an observation, not a credibility verdict. Research may record budget exhaustion internally; it is not mandatory user-facing output.

**DecisionResult contract (draft, field names not frozen):** `outcome` (one of six supported outcomes), `reasoning` (text), `evidence_ids` (array of research claim IDs), `source_basis` (manufacturer/general/mixed/none), `uncertainty` (simple text, empty when none), `next_action` (optional text). The Decision Agent assesses credibility, independence, applicability, conflicts, and sufficiency; it does not duplicate full evidence objects.

**Rendering:** The application joins DecisionResult `evidence_ids` to ResearchResult claims and displays the selected claims and source links alongside the outcome and reasoning. Never display uncited claims as the decision's supporting evidence.

**Final validator:** Deterministically check the schema, allowed outcomes, claim-ID membership, and simple outcome-specific invariants (for example, `insufficient_evidence` requires a nonempty explanation of the limitation). Do not pretend code-based schema checks prove source credibility, semantic correctness, or genuine independence. Validation failure is a controlled system error; valid empty/weak evidence is handled by the Decision Agent as **Insufficient evidence**.

**Diagnostics:** Temporary development/test logs may record number of searches, budget exhaustion, and retrieval/access errors. User-facing text explains only meaningful evidence limitations. Do not commit to permanent storage.

**Testing:** Unit/fixture tests for research extraction, decision reasoning, input/schema validators, and final consistency rules; then integration/API and end-to-end regression tests. Include manufacturer early stop, conditional general fallback, one general source, no findings, budget exhaustion, missing claim ID, and uncertainty consistency.

**Delivery order:** Backend and API first; minimal web UI second. Python + FastAPI + Pydantic are proposed, not selected. Model/retrieval provider, hosting, and numeric research limits remain open.

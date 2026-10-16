# Household Agent — V1 Requirements

**Updated:** October 16, 2026

## 1. Purpose

This document defines what V1 must do and the quality constraints under which it must operate. Architecture and implementation mechanisms are intentionally excluded.

## 2. Functional Requirements

| ID | Requirement | V1 behavior |
|---|---|---|
| FR-01 | Accept minimal manual input | Require only product name; accept optional purchase date, product link, and notes. Generic names are valid input. |
| FR-02 | Preserve purchase-date semantics | Use original purchase date for age reasoning; do not treat it as first-use date without evidence. |
| FR-03 | Identify sufficiently, not perfectly | Determine product/category/material specificity sufficient for applicable guidance. Do not guess when ambiguity materially changes guidance. |
| FR-04 | Targeted iterative clarification | Do not ask follow-up questions in V1. If product identity cannot support applicable guidance, return **Insufficient product information**. |
| FR-05 | Ask for decision-relevant context | Do not request missing context in V1; preserve unknowns. Return **Condition dependent** when credible applicable guidance depends on an unknown condition. |
| FR-06 | Route lifecycle/evidence behavior | Support explicit-expiration, replacement/lifespan, condition-based, and no-reliable-guidance situations without conflating path with outcome. |
| FR-07 | Explicit-expiration handling | For products governed by a labeled expiration date, direct the user to that date rather than inventing a schedule from purchase age. |
| FR-08 | Manufacturer-first evidence | Prefer verified, explicit, applicable manufacturer guidance. If it directly resolves the decision, a second source is not required. |
| FR-09 | General-guidance fallback | If manufacturer guidance is absent or does not directly resolve the decision, search credible general guidance. |
| FR-10 | Two-source corroboration | A recommendation based on general guidance requires two credible independent sources supporting compatible, applicable claims. |
| FR-11 | Credibility assessment | Assess provenance, claim authority, evidence transparency, applicability, incentives, currency, corroboration, traceability, claim fidelity, and independence. |
| FR-12 | Weak-source handling | Weak/conflicted retailer, blog, or similar sources do not count toward corroboration merely because they repeat a claim. |
| FR-13 | Claim fidelity | Preserve each source's direction, conditions, and limits. Do not reverse implications, broaden claims, or convert conditional guidance into universal guidance. |
| FR-14 | Conflict handling | Attempt to reconcile credible conflicts through scope, definitions, applicability, or conditions. If unresolved, surface the conflict and abstain; do not majority-vote. |
| FR-15 | Evidence-to-recommendation mapping | Correctly map known user facts to evidence criteria; do not output a recommendation opposite to the evidence. |
| FR-16 | Outcome selection | Support **Replace**, **Not yet**, **Condition dependent**, **Insufficient evidence**, **Unresolved evidence conflict / abstain**, and **Insufficient product information** as distinct states. |
| FR-17 | Specific uncertainty | Tie uncertainty to the actual gap: identity, missing condition, weak evidence, unresolved conflict, access failure, or another concrete limitation. |
| FR-18 | Result structure | Lead with recommendation/guidance, then reasoning, evidence basis, sources, specific uncertainty, and a next action when useful. |
| FR-19 | Evidence labeling | Visibly distinguish manufacturer-specific guidance from general guidance and attribute sources. |
| FR-20 | Retrieval failure precision | Treat inability to open/retrieve a link as an access limitation, not proof that guidance does not exist. |
| FR-21 | Whole-item scope | Treat a multi-component product as one item in V1; component-specific schedules are out of scope. |
| FR-22 | Immediate result | Return the result without requiring saved history, persistent accounts, or reminders. |

| FR-23 | Research scope | Collect replacement-relevant evidence only; include maintenance or safety guidance only if it directly affects replacement criteria. |
| FR-24 | Research evidence contract | Return structured claims with source URL, source type, claim, conditions/limitations, and product applicability. |
| FR-25 | Sequential processing | Use deterministic input validation, Research Agent, research schema validation, Decision Agent, and final schema/consistency validation in order, without agent feedback loops. |
| FR-26 | Validation failures | Both deterministic validators fail fast and return controlled system errors, without automatic regeneration or retry. Keep system errors separate from evidence-based outcomes. |
| FR-27 | Reasoning ownership | Decision Agent evaluates source credibility, independence, applicability, conflicts, and sufficiency. Validators cannot certify semantic correctness. |

## 3. Credibility Criteria

A source assessment should consider:

- **Identity / provenance:** Who published it and can it be traced?
- **Claim authority:** Why is the source qualified for this claim?
- **Evidence transparency:** Is the basis of the claim explained or traceable?
- **Specificity / applicability:** Does it apply to this product/material/use case?
- **Incentives:** Are commercial or other incentives relevant?
- **Currency:** Is it recent enough for this claim?
- **Corroboration:** Does an independent credible source support a compatible conclusion?
- **Traceability:** Can the claim be traced to an original or authoritative source?
- **Claim fidelity:** Are direction, conditions, and limitations preserved?
- **Independence:** Are corroborating sources genuinely independent?

No simplistic numeric truth score should replace this assessment.

## 4. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | **Transparency:** Users can see evidence basis, source type, assumptions, and specific uncertainty. |
| NFR-02 | **Reproducibility:** Equivalent inputs and evidence should produce materially consistent outcomes. |
| NFR-03 | **Privacy boundary:** Core V1 does not require personal household accounts or persistent history; external-provider retention/privacy must be explicit during architecture. |
| NFR-04 | **Graceful failure:** Fail with a specific useful reason rather than fabricating an answer. |
| NFR-05 | **Conflict integrity:** Preserve and surface unresolved credible conflict. |
| NFR-06 | **Scope discipline:** Do not invent performance, scale, uptime, authentication, storage, or infrastructure targets without a demonstrated V1 need. |

## 5. Clarified Terminology

- **Lifecycle/evidence path** describes what kind of guidance governs the product; **recommendation outcome** describes what the system tells the user.
- **Insufficient product information** is an input/identification limitation.
- **Insufficient evidence** is a sourcing/evidence limitation.
- **Condition dependent** means the decision rule is known but a decision-relevant condition cannot be established without follow-up questions.
- **Abstention** is an intentional no-recommendation outcome when evidence cannot defensibly support a choice, especially under unresolved credible conflict.
- Usage frequency is optional context and is not requested in V1.

## 6. Accepted Behavioral Clarifications (October 16, 2026)

These refine existing requirements rather than mandate a programming language or model:

- **FR-23 — Evidence traceability:** Research evidence is represented as distinct claims with source links, relevant conditions, and stable IDs; the final displayed recommendation includes the claims cited by the decision.
- **FR-24 — Missing evidence:** A successful research operation yielding no defensible evidence produces **Insufficient evidence**, not a system error. Retrieval errors remain distinguishable from proof of no guidance.
- **FR-25 — Meaningful uncertainty:** A non-decisive result identifies the concrete unknown or evidentiary limitation in plain language.
- **FR-26 — Research boundedness:** Research must respect configurable query/source limits and may stop early only for clearly decisive, applicable manufacturer guidance. Exact limits are implementation configuration, not product requirements.
- **FR-27 — Contract integrity:** Malformed research/decision outputs or invalid claim references are treated as system validation errors, not replacement outcomes.
- **NFR-07 — Testable components:** Independent component fixtures and end-to-end regressions verify source attribution, decision reasoning, and mechanical contract validation.
- **NFR-08 — Minimal diagnostic retention:** Temporary testing diagnostics may include query counts, budget exhaustion, and retrieval errors; unnecessary long-term user-data retention is not part of V1.

# Household Agent — Decision Log

**Last updated:** October 16, 2026  
**Status:** Active — product definition and design

## Purpose

This living document records accepted product/design decisions, rationale, important superseded directions, and unresolved questions. Suggestions are not requirements until deliberately accepted.

## Product and Scope Decisions

### D-001 — Use “Household Agent” as a temporary project name
Working name only; final naming and whether “agent” is the right description remain open.

### D-002 — Start with a deliberately small V1
Validate one useful recommendation workflow before expanding into a broader household-management system.

### D-003 — Keep V1 retailer-agnostic
Retailers may supply product information but are not dependencies of the core recommendation workflow.

### D-004 — Automatic purchase retrieval is future scope
V1 does not automatically retrieve Amazon or other retailer purchase history.

## Development Process Decisions

### D-005 — Documentation-first AI-assisted development
Maintain project overview, requirements, evaluation plan, architecture, implementation plan, and decision records before substantial implementation.

### D-006 — Do not silently convert proposals into requirements
Unaccepted choices remain proposals/open questions.

### D-007 — Maintain the Decision Log as a durable source of truth
Working copies must incorporate accepted decisions before being treated as current.

### D-008 — Evaluate engineering choices through product and portfolio lenses
Demonstrate meaningful senior engineering/AI skills without adding unjustified complexity.

## V1 Input and Clarification Decisions

### D-009 — Minimal initial manual input
Only product name is required, including generic names such as “pan.” Purchase date, product link, and notes are optional. Do not invent unknown age, material, coating, or condition.

### D-010 — Product link is an identification aid
It is not the source of truth for replacement guidance.

### D-011 — Evaluate a product whenever it is added
No blanket purchase-age cutoff. Preserve original purchase date.

### D-012 — Usage frequency is not a mandatory initial input
It is optional context; V1 does not request additional details.

### D-013 — No follow-up questions in V1
Do not request additional product identity, material, condition, or usage information. Explain the consequential unknown in the outcome instead.

### D-014 — Stop rather than guess when product identity is insufficient
If the supplied product cannot be identified sufficiently for applicable guidance, return **Insufficient product information**; if credible guidance is conditional on an unknown condition, return **Condition dependent** and explain the trigger.

## Lifecycle and Evidence Decisions

### D-015 — Keep lifecycle/evidence path separate from recommendation outcome
Support explicit-expiration, replacement/lifespan, condition-based, and no-reliable-guidance situations without conflating them with the final result.

### D-016 — Explicit-expiration products use their labeled expiration
Do not invent a replacement interval from purchase age.

### D-017 — Prefer verified manufacturer guidance
Applicable exact-product/manufacturer guidance has priority.

### D-018 — Manufacturer guidance can resolve the decision alone
When explicit applicable manufacturer guidance directly answers the question, no second source is required.

### D-019 — Fall back to credible general guidance
If manufacturer guidance is absent or does not directly resolve the decision, continue research rather than assuming no guidance exists.

### D-020 — General-guidance recommendations require two credible independent sources
The sources must support compatible and applicable claims.

### D-021 — Weak sources do not become credible through repetition
Retailers, blogs, or conflicted sources that fail the credibility bar do not count merely because several repeat the same claim.

### D-022 — Preserve claim fidelity; no reverse inference
Do not reverse implications, broaden claims, or silently convert conditional guidance into universal guidance. “Replace if peeling” does not by itself establish “do not replace if not peeling.”

### D-023 — Reconcile credible conflicts; abstain if unresolved
Try to reconcile differences through scope, definitions, applicability, or conditions. If material conflict remains, surface it and abstain rather than majority-voting.

### D-024 — Correctly map evidence to known product facts
The recommendation must follow the actual evidence criterion. If a criterion requires “significantly worn,” mere unspecified “wear” is not silently upgraded to significant wear.

## Outcome and UX Decisions

### D-025 — Use distinct recommendation states
V1 supports **Replace**, **Not yet**, **Condition dependent**, **Insufficient evidence**, **Unresolved evidence conflict / abstain**, and **Insufficient product information**.

### D-026 — Tie uncertainty to the actual gap
Avoid generic confidence language when a concrete limitation can be named.

### D-027 — Lead with the decision, then evidence
Show recommendation/guidance first, followed by reasoning, evidence basis, sources, uncertainty, and useful next action.

### D-028 — Clearly label manufacturer vs general guidance
Source basis must be visible.

### D-029 — Skip numeric confidence scores in V1
Avoid false precision; describe the actual evidence gap.

### D-030 — Retrieval failure is an access limitation
Failure to retrieve/open a source is not evidence that the source or guidance does not exist.

## Scope / Architecture Decisions

### D-031 — Whole-item lifecycle only in V1
No component-specific replacement schedules.

### D-032 — Do not invent architecture requirements
Do not add performance, scale, uptime, authentication, storage, or infrastructure requirements without demonstrated need.

### D-033 — V1 non-functional priorities
Transparency, reproducibility, privacy boundaries, graceful failure, conflict integrity, and scope discipline.

## Evaluation Decisions

### D-034 — Maintain evaluation coverage before architecture
The evaluation suite defines expected behavior before implementation machinery is selected and later serves as regression coverage.

### D-035 — Run a cross-document traceability review before architecture
Every evaluation must map to requirements, and important behavioral requirements should have evaluation coverage.

## Superseded / Clarified Earlier Directions

- **Manufacturer-only guidance** → manufacturer-first plus credible general fallback.
- **General guidance should remain informational only** → actionable evidence-qualified recommendations.
- **Clarification only for product identity** → later expanded clarification → **no follow-up questions in V1**.
- **Usage frequency as a possible required input** → optional context; do not ask in V1.
- **Time-based-only framing** → includes condition-based evidence while preserving explicit-expiration routing.
- **Generic “insufficient evidence” for all failures** → distinct insufficient product information, insufficient evidence, condition dependent, and unresolved conflict outcomes.
- **Inferring “not yet” from absence of a manufacturer trigger** → prohibited by claim-fidelity / no-reverse-inference rule.

## Architecture Decisions — October 16, 2026

### D-036 — Two AI agents, sequential pipeline
V1 runs deterministic input validation → Research Agent → deterministic research schema validator → Decision Agent → deterministic final schema/consistency validator → output. No agent-to-agent feedback loops. Research may perform multiple searches internally.

### D-037 — Deterministic input stage
Validate and normalize user-provided fields without guessing unspecified product facts. This is code, not an AI agent.

### D-038 — Focused Research Agent
Retrieve only replacement-relevant claims. Include maintenance or safety information only when it directly establishes a replacement criterion. Search manufacturer guidance first, then credible general guidance when needed. Return structured evidence with source URL, source type, claim, conditions, limitations, and applicability.

### D-039 — Decision Agent owns semantic evaluation
Assess source credibility, independence, applicability, conflicts, evidence sufficiency, claim fidelity, and select one of six supported outcomes. A single credible general source is insufficient for an actionable general-guidance recommendation. Do not request further research from the Research Agent.

### D-040 — Deterministic validators
Research validator checks JSON schema, required fields, and types, not factual truth or source credibility. Final validator checks output schema, allowed states, evidence-ID references, and mechanically verifiable consistency; it does not independently judge reasoning quality.

### D-041 — Fail fast on validation failure
Both validators stop the pipeline and return a controlled system error. No regeneration, retries, or agent feedback loops in V1. Validation errors are distinct from evidence-based abstention.

## Open Questions for Architecture / Later Validation

- How lifecycle/evidence routing will be implemented and verified.
- How manufacturer sources and exact-product matches will be technically verified.
- How credibility criteria will be operationalized without a brittle numeric score.
- Which retrieval/search and model approach to use.
- What privacy/retention behavior external AI or search providers introduce.
- What observability/logging is needed for evaluation without unnecessary personal-data retention.
- Whether later validation needs a larger benchmark beyond the initial scenario suite.
- Final technology stack, repository structure, hosting, and UI.
- Final product name and whether “agent” remains the right product description.

## Contract, Research, and Delivery Decisions — October 16, 2026

### D-042 — Research gathers; Decision assesses
The Research Agent collects relevant manufacturer-first evidence and faithfully records claims, links, conditions, and applicability. It does not judge credibility or make replacement recommendations. The Decision Agent assesses credibility, independence, conflicts, sufficiency, and final outcome.

### D-043 — Conditional general fallback without a fallback-reason field
Research checks whether manufacturer guidance clearly addresses the question. If absent, unclear, or not decisively applicable to known input facts, research continues with general guidance. The V1 result need not include a `fallback_reason` field.

### D-044 — Structured claims and referenced decisions
Research emits an array of traceable claims with stable IDs and URLs; summaries are optional. Decision output references claim IDs rather than repeating all evidence. The application joins referenced claims and sources for the user-facing answer.

### D-045 — Simple uncertainty field
The Decision Agent provides uncertainty as a plain-language string rather than a nested taxonomy or numeric confidence score.

### D-046 — Deterministic final consistency validation
The final code validator checks schema, allowed outcomes, claim ID references, and simple outcome/uncertainty consistency. It cannot certify semantic credibility or reasoning correctness.

### D-047 — Research budget and conservative early stopping
Research has configurable limits on queries/sources (exact values TBD). Stop early only if directly applicable manufacturer guidance clearly resolves the question using known facts; otherwise search general guidance within the budget. Reaching the budget with weak/partial evidence is not a schema error.

### D-048 — Internal, privacy-conscious diagnostics
Record search count, budget exhaustion, and retrieval errors in temporary test logs, not as mandatory user-facing technical details. Explain meaningful evidence limitations in plain language. Long-term retention is not approved for V1.

### D-049 — Test components before full integration
Test Research Agent, Decision Agent, and deterministic validators independently using fixtures; then run end-to-end evaluation and regression tests.

### D-050 — Backend/API before minimal web UI
Implement and verify a simple backend/API first, then add a minimal web interface. Python, FastAPI, and Pydantic are suggestions, not selected technologies.

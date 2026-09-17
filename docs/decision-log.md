# Household Agent — Decision Log

**Last updated:** September 17, 2026  
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
Product name and purchase date are required; product link is optional.

### D-010 — Product link is an identification aid
It is not the source of truth for replacement guidance.

### D-011 — Evaluate a product whenever it is added
No blanket purchase-age cutoff. Preserve original purchase date.

### D-012 — Usage frequency is not a mandatory initial input
It may be requested when it materially affects the recommendation.

### D-013 — Clarification applies to any decision-relevant missing context
Targeted clarification is not limited to product identity. Ask simple user-observable questions about product type, material, condition, usage, or similar context when the missing information materially changes the decision.

### D-014 — Stop rather than guess when clarification remains insufficient
If product identity remains materially ambiguous, return **Insufficient product information**.

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
- **Clarification only for product identity** → clarification for any missing decision-relevant context.
- **Usage frequency as a possible required input** → not mandatory initially; ask only when materially relevant.
- **Time-based-only framing** → includes condition-based evidence while preserving explicit-expiration routing.
- **Generic “insufficient evidence” for all failures** → distinct insufficient product information, insufficient evidence, condition dependent, and unresolved conflict outcomes.
- **Inferring “not yet” from absence of a manufacturer trigger** → prohibited by claim-fidelity / no-reverse-inference rule.

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

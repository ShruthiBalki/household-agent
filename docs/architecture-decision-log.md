# Household Product Lifecycle Agent — Architecture Decision Log

**Date:** 2026-10-13  
**Status:** Living document  
**Scope:** High-level V1 architecture decisions (includes superseding LLD discussion updates)

| ID | Decision | Status | Rationale / Trade-off |
|---|---|---|---|
| AD-001 | Use a modular monolith for V1 rather than separate microservices. | Accepted | Deliver V1 with lower deployment and operational complexity while preserving future reusability through module boundaries. |
| AD-002 | [Superseded by AD-012] Define four logical modules: Input Processor, Recommendation Engine, Decision Engine, Output Engine. | Accepted | Separate parsing, evidence/guidance, actual decisions, and presentation. |
| AD-003 | Do not introduce a dedicated Orchestrator component for V1. | Accepted | The initial pipeline is linear. A thin application entry point/controller can invoke the modules in order. |
| AD-004 | Keep the Input Processor focused on extracting and normalizing known product details. | Accepted for V1 | Avoid a large upfront questionnaire. Do not assume unknown attributes. |
| AD-005 | [Superseded as a component by AD-013] Recommendation Engine handles ambiguous product categories and supplies conditional guidance. | Accepted for V1 | A user saying “pan” may want guidance for several pan types, not just one; avoid premature narrowing. |
| AD-006 | [Superseded as a component by AD-013] Decision Engine owns replace/retain/check-expiration/condition-dependent outcomes. | Accepted | A consistent decision can be reused across web, mobile, or voice channels without duplicating policy in presentation code. |
| AD-007 | Output Engine presents but does not make or change decisions. | Accepted | Keep business logic out of the presentation layer. |
| AD-008 | Prefer conditional answers over mandatory follow-up questions when details are missing. | Accepted for V1 | Reduce user friction and repeated engine calls; acknowledge that very broad answers can be less personalized. |
| AD-009 | Use manufacturer-specific guidance over generic guidance when applicable, while respecting the actual triggering conditions. | Accepted principle; details pending | Avoid overriding applicable instructions with generic age-based rules; conflict-resolution specifics need low-level design. |
| AD-010 | Keep V1 focused on product information, evidence research, lifecycle assessment and replacement recommendations; defer accounts, automation and component tracking. | Accepted | Constrain initial implementation scope. |
| AD-011 | Preserve evidence provenance and communicate uncertainty. | Accepted principle | A recommendation should be explainable and should not imply certainty unsupported by sources. |

## Important Discussion Outcomes

**Why not let the Output Engine decide?** That would mix decision policy with response formatting and risk inconsistent results across different client experiences. Under the original four-component proposal, the separate Decision Engine owned the outcome. **Current design:** decision policy is inside the Product Assessment Engine, never the Output Engine.

**Why not ask every question first?** The questions needed may depend on manufacturer guidance; a long initial questionnaire creates friction. The agreed V1 default is to proceed with available facts and provide condition-based alternatives.

**Why not use microservices immediately?** Independent reuse is a possible future need, not an immediate operational requirement. Clear internal contracts support later extraction without imposing network, deployment and distributed-failure complexity today.

## Deferred / Not Yet Decided

| ID | Topic | Status |
|---|---|---|
| OPEN-01 | Implementation language, frameworks and deployment | Open |
| OPEN-02 | Exact request, evidence and decision schemas | Open |
| OPEN-03 | Persistence / memory design and retention | Open |
| OPEN-04 | Manufacturer-source discovery, search providers and credibility scoring | Open |
| OPEN-05 | Detailed conflict-resolution and condition rules by product category | Open |
| OPEN-06 | Safety-sensitive cases and when clarification is unavoidable | Open |
| OPEN-07 | Timeouts, retries, caching, testing and monitoring | Open |

## Change Policy
Add a new entry when an architectural choice is made or revised. Preserve the original decision and document superseding decisions rather than silently rewriting history.

## Low-Level Design Discussion Updates — 2026-10-13

The entries below **supersede**, rather than erase, earlier decisions. The high-level architecture is now version 1.1.

| ID | Decision | Status | Rationale / Trade-off |
|---|---|---|---|
| AD-012 | Replace the four-module architecture with **three logical components**: Input Processor, Product Assessment Engine, Output Engine. Supersedes AD-002. | Accepted | A unified assessment has the decision context needed for better LLM-supported summaries without losing internal separation of retrieval and decision policy. |
| AD-013 | Merge the former Recommendation Engine and Decision Engine into one **Product Assessment Engine**, with internal retrieve → verify → summarize → validate → decide steps. Supersedes AD-005 and AD-006 as *component boundaries* (their evidence/decision responsibilities remain). | Accepted | Keep V1 simple and maintain clear internal logic, rather than two thin modules passing overlapping context. |
| AD-014 | Use a **simple form**, not free-text-only or raw JSON, for V1: required product name; optional purchase date; optional notes. Refines AD-004. | Accepted | Reduce parsing and user friction. Product name such as `pan` is valid; classification is downstream. |
| AD-015 | Input Processor validates and normalizes form fields only; no product classification or evidence research. | Accepted | Maintain a predictable boundary. |
| AD-016 | Product Assessment Engine may call an LLM provider (e.g., OpenAI or Anthropic), but must verify cited sources and their actual claims instead of trusting LLM-generated links or statements. | Accepted principle | Prevent hallucinated evidence; provider and implementation are open. |
| AD-017 | Research manufacturer guidance first; when verified and sufficient, stop. Otherwise seek credible general guidance. | Accepted | Prefer product-specific evidence without unnecessary searches. |
| AD-018 | If a manufacturer page is temporarily inaccessible, distinguish access failure from absent guidance; retry then fall back. | Accepted principle | Do not misrepresent retrieval failure. **Up to two retries** was discussed; precise policy is deferred. |
| AD-019 | For unspecified brands, synthesize relevant guidance from multiple manufacturers as **category-level** guidance, not as guidance verified for the user's product. Preserve distinct conditions and attribution. | Accepted | Avoid choosing an arbitrary manufacturer or falsely transferring brand-specific rules. |
| AD-020 | Validate each condition in an LLM summary against retrieved sources; remove unsupported conditions individually. | Accepted | Retain valid evidence without passing hallucinated conditions to decision logic. |
| AD-021 | Give the Product Assessment Engine the purchase date and notes, as well as product name, so its LLM-supported assessment is decision-aware. | Accepted | Better context and decision quality. |
| AD-022 | Assessment output contains **decision, reasoning, evidence**, plus relevant notes/uncertainty. | Accepted | Supports explainability and presentation across clients. |
| AD-023 | Unknown condition yields conditional guidance; credible unresolved conflicts yield abstention with reasons. | Accepted | No invented certainty. |
| AD-024 | Output Engine displays **decision → reasoning → evidence links**, and for insufficient information explains what is missing and what would help. Refines AD-007. | Accepted | Decision-first, evidence-transparent UX; output formatting does not make decisions. |

### Clarification on earlier decisions
- **AD-001, AD-003, AD-007 through AD-011 remain applicable**, subject to the refinements above.
- **AD-002 is superseded by AD-012**; **AD-005 and AD-006 are superseded as standalone component definitions by AD-013**. Their substantive duties now live inside Product Assessment Engine.
- The earlier **Household Agent product decision log** remains relevant, including independent credible general-source requirements, claim fidelity, conflict abstention, and the prohibition on inferring `Not yet` merely from absence of a replacement trigger. This architecture update does not silently overturn those product decisions.
- **OPEN-02, OPEN-04, OPEN-05 and OPEN-07** now also cover detailed schemas, LLM/source validation, exact applicability rules and retry settings.

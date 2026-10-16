# Household Agent

An AI-assisted application that researches replacement guidance for everyday household products and returns an evidence-backed recommendation—or clearly explains why a defensible recommendation is not possible.

> 🚧 **Status:** V1 design and implementation planning. Architecture and evaluation criteria are documented; implementation technology and model providers are not yet finalized.

## The Problem

Deciding whether to replace a pan, water bottle, or another reusable household item can require finding manufacturer instructions, interpreting condition-based guidance, comparing general sources, and accounting for missing or conflicting information. Household Agent aims to reduce that research and decision-making effort without inventing product facts or replacement schedules.

## V1 Experience

The user enters a **product name** (required). **Purchase date, product link, and notes** are optional. Generic names such as "pan" are accepted; the system does not guess unknown details or ask follow-up questions in V1.

The application returns one of six outcomes:

- **Replace**
- **Not yet**
- **Condition dependent**
- **Insufficient evidence**
- **Unresolved evidence conflict / abstain**
- **Insufficient product information**

The result leads with the outcome and explains the reasoning, the specific uncertainty (if any), and the evidence and source links used. An explicit product expiration date takes precedence over inventing an age-based schedule. Purchase date alone does not prove the item's condition.

## V1 Architecture

The design uses **two AI agents** separated by deterministic validation steps:

```text
User input
    ↓
Input validation (code)
    ↓
Research Agent (AI)
    ↓
Research schema validator (code)
    ↓
Decision Agent (AI)
    ↓
Final schema and consistency validator (code)
    ↓
User-facing result (outcome + cited evidence)
```

The pipeline is **strictly sequential**. There are no inter-agent feedback loops, user clarification turns, or automatic regeneration retries in V1. Invalid agent output causes a controlled system error, distinct from a valid **Insufficient evidence** recommendation.

### Research Agent

Collects replacement-relevant evidence, preserving each source's claim, URL, scope, conditions, and limitations. It searches **manufacturer guidance first**, then searches general guidance when manufacturer guidance is missing or not clearly decisive for the supplied facts. It does **not** assess source credibility or decide whether to replace the product.

Research is bounded by configurable search/source limits (numeric defaults to be decided). Conservative early stopping is allowed only when applicable manufacturer guidance clearly resolves the question. Temporary development logs can capture search counts, budget exhaustion, and retrieval failures without exposing operational details unnecessarily to users.

### Decision Agent

Evaluates credibility, applicability, source independence, conflicts, evidence sufficiency, and the fit between known product facts and source claims. A directly applicable manufacturer claim may be sufficient; an actionable recommendation based on general guidance requires **two credible independent sources** with compatible, applicable claims. The agent must not reverse conditional implications ("replace if peeling" does not establish "not yet" when peeling is absent).

The Decision Agent returns the outcome, reasoning, **claim IDs** identifying evidence it relied on, a source-basis label, a **simple text uncertainty field**, and an optional next action. The application joins those IDs to the Research Agent's full evidence records for user-facing citations; the Decision Agent does not duplicate entire evidence objects.

### Deterministic Validators

Validate JSON structure, required fields, allowed outcomes, claim-ID references, and mechanically checkable outcome-specific consistency rules. They **cannot** independently establish whether a source is truthful, credible, or genuinely independent. Valid research with no usable evidence results in **Insufficient evidence**, not a system error.

The exact JSON schemas are still drafts; see the architecture document for proposed fields and remaining contract decisions.

## Design Principles

- Evidence before certainty; never invent product characteristics, safety claims, or replacement intervals.
- Manufacturer-first research, with general guidance fallback when needed.
- Clear separation between **evidence collection** and **credibility/decision assessment**.
- Preserve the direction, conditions, and limitations of every source claim.
- Show supporting evidence and clearly distinguish manufacturer from general guidance.
- Express specific uncertainty rather than a numerical confidence score.
- Prefer a small, testable implementation over unnecessary agent-framework complexity.

## V1 Non-Goals

V1 excludes automatic retailer purchase-history retrieval, persistent user accounts or inventory, reminders, component-specific replacement schedules, interactive clarification, and multi-agent feedback loops. These may be reconsidered in a later version.

## Engineering and Testing Approach

We are following documentation-first, AI-assisted development: requirements and decisions precede implementation, and behavior is checked against explicit evaluation cases.

**Testing order:** test research extraction, decision reasoning, and both validators individually; then test API integration and the complete end-to-end workflow. Regression cases cover manufacturer evidence, general-source corroboration, missing information, conflicts, claim fidelity, empty results, search-budget exhaustion, and validation failures.

**Implementation order:** backend/API first, then a minimal web interface.

**Proposed (not finalized) stack:** Python, FastAPI, and Pydantic, using direct model-provider SDK calls and straightforward sequential orchestration. LangChain or LangGraph are **not required for V1**. LangChain may become useful for more complex retrieval integrations; LangGraph may be appropriate later if the workflow gains stateful branches, feedback loops, checkpoints, or human approvals. Model provider, search provider, hosting, and numerical research limits remain open decisions.

## Documentation

Detailed design records live in [`docs/`](docs/):

- [`project-overview.md`](docs/project-overview.md) — problem, goals, and scope
- [`requirements.md`](docs/requirements.md) — functional and non-functional requirements
- [`architecture.md`](docs/architecture.md) — pipeline, agent responsibilities, and draft contracts
- [`evaluation-plan.md`](docs/evaluation-plan.md) — acceptance and regression scenarios
- [`decision-log.md`](docs/decision-log.md) — accepted choices and superseded directions
- [`implementation-plan.md`](docs/implementation-plan.md) — phased delivery plan

## Current Phase

**Product definition → Requirements → Evaluation → Architecture → Implementation**

V1 is at the **architecture-to-implementation planning** transition. Next: finalize the ResearchResult and DecisionResult JSON contracts, confirm the backend stack, and implement/test the pipeline incrementally.

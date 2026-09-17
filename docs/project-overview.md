# Household Agent — Project Overview

**Last updated:** September 17, 2026  
**Status:** Product definition and design

## Overview

Household Agent is an AI-powered household-management application intended to reduce the mental effort involved in deciding when everyday household products should be replaced.

Useful replacement information may be fragmented across manufacturer guidance, credible general guidance, product age, product condition, usage, and other product-specific circumstances. Household Agent researches and reasons over that evidence and turns it into a clear, evidence-backed recommendation when the evidence supports one.

## V1 Goal

Validate one core workflow before investing in automatic purchase ingestion, persistent household inventory, reminders, or a broader household-management platform:

> Given basic information about a household product, can the application identify the decision-relevant context, find trustworthy evidence, and produce a useful and defensible replacement recommendation?

## V1 Inputs

Initial input is intentionally minimal:

- **Product name** — required
- **Purchase date** — required
- **Product link** — optional identification aid

The system may ask targeted follow-up questions about product type, material, coating, condition, usage, or similar context **only when that information materially changes the recommendation**.

If the product remains too ambiguous after simple user-observable clarification, the system stops rather than guessing.

Purchase date is evidence for age reasoning; it is not automatically first-use date and does not prove physical condition or safety.

## V1 Experience

For each product, the application should:

1. Identify the product/category/material with enough specificity for applicable guidance.
2. Ask targeted clarification when missing identity or context materially affects the decision.
3. Determine the appropriate lifecycle/evidence path.
4. Prefer verified, explicit, applicable manufacturer guidance.
5. If manufacturer guidance does not directly resolve the decision, search credible general guidance.
6. Require two credible independent sources for a recommendation based on general guidance.
7. Preserve source claims faithfully; do not reverse implications or broaden conditional claims.
8. Reconcile credible conflicts when possible; abstain if a material conflict remains unresolved.
9. Map known product facts correctly to evidence criteria.
10. Return a distinct, actionable outcome and explain its evidence basis and uncertainty.

## Lifecycle / Evidence Paths

V1 supports:

- **Explicit expiration:** use the labeled expiration date rather than inventing a schedule from purchase age.
- **Replacement/lifespan guidance:** reason from applicable manufacturer or corroborated general guidance.
- **Condition-based guidance:** reason from observable condition when evidence makes condition decision-relevant.
- **No reliable guidance:** explain why a defensible recommendation cannot be established.

Lifecycle/evidence path is separate from recommendation outcome.

## Recommendation Outcomes

V1 distinguishes:

- **Replace**
- **Not yet**
- **Condition dependent**
- **Insufficient evidence**
- **Unresolved evidence conflict / abstain**
- **Insufficient product information**

Uncertainty must be tied to the actual gap rather than expressed as a generic confidence disclaimer.

## Evidence Principles

- Manufacturer-specific guidance first when verified and directly applicable.
- A second source is not required when explicit manufacturer guidance directly resolves the decision.
- General-guidance recommendations require two credible independent sources with compatible applicable claims.
- Retailers, blogs, or conflicted sources do not count merely because several repeat the same claim.
- Preserve claim direction, conditions, scope, and limitations.
- Never infer the reverse of a source claim. For example, “replace if peeling” does not by itself mean “do not replace if not peeling.”
- Do not invent replacement intervals, safety claims, or false precision.
- Purchase age is not product condition.

## V1 Boundaries

### Included

- Manual product input
- Targeted iterative clarification
- Product/category/material identification sufficient for guidance
- Manufacturer-first research
- Credible general-guidance fallback
- Condition-aware reasoning when materially relevant
- Evidence conflict handling
- Evidence-qualified actionable outcomes
- Source attribution and uncertainty explanation
- Whole-item lifecycle treatment

### Not included

- Automatic retailer purchase-history retrieval
- Retailer-specific dependency
- Persistent user accounts
- Saved household history
- Ongoing reminders
- Component-specific lifecycle schedules
- Full household inventory platform
- Architecture complexity without a demonstrated requirement

## Design Principles

**Useful over complex.** Validate a meaningful workflow first.  
**Actionable over informational.** Research should reduce the user's decision burden.  
**Evidence before certainty.** Recommendations must be proportional to evidence.  
**Claim fidelity.** Never make a source say more than it says.  
**Transparent fallback.** Clearly distinguish manufacturer and general guidance.  
**Graceful abstention.** Stop with a specific reason rather than fabricate an answer.  
**AI should serve the product, not define it.** Architecture choices must be justified by requirements.

## Current Stage and Next Step

Requirements and the initial evaluation suite are now defined. The next step is a cross-document traceability review, followed by architecture and implementation planning.

## Related Documents

- `project-overview.md`
- `requirements.md`
- `evaluation-plan.md`
- `decision-log.md`
- `architecture.md` — next after traceability review
- `implementation-plan.md` — after architecture
- `AGENTS.md` — future concise entry point for AI-assisted development

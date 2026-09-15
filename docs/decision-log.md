# Household Agent --- Decision Log

**Last updated:** September 15, 2026\
**Status:** Active --- product definition and design

## Purpose of this log

This document records accepted product and design decisions for
Household Agent, including the context and rationale behind them. It is
intentionally maintained as a living engineering artifact. Important
superseded decisions are retained because understanding why the
direction changed is useful for future implementation and review.

Open questions remain explicitly open until they are deliberately
resolved. Suggestions and proposals are not treated as requirements
unless accepted.

## Project context

Household Agent originated from the recurring mental effort involved in
deciding when everyday household products should be replaced. For many
products, useful replacement information is fragmented across
manufacturer guidance, general lifecycle guidance, purchase timing, and
product-specific circumstances.

The project has two complementary objectives:

1.  Validate whether an application can materially reduce the research
    and decision-making effort involved in household product
    replacement.
2.  Serve as a disciplined senior-software-engineering and AI
    application project, demonstrating product reasoning, architecture,
    evidence-grounded AI behavior, evaluation, testing, implementation
    trade-offs, and responsible use of AI-assisted development.

The second objective should not introduce unnecessary complexity.
Technical choices should remain justified by product or engineering
needs; deliberately choosing a simpler design when appropriate is itself
an engineering decision.

The project is currently in product definition and design. No technology
stack or architecture has been selected.

------------------------------------------------------------------------

## 1. Product identity and scope

### D-001 --- Use "Household Agent" as a temporary project name

**Decision:** Use *Household Agent* as the working name.

**Rationale:** A name is useful for discussing and organizing the
project, but naming should not block product discovery.

**Boundary:** The final product name and whether the system is best
described as an "agent," "application," or something else remain open.

### D-002 --- Start with a deliberately small V1 and iterate

**Decision:** Validate one useful workflow before expanding into a
broader household-management system.

**Rationale:** The most important early uncertainty is whether the
recommendation workflow itself provides enough value to reduce a user's
research and decision-making effort. Building integrations, accounts,
reminders, and a larger platform before validating that would combine
too many unknowns.

### D-003 --- Keep V1 retailer-agnostic

**Decision:** Household Agent is not an Amazon-specific product. Product
information may originate from Amazon, Walmart, Best Buy, a
manufacturer, another retailer, or another source.

**Rationale:** The core product value is lifecycle research and
recommendation, not retailer-specific purchase retrieval.

**Consequence:** Future purchase ingestion can evolve independently from
the recommendation engine.

### D-004 --- Automatic purchase retrieval is a future ingestion capability

**Decision:** V1 will not automatically retrieve Amazon or other
retailer purchase history.

**Rationale:** Automatic retrieval could eventually reduce recurring
user effort, but it should not be developed before validating the
recommendation experience. A supported retailer-access method has not
yet been selected or verified.

**Boundary:** No retailer integration is promised for V1.

------------------------------------------------------------------------

## 2. Development and decision-making process

### D-005 --- Use a documented design process for AI-assisted development

**Decision:** Establish project context and requirements before
generating substantial implementation code. Maintain project overview,
requirements, evaluation planning, architecture, implementation
planning, and decision records as the project evolves.

**Rationale:** AI-assisted development should follow explicit product
and engineering context rather than allowing generated code to
implicitly define the design.

**Intended documentation sequence:** 1. Project overview 2. Requirements
3. Evaluation plan 4. Architecture 5. Implementation plan 6. A concise
`AGENTS.md` or equivalent entry point directing coding agents to the
source-of-truth documents

### D-006 --- Do not silently convert proposals into requirements

**Decision:** Material product and architecture choices that have not
been accepted remain proposals or open questions.

**Rationale:** Prevents implementation convenience, AI suggestions, or
assumptions from silently changing product behavior.

### D-007 --- Maintain the Decision Log as a durable source of truth

**Decision:** Preserve accepted choices, their context and rationale,
important superseded decisions, and unresolved questions as the project
progresses.

**Rationale:** Later requirements, architecture, implementation, and
interview discussions should be able to explain not only what was
chosen, but why.

**Operating rule:** When a working copy is updated, it must incorporate
all accepted project decisions made since the previous version before
being treated as the latest decision record.

### D-008 --- Evaluate engineering choices through both product and portfolio lenses

**Decision:** During architecture, coding, research, testing, and
evaluation, identify opportunities to demonstrate meaningful
senior-level software engineering and AI-system skills.

**Rationale:** The project is intended both to solve a real problem and
to demonstrate senior engineering capability in interviews.

**Boundary:** Do not add technologies, services, agents, infrastructure,
or architectural complexity solely because they appear impressive.
Choices must remain technically defensible.

------------------------------------------------------------------------

## 3. V1 input and evaluation behavior

### D-009 --- Use minimal manual product input in V1

**Decision:** V1 accepts: - Product name --- required - Purchase date
--- required - Product link --- optional

**Rationale:** This is sufficient to validate the core recommendation
workflow without first solving purchase-history ingestion.

**Evolution:** Early exploration considered uploads, invoices,
screenshots, and pasted structured text. The validation approach was
simplified to minimal product information; file uploads are not required
for the initial workflow.

**Boundary:** Purchase date is not automatically equivalent to first-use
date.

### D-010 --- Treat the product link as an identification aid, not the source of truth

**Decision:** A supplied link can help identify a product but does not
determine the replacement recommendation and is not tied to a particular
retailer.

**Rationale:** Product guidance should be researched and verified
independently where possible.

**Behavior:** If the exact product cannot be identified confidently,
communicate that uncertainty rather than guessing.

### D-011 --- Evaluate a product whenever it is added

**Decision:** Evaluate each submitted product regardless of how recently
or how long ago it was purchased.

**Rationale:** An older product may be precisely the item for which a
recommendation is most valuable.

**Consequences:** - Preserve the original purchase date for age
calculations. - Adding a product does not restart its age. - No blanket
one-month, one-year, or similar purchase-age cutoff applies.

### D-012 --- Usage frequency is not currently a required input

**Decision:** Usage frequency remains a proposal rather than a V1
requirement.

**Rationale:** Its usefulness and necessity have not yet been
established.

------------------------------------------------------------------------

## 4. Lifecycle routing and evidence

### D-013 --- Route products according to lifecycle behavior

**Decision:** V1 conceptually supports three lifecycle outcomes:

1.  **Expiration-based:** The product is governed by a labeled
    expiration date.
2.  **Replacement/lifespan-based:** Time-based manufacturer or credible
    general lifecycle guidance can support a recommendation.
3.  **No reliable time-based guidance:** Neither manufacturer nor
    credible general evidence supports a usable time-based estimate.

**Rationale:** Different products require fundamentally different
reasoning. A medicine with an explicit expiration date should not be
treated like a reusable household product.

**Boundary:** If lifecycle type cannot be determined reliably,
communicate uncertainty rather than guessing.

**Open implementation question:** How lifecycle routing is
determined---rules, metadata, manufacturer documentation, retrieval, an
LLM, or a combination---belongs to architecture and has not been
selected.

### D-014 --- Explicit-expiration products must use their labeled expiration

**Decision:** When a product is governed by an explicit expiration date,
do not calculate or invent a replacement interval from purchase age.
Direct the user to check the expiration date on the product or package.

**Rationale:** Purchase date is not a valid substitute for an explicit
product expiration.

**Validation note:** Children's Motrin was used as an edge/robustness
case for this route. This does not establish medicines as a core V1
category.

### D-015 --- Prefer verified manufacturer guidance

**Decision:** Manufacturer-specific lifecycle guidance is the preferred
evidence source when available and applicable.

**Rationale:** Exact-product manufacturer guidance is generally more
product-specific than broad lifecycle estimates.

### D-016 --- Continue to credible general guidance when manufacturer guidance lacks a usable interval

**Decision:** Absence of a manufacturer replacement interval is not
sufficient to conclude that no time-based guidance exists. Research
credible general guidance before reaching the no-guidance outcome.

**Rationale:** A manufacturer may provide care instructions without a
replacement schedule while useful broader lifecycle evidence still
exists.

**Validation lesson:** The training-underwear example exposed this
failure mode: lack of manufacturer replacement guidance did not mean
that no conditional general lifespan guidance could be found.

### D-017 --- Distinguish missing guidance from guidance without a time-based interval

**Decision:** "No guidance found" and "guidance exists but does not
specify a usable replacement interval" are different states.

**Rationale:** Conflating them can produce incorrect conclusions and
obscure why the application cannot establish a recommendation.

### D-018 --- Never invent a lifecycle interval

**Decision:** The application must not manufacture a lifespan or
replacement interval merely to produce an answer.

**Rationale:** An unsupported precise answer would undermine trust and
could falsely imply manufacturer, safety, or expiration authority.

### D-019 --- Explain why a reliable estimate cannot be established

**Decision:** If reliable time-based guidance cannot be established,
return the specific reason when known.

Possible reasons include: - no time-based guidance; - unresolved product
or material identity; - weak supporting evidence; - substantial
unresolved disagreement; - inaccessible relevant information.

**Important distinction:** An access or retrieval failure is a research
limitation, not evidence that guidance does not exist.

------------------------------------------------------------------------

## 5. Recommendation behavior

### D-020 --- Make an actionable recommendation when the evidence supports one

**Decision:** V1 should not merely present research and leave all
interpretation to the user. It should make an actionable replacement
recommendation while showing the evidence and reasoning behind it.

**Rationale:** The core problem is mental effort. If the application
simply reproduces research and requires the user to make the same
judgment, it has not solved enough of the problem.

### D-021 --- General guidance may support a recommendation, with explicit limitations

**Decision:** Credible general lifespan guidance may support a
recommendation such as "replacement recommended based on age" when
product age is meaningfully beyond the supported range.

**Required boundaries:** General guidance must not be represented as: -
a manufacturer requirement; - a medical expiration; - a universal
rule; - proof of the item's actual condition; - a safety
determination; - an exact or falsely precise replacement deadline.

The recommendation must explain its basis, assumptions, and uncertainty.

### D-022 --- Purchase age is evidence, not proof of condition

**Decision:** Product age may inform a lifecycle recommendation but does
not prove the item's actual physical condition or safety.

**Rationale:** Usage, care, material variation, damage, storage, and
other factors can affect real-world condition.

### D-023 --- Use evidence-appropriate recommendation outcomes

**Decision:** Intended recommendation framing is:

-   **Within supported guidance:** no replacement indicated by age.
-   **Near or around the supported range:** replacement may be worth
    considering; show evidence and uncertainty.
-   **Meaningfully beyond a supported range:** replacement recommended
    based on age/guidance; clearly label the basis.
-   **Explicit-expiration product:** check the labeled expiration date;
    do not calculate from purchase age.
-   **Insufficient evidence:** no reliable time-based recommendation
    available; explain why.

**Boundary:** These are recommendation categories, not claims that
purchase age proves physical condition or safety.

------------------------------------------------------------------------

## 6. Result presentation and retrieval behavior

### D-024 --- Lead with the takeaway

**Decision:** Present a short recommendation or takeaway first, followed
by supporting evidence.

**Supporting context should include, as applicable:** - product
identity; - age since purchase; - recommendation; - manufacturer
guidance; - credible general guidance; - sources; - assumptions and
uncertainty; - a specific explanation when a reliable estimate cannot be
established.

**Rationale:** The user should receive the decision-oriented answer
before needing to inspect the research details.

### D-025 --- Visibly separate manufacturer guidance from general guidance

**Decision:** Present manufacturer-specific and general guidance
distinctly rather than blending them.

Suggested conceptual labels: - **Manufacturer guidance** - **Found
online --- general guidance**

**Rationale:** Users should be able to understand the authority and
applicability of each piece of evidence.

**Additional boundaries:** - Attribute sources. - Show assumptions for
general ranges. - Distinguish search-excerpt-only findings from fully
reviewed sources. - Do not present generic seller suggestions as
exact-product instructions or universal schedules.

### D-026 --- Describe link retrieval failures precisely

**Decision:** If a supplied product link cannot be opened, describe the
retrieval failure rather than asserting that the listing does not exist.

Preferred behavior: "The app couldn't open this link."

**Rationale:** A failed retrieval does not prove that a listing is
missing, that a link is broken, or that a retailer intentionally blocked
access.

**Consequence:** Retain the user-supplied product identity while
distinguishing it from independently verified page details.

------------------------------------------------------------------------

## 7. Persistence and V1 non-goals

### D-027 --- V1 returns immediate results without saved product history

**Decision:** V1 accepts product information, performs the
research/recommendation workflow, and displays the result without
requiring persistent saved-item history.

**Rationale:** Persistence is not required to validate whether the core
recommendation is useful.

**Consequences:** - Users may re-enter products on later visits. -
Product-history management is deferred. - Persistent accounts are not
required for this workflow. - Ongoing reminders are deferred.

**Boundary:** This does not decide hosting-log, telemetry, AI-provider,
or search-provider retention behavior. Privacy and retention
requirements remain to be designed.

### D-028 --- Track the whole item in V1, not individual components

**Decision:** A multi-component product is treated as one tracked item.

**Example:** A reusable water bottle remains one item; its straw, lid,
gasket, and spout do not receive independent schedules in V1.

**Rationale:** Component lifecycle tracking would materially expand the
first version before the core workflow is validated.

### D-029 --- A complete household-management platform is outside V1

**Decision:** V1 does not attempt to provide comprehensive household
inventory, lifecycle management, reminders, accounts, retailer
synchronization, or component management.

**Rationale:** These may become useful only after the core
recommendation workflow demonstrates value.

------------------------------------------------------------------------

## 8. Initial qualitative validation set

### D-030 --- Stop the first discovery exercise at four deliberately varied products

**Decision:** Use four different product patterns for the initial
qualitative validation pass rather than attempting broad category
coverage.

**Rationale:** The purpose is to expose different lifecycle and evidence
patterns, not to establish a permanent supported-product catalog.

The cases are generalized for public documentation:

1.  **Ceramic cookware** --- durable reusable product; useful for
    testing manufacturer care guidance when a manufacturer replacement
    interval may be absent.
2.  **Children's training underwear** --- useful for testing the
    general-guidance fallback when manufacturer replacement guidance is
    unavailable.
3.  **Children's OTC medicine** --- explicit-expiration edge case used
    to test lifecycle routing.
4.  **Insulated stainless-steel children's water bottle** ---
    multi-component reusable product used to confirm whole-item V1
    scope.

**Boundary:** These examples expose requirements and failure modes; they
do not establish permanent category-specific replacement intervals.

### Validation observations retained

The exercise produced several durable lessons:

-   Manufacturer care guidance can exist without a manufacturer
    replacement interval; the workflow must still consider credible
    general guidance.
-   Absence of manufacturer replacement guidance does not automatically
    imply absence of useful general lifespan guidance.
-   Explicit-expiration products require a different lifecycle route.
-   Multi-component products remain whole items in V1.
-   Evidence hierarchy and recommendation framing materially affect
    whether the product reduces decision-making effort.

------------------------------------------------------------------------

## 9. Superseded decisions and why they changed

Superseded decisions are intentionally retained because they document
learning.

### S-001 --- Component-level tracking in V1

**Earlier direction:** Consider tracking replaceable components
independently.

**Superseded by:** D-028, whole-item tracking.

**Why:** Component tracking increased V1 scope without being necessary
to validate the core recommendation workflow.

### S-002 --- Manufacturer-only lifecycle guidance

**Earlier direction:** Restrict replacement guidance to
manufacturer-specific evidence.

**Superseded by:** D-015 and D-016, manufacturer-first with credible
general fallback.

**Why:** Real products may have useful lifecycle information even when
the manufacturer does not publish a time-based replacement interval.
Manufacturer-only behavior made the application unnecessarily unable to
help.

### S-003 --- General guidance should leave the replacement decision entirely to the user

**Earlier direction:** Display general lifespan guidance, source,
assumptions, and purchase age, but avoid turning it into an actionable
replacement recommendation.

**Reason for the earlier caution:** General lifespan estimates can vary
with usage, care, condition, and product variation. Avoiding a
recommendation reduced the risk of false precision.

**Superseded by:** D-020 through D-023.

**Why it changed:** The cautious behavior made the application too
passive and returned the central mental task to the user. The product
exists to reduce that decision-making burden. The revised approach
preserves the caution---source transparency, uncertainty, no invented
intervals, and no claim that age proves condition---while allowing the
system to make a useful recommendation.

### S-004 --- Default to inspection reminders

**Earlier direction:** Use inspection-oriented reminders when
replacement timing is uncertain.

**Superseded by:** Evidence-appropriate actionable recommendation
outcomes.

**Why:** Requiring users to remember to inspect items does not
sufficiently reduce the mental load the product is intended to address.

### S-005 --- Upload-oriented initial product input

**Earlier exploration:** Consider invoices, screenshots, or uploaded
purchase information as the starting input.

**Superseded by:** D-009, minimal manual input.

**Why:** Minimal product information is sufficient to test
recommendation quality without adding ingestion complexity.

------------------------------------------------------------------------

## 10. Open questions

The following are deliberately unresolved and must not be silently
decided during implementation:

1.  How should guidance measured from **first use** be handled when only
    purchase date is known?
2.  Is **usage frequency** valuable enough to become an input?
3.  How should lifecycle type be determined and verified?
4.  How should exact product identity and exact-product matches be
    established confidently?
5.  How should manufacturer sources be verified?
6.  What source-quality and evidence-strength model should be used?
7.  What precise result-screen UX should present recommendation,
    evidence strength, guidance, sources, and assumptions?
8.  What constitutes successful V1 validation beyond the initial
    qualitative four-product exercise?
9.  What privacy, retention, logging, telemetry, and deletion
    requirements should apply?
10. What privacy implications arise from external AI, retrieval, and
    search providers?
11. Which technology stack and development tooling should be used?
12. What repository and application structure should be used?
13. What retrieval/search approach should be used?
14. What model approach should be used?
15. What architecture should implement the recommendation workflow?
16. What supported method, if any, should provide automatic retailer
    purchase ingestion in a later version?
17. What should the final product be named, and is "agent" the right
    product description?

------------------------------------------------------------------------

## 11. Current V1 boundaries at a glance

**Included** - Manual product identification information - Original
purchase date - Optional retailer/manufacturer/product link - Product
identification with uncertainty handling - Lifecycle routing -
Manufacturer-first evidence research - Credible general-guidance
fallback - Actionable, evidence-qualified recommendation - Source and
uncertainty presentation - Explicit-expiration handling - Whole-item
lifecycle treatment

**Not included in V1** - Automatic retailer purchase-history retrieval -
Retailer-specific dependency - Persistent user accounts - Saved product
history - Ongoing replacement reminders - Component-level lifecycle
schedules - Full household inventory/management platform

------------------------------------------------------------------------

## 12. Decision-log maintenance rule

As requirements, evaluation, architecture, implementation, and testing
progress:

-   Add material accepted decisions with their rationale and boundaries.
-   Preserve meaningful minor decisions when they constrain behavior or
    explain implementation.
-   Preserve important superseded decisions and explain why they
    changed.
-   Keep proposals explicitly labeled as proposals.
-   Keep unresolved questions open until deliberately resolved.
-   Do not allow generated code or AI suggestions to silently become
    product requirements.
-   Keep public documentation free of personal information,
    machine-specific paths, private identifiers, and unnecessary
    purchase/account details.
-   For significant technical decisions, capture enough context to
    explain the trade-off in a senior-engineering interview.

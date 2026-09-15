# Household Agent --- Project Overview

**Last updated:** September 15, 2026\
**Status:** Product definition and design

## Overview

Household Agent is an AI-powered household-management application
intended to reduce the mental effort involved in deciding when everyday
products should be replaced.

For many household products, replacement timing is unclear. Useful
information may be fragmented across manufacturer documentation,
credible general lifecycle guidance, product age, and product-specific
circumstances. Users may need to find that information, judge its
quality, reconcile different forms of guidance, and decide whether an
item should be replaced.

Household Agent aims to perform that research and reasoning and turn it
into a clear, evidence-backed recommendation.

## Problem

Many everyday products do not have an obvious expiration date or
universally applicable replacement schedule.

Answering a seemingly simple question such as "Should this product be
replaced?" may require answering several others:

-   What exact product is this?
-   Does the manufacturer provide lifecycle or replacement guidance?
-   If the manufacturer does not provide a usable interval, is there
    credible general guidance?
-   How old is the product relative to the available guidance?
-   How strong and applicable is the evidence?
-   Is there enough evidence to make a recommendation at all?

This creates recurring research and decision-making work for households.
Household Agent is intended to reduce that mental load.

## Target User

The initial target user is a household decision-maker who wants help
determining when everyday products should be replaced without repeatedly
researching product lifespans and replacement guidance manually.

The product is retailer-agnostic. A product may have been purchased from
a major retailer, directly from a manufacturer, or through another
source.

## Version One Hypothesis

Version One is a validation release designed to answer one core
question:

**Given basic information about a household product and when it was
purchased, can an AI-powered application produce a useful, trustworthy
replacement recommendation that reduces the user's research and
decision-making effort?**

The initial workflow is intentionally manual so that recommendation
quality can be validated before investing in automatic purchase
ingestion or a broader household-management system.

## Version One Input

The user provides:

-   **Product name** --- required
-   **Purchase date** --- required
-   **Product link** --- optional

The product link is an identification aid, not the source of truth for
replacement guidance and not a dependency on any particular retailer.

If the exact product cannot be identified with sufficient confidence,
the application should communicate that uncertainty rather than guess.

Purchase age is useful evidence for lifecycle reasoning, but it is not
proof of a product's actual physical condition or safety. Purchase date
is also not automatically equivalent to first-use date.

## Version One Experience

For each submitted product, the application should:

1.  Identify the product as confidently as possible.
2.  Determine the appropriate lifecycle path.
3.  Prefer verified manufacturer guidance when available.
4.  Continue to credible general guidance when manufacturer guidance
    does not provide a usable time-based replacement interval.
5.  Consider the product's age based on the supplied purchase date.
6.  Produce an actionable replacement recommendation when the evidence
    supports one.
7.  Explain the evidence, source basis, assumptions, and uncertainty
    behind the recommendation.
8.  Explain specifically when reliable time-based guidance cannot be
    established.

The application should distinguish manufacturer-specific guidance from
general guidance and should never invent an interval or present
uncertain evidence as a definitive safety claim.

## Lifecycle Concept

Products may require different forms of lifecycle reasoning. At a high
level, Version One supports three conceptual paths.

### Expiration-based

Some products are governed by an explicit labeled expiration date.

For these products, the application should direct the user to the
labeled expiration date on the product or packaging rather than
inventing a replacement schedule from purchase age.

### Replacement/lifespan-based

For products without an explicit expiration date, the application should
look for verified manufacturer-specific replacement or lifespan guidance
first.

When manufacturer guidance does not provide a usable time-based
interval, credible general lifecycle guidance may be used. General
guidance can support an actionable age-based recommendation, but the
application must clearly identify that the recommendation is based on
general rather than manufacturer-specific evidence.

### Insufficient time-based evidence

For some products, reliable time-based guidance may not be available or
the product may not be identifiable with enough confidence.

The application should communicate the limitation and its reason rather
than inventing an interval or presenting unsupported certainty.

The technical mechanism used to perform lifecycle routing, product
identification, retrieval, evidence evaluation, and recommendation
generation will be determined during requirements and architecture work
rather than assumed in this overview.

## Recommendation Philosophy

Household Agent is intended to make useful recommendations, not merely
return research results.

When the available evidence supports it, the application may indicate
that:

-   replacement is not indicated by age;
-   replacement may be worth considering; or
-   replacement is recommended based on age and available guidance.

Recommendations must remain proportional to the evidence.

General lifecycle guidance must not be presented as:

-   a manufacturer requirement;
-   an exact expiration date;
-   a safety determination;
-   proof of the item's actual physical condition; or
-   a falsely precise replacement deadline.

If reliable evidence does not support a time-based recommendation, the
application should say so and explain why.

## Result Experience

The result should lead with a short, decision-oriented takeaway and then
provide supporting context as applicable:

-   product identity;
-   age since purchase;
-   recommendation;
-   manufacturer guidance;
-   credible general guidance;
-   sources;
-   assumptions and uncertainty; and
-   an explanation when a reliable recommendation cannot be established.

Manufacturer-specific guidance and general guidance should remain
visibly distinct so the user can understand the basis and authority of
the recommendation.

## Version One Scope

Version One includes:

-   manual product entry;
-   retailer-agnostic product handling;
-   product-identification attempts using supplied information;
-   explicit handling of uncertain product identity;
-   lifecycle routing;
-   manufacturer-guidance research;
-   credible general-guidance fallback;
-   age-based reasoning using the original purchase date;
-   actionable, evidence-qualified replacement recommendations;
-   evidence and source presentation;
-   explicit handling of expiration-based products;
-   transparent handling of missing or uncertain guidance; and
-   whole-item lifecycle evaluation rather than component-level
    schedules.

Version One is intentionally small so that the core recommendation
workflow can be validated before investing in broader automation.

## Initial Validation Approach

Early product discovery uses a small set of deliberately varied
household product types to exercise different lifecycle and evidence
patterns. These include durable reusable products, products where
general lifecycle guidance may be more useful than manufacturer
replacement guidance, an explicit-expiration edge case, and a
multi-component reusable product.

These examples are validation cases rather than a permanent
supported-category list. Their purpose is to expose requirements,
uncertainty, evidence-quality issues, and failure modes before
implementation expands.

## Version One Non-Goals

Version One does **not** currently include:

-   automatic retailer order-history retrieval;
-   retailer-specific dependencies in the core recommendation workflow;
-   persistent household inventory;
-   user accounts;
-   saved product history;
-   ongoing replacement reminders;
-   component-level replacement schedules; or
-   a complete household-management platform.

These exclusions keep the initial validation focused. They do not imply
that the capabilities are permanently out of scope.

## Longer-Term Vision

If the core recommendation workflow proves useful, Household Agent can
evolve toward a more automated household lifecycle-management system.

Future versions could supplement or replace manual entry with purchase
information from supported retailers, manufacturers, receipts, email, or
other purchase records. The method used to acquire product information
should remain conceptually separate from the core recommendation
workflow.

Over time, the system could identify products automatically, evaluate
their expected lifecycle, maintain a household inventory, and surface
products that may need attention or replacement.

The intended longer-term experience is to minimize recurring manual
research and product entry while preserving transparent, evidence-based
recommendations.

## Design Principles

**Useful over complex.**\
Validate a meaningful workflow before expanding the system.

**Actionable over informational.**\
Research should ultimately help the user make a decision rather than
simply reproduce information.

**Evidence before certainty.**\
Recommendations should reflect the strength and applicability of the
available evidence.

**Manufacturer guidance first.**\
Verified exact-product and manufacturer information should take
precedence over generic lifecycle guidance when available.

**Transparent fallback.**\
When credible general guidance is used, the application should make that
basis clear.

**No invented precision.**\
The application should communicate uncertainty rather than manufacture
unsupported replacement intervals.

**Purchase age is not product condition.**\
Age can inform a recommendation but does not prove actual condition or
safety.

**Retailer-independent core.**\
Retailers are potential sources of product information, not dependencies
of the recommendation workflow.

**Extensible without premature complexity.**\
Version One should remain simple while avoiding design choices that
unnecessarily prevent future ingestion or product evolution.

**AI should serve the product, not define it.**\
AI-powered capabilities should be used where they improve research,
reasoning, evidence handling, or user value. Technical mechanisms should
be selected deliberately during architecture rather than added solely
because AI is available.

## Current Project Stage

The project is currently in **product definition and design**.

The core workflow has been explored using varied product scenarios
representing different lifecycle situations. No production application,
retailer integration, persistent product database, final technology
stack, or final technical architecture has been selected yet.

The development approach is documentation-first and intended to support
disciplined AI-assisted engineering. Product decisions and requirements
will guide evaluation, architecture, implementation planning, coding,
and testing rather than allowing generated code to implicitly determine
product behavior.

The next stages are to define Version One requirements and evaluation
criteria, followed by architecture and implementation planning.

## Related Project Documents

-   `decision-log.md` --- accepted decisions, rationale, superseded
    decisions, and open questions
-   `requirements.md` --- next
-   `evaluation-plan.md` --- planned
-   `architecture.md` --- planned after requirements and evaluation
    criteria are sufficiently clear
-   `implementation-plan.md` --- planned after architecture
-   `AGENTS.md` --- planned as a concise guide directing AI-assisted
    development to the project's source-of-truth documentation

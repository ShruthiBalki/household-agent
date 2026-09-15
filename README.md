# Household Agent

An AI-assisted product lifecycle application that researches evidence-backed guidance and recommends when everyday household products should be replaced.

> 🚧 **Status:** Early development — currently in product definition and system design.

## The Problem

Everyday household products often don't have obvious replacement schedules.

Knowing whether a pan, water bottle, clothing item, or other reusable product should be replaced can require users to:

- remember when it was purchased,
- find manufacturer guidance,
- search for general lifespan recommendations,
- evaluate conflicting or incomplete information,
- and decide whether that guidance applies to their product.

Household Agent explores whether AI can reduce this research and decision-making effort.

## V1

The first version intentionally focuses on validating the core recommendation workflow before adding automation.

A user provides:

- **Product name**
- **Purchase date**
- **Product link (optional)**

The system will identify the product, research available lifecycle guidance, and provide a replacement recommendation together with the evidence and assumptions behind it.

When exact product guidance is unavailable, the system may use credible general guidance while clearly distinguishing it from manufacturer-specific information.

If a product normally has an explicit expiration date, the application will direct the user to that expiration information rather than attempting to invent a replacement interval.

## Design Principles

- Evidence-backed recommendations
- Manufacturer guidance preferred when available
- Clear distinction between product-specific and general guidance
- Explicit handling of uncertainty and missing information
- No invented replacement intervals
- Retailer-agnostic product identification
- Actionable results rather than simply presenting research

## V1 Non-Goals

The initial version does **not** include:

- Automatic Amazon, Walmart, or other retailer purchase retrieval
- User accounts
- Persistent household inventory
- Ongoing replacement reminders
- Component-level lifecycle tracking

These capabilities may be explored after validating the core recommendation experience.

## Engineering Approach

This project is also an exploration of disciplined **AI-assisted software development**.

Rather than beginning with AI-generated implementation, the project is being developed through explicit product definition, requirements, architectural decisions, evaluation criteria, implementation planning, and testing.

Key engineering decisions and their rationale are documented as the system evolves.

## Documentation

Detailed project documentation lives in [`docs/`](docs/).

- [`project-overview.md`](docs/project-overview.md) — problem, goals, scope, and product direction
- [`decision-log.md`](docs/decision-log.md) — significant product and engineering decisions with their rationale

Additional requirements, architecture, evaluation, and implementation documentation will be added as the project progresses.

## Current Phase

**Product definition → Requirements → Evaluation → Architecture → Implementation**

The project is currently moving from product definition into requirements.

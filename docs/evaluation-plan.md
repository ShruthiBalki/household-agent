# Household Agent — V1 Evaluation Plan

**Updated:** October 16, 2026  
**Status:** Updated for accepted sequential-pipeline design

## 1. Objective

Verify the V1 requirements and agreed architecture using controlled, repeatable tests. Evaluate recommendation correctness independently from JSON/schema correctness and retrieval quality. The system accepts generic names, requires only a product name, asks no follow-up questions, and runs a strictly sequential pipeline with two AI agents and deterministic validators.

## 2. Evaluation Method

- Use deterministic fixtures: user input, controlled search results/source contents, source identity and independence metadata, expected research claims, and expected recommendation or error. Examples of manufacturer statements below are **fixture assumptions**, not assertions about actual manufacturer policy.
- Run **component tests** for input validation, research output, research schema validator, decision agent, and final validator; then **end-to-end tests** for ordering and user-facing results.
- Assert outcome, evidence sufficiency, source applicability/independence, claim fidelity, conflict handling, uncertainty, source presentation, no clarification, and fail-fast behavior.
- Test expected decisions against frozen evidence, not live search. Run separate retrieval integration checks with actual providers; distinguish an inaccessible URL from absence of guidance.
- An unsupported recommendation fails even if retrieval and schemas are correct. A valid JSON payload is not proof of factual correctness.
- For every fixture, capture expected outcome, supporting evidence IDs, forbidden conclusions, and exact failure stage where applicable. Retain fixtures as regression tests.

## 3. Behavioral Evaluation Cases

### EV-01 — Explicit manufacturer guidance: happy path
**Scenario:** GreenPan ceramic nonstick pan; purchased June 2021; used several times/week; coating visibly peeling. Fixture contains verified, applicable manufacturer guidance saying replace when peeling.
**PASS:** **Replace**; cite applicable manufacturer claim; no second source needed; no invented uncertainty.
**Coverage:** FR-08, FR-15, FR-18, FR-19, FR-27.

### EV-02 — Unresolved credible-source conflict
**Scenario:** Ceramic nonstick pan; purchased 2021; regular use; no major damage; no manufacturer guidance. Two independent credible general sources irreconcilably disagree: age-based 3–5 years versus condition-only replacement.
**PASS:** **Unresolved evidence conflict / abstain**; accurately surface both positions; do not choose, blend, or majority-vote.
**Coverage:** FR-10, FR-14, FR-16, FR-17, FR-27.

### EV-03 — Condition-dependent result without clarification
**Scenario:** Ceramic nonstick pan; purchased 2022; condition unspecified. Two credible independent general sources agree replacement depends on significant scratching/peeling.
**PASS:** **Condition dependent** immediately; name the unverified trigger and provide supported conditional guidance; ask no question and do not infer current damage.
**Coverage:** FR-05, FR-10, FR-16, FR-17.

### EV-04 — Insufficient evidence
**Scenario:** Identifiable reusable silicone food-storage pouch; purchased 2021; undamaged. No manufacturer replacement guidance; general sources fail credibility requirements.
**PASS:** **Insufficient evidence**; explain why reliable guidance was not established; do not upgrade weak sources.
**Coverage:** FR-09, FR-11, FR-12, FR-16, FR-17.

### EV-05 — Generic product name, no follow-up
**Scenario:** User submits only `pan`; material, brand, coating, purchase date, and condition are absent. Fixture includes distinguishable guidance for different pan types, but no applicable universal replacement trigger.
**PASS:** Accept input; research at the supported generic scope; do not invent a type or ask a follow-up; return **Insufficient product information** if no applicable guidance can be established, explaining the specificity gap. A different fixture with applicable generic guidance may instead support a conditional recommendation.
**Coverage:** FR-01, FR-03, FR-04, FR-05, FR-16, FR-17.

### EV-06 — General guidance succeeds
**Scenario:** Ceramic nonstick pan; purchased 2020; coating **significantly worn**. No manufacturer guidance. Two credible independent general sources agree to replace when significantly worn.
**PASS:** **Replace**; match known condition to criterion; cite both independent sources; label basis as general.
**Coverage:** FR-09, FR-10, FR-15, FR-18, FR-19.

### EV-07 — Claim fidelity / no reverse inference
**Scenario:** Ceramic nonstick pan; purchased 2021; coating not peeling. Manufacturer only says “replace if coating peels”; no other manufacturer criteria. General guidance fixtures may or may not be sufficient.
**PASS:** Never conclude **Not yet** solely from absence of peeling. Research general guidance because manufacturer statement does not establish the reverse; decide based on that evidence or abstain appropriately.
**Coverage:** FR-09, FR-13, FR-15.

### EV-08 — Weak sources do not count as corroboration
**Scenario:** Ceramic nonstick pan; purchased 2020; coating significantly worn. No manufacturer guidance. Three retailer sites say replace every three years, with no qualifying credible independent general sources.
**PASS:** **Insufficient evidence**; explain that repetition of weak retailer guidance does not meet corroboration rules.
**Coverage:** FR-10, FR-11, FR-12, FR-16, FR-17.

### EV-09 — Optional inputs and input errors
**Scenario:** A) only nonempty product name; B) product name plus optional date, link, and notes; C) blank/missing name; D) malformed optional date or link.
**PASS:** A and B pass deterministic input validation, preserving supplied facts and unknowns; C and D return controlled **input validation errors**, not an evidence outcome. Missing purchase date never causes rejection or invented product age.
**Coverage:** FR-01, FR-02, FR-25.

### EV-10 — Manufacturer guidance exists but does not resolve
**Scenario:** Verified manufacturer page offers cleaning/maintenance tips but no applicable replacement criterion; two independent credible general sources give compatible replacement criteria.
**PASS:** Research continues to general guidance within the Research Agent stage; maintenance claims not affecting replacement are excluded; decision uses qualifying general evidence.
**Coverage:** FR-08, FR-09, FR-23, FR-27.

### EV-11 — Research evidence contract and claim fidelity
**Scenario:** Controlled sources contain a conditional manufacturer claim and two general claims, each with distinct applicability and limitations.
**PASS:** Research output has unique evidence IDs, URL, source type, claim text, conditions/limitations, applicability, and optional summary; no fabricated URL or stripped conditions. Empty findings and access failures are represented explicitly. Decision Agent receives the structured claims.
**Coverage:** FR-13, FR-20, FR-24, FR-25.

### EV-12 — Research schema validator fails fast
**Scenario:** Research Agent returns malformed JSON, missing required claim fields, invalid types, or duplicate evidence IDs.
**PASS:** Deterministic research validator rejects payload with controlled **system error**; Decision Agent is never invoked; no retry or regeneration. Well-formed but false claims are **not** certified as true by schema validation.
**Coverage:** FR-24, FR-25, FR-26.

### EV-13 — Final validator fails fast
**Scenario:** Decision Agent returns invalid outcome enum, missing required output fields, or evidence IDs absent from research output.
**PASS:** Deterministic final validator rejects with controlled **system error**; no recommendation is shown and no regeneration/retry occurs. Valid-looking but unsupported reasoning remains an evaluation failure, not something the schema validator can guarantee to catch.
**Coverage:** FR-16, FR-18, FR-25, FR-26, FR-27.

### EV-14 — Sequential execution / no feedback loops
**Scenario:** Instrument the stages on successful execution and on failures at each validator; provide only one credible general source in a separate fixture.
**PASS:** Order is input validation → Research Agent → research schema validation → Decision Agent → final validation → output. Neither AI agent calls the other; decision stage does not request additional research. With one credible general source and no manufacturer resolution, return **Insufficient evidence**, not a retry. Failed stages stop downstream execution.
**Coverage:** FR-10, FR-25, FR-26, FR-27.

### EV-15 — Access failure versus no guidance
**Scenario:** Manufacturer URL is inaccessible; independent general sources are either available or unavailable in separate fixtures.
**PASS:** Represent manufacturer retrieval as an access limitation, never as proof that no manufacturer guidance exists; continue general research where possible; communicate remaining limitation and choose an evidence-supported outcome.
**Coverage:** FR-09, FR-17, FR-20.

### EV-16 — Missing expiration information
**Scenario:** Product governed by a labeled expiration date; user provides product name but no label date or purchase date.
**PASS:** Explain that labeled expiration governs; do not invent an expiration or treat purchase date as expiration; do not ask follow-up questions. Return a suitable limited outcome based on evidence and known facts.
**Coverage:** FR-02, FR-05, FR-06, FR-07, FR-17.

### EV-17 — Source independence and applicability
**Scenario:** Two apparently separate websites reproduce the same underlying source; another fixture contains manufacturer advice for a different model or material.
**PASS:** Reposts do not count as independent corroboration; wrong-product manufacturer guidance does not resolve the decision. Return a defensible limited outcome unless other qualifying evidence exists.
**Coverage:** FR-08, FR-10, FR-11, FR-13, FR-27.

### EV-18 — Unknown wear is not significant wear
**Scenario:** User notes “some wear,” while credible applicable evidence requires **significant** wear before replacement.
**PASS:** Do not upgrade unspecified wear to significant wear. Preserve conditionality and specific uncertainty; no unsupported **Replace** or **Not yet**.
**Coverage:** FR-13, FR-15, FR-16, FR-17.

## 4. Component Acceptance Matrix

| Component | Required checks | Explicitly not guaranteed |
|---|---|---|
| Input validation (code) | Required name; optional field formats; preservation of unknowns | Product identification by AI |
| Research Agent (AI) | Manufacturer-first search; appropriate general fallback; replacement-relevant structured claims | Final replacement decision |
| Research validator (code) | JSON schema, field types, unique IDs | Credibility, truth, applicability |
| Decision Agent (AI) | Credibility, independence, conflicts, claim fidelity, six-state outcome | Retrieval retries or research callbacks |
| Final validator (code) | Output schema, allowed states, valid evidence references, mechanically checkable consistency | Proof of semantic reasoning correctness |
| Pipeline | Ordered execution, no feedback loops, controlled errors | Automatic recovery/retry |

## 5. Regression and Release Gate

Run all behavioral cases after any change to prompts, models, retrieval, ranking, schemas, or architecture. **Release gate:** all deterministic contract and fail-fast tests pass; all scenario outcomes are supported by their frozen evidence; no prohibited inference or ungrounded citation is accepted. Track failures by input, retrieval, research extraction, schema, reasoning, or presentation. Do not use a single aggregate accuracy number as a substitute for inspecting critical failures.

## 6. Traceability and Outstanding Work

- Existing EV-01–EV-08 are retained, with EV-03 and EV-05 revised to remove clarification. EV-09–EV-18 cover the agreed V1 changes and previously uncovered risks.
- New architectural behavior is mapped to FR-23–FR-27 in the revised requirements. Existing behavioral requirements FR-01–FR-22 remain the source of truth for recommendation behavior.
- Before implementation, finalize the precise JSON schemas, source retrieval/access-status representation, and the fixture-specific expected outcome for EV-16. The absence of a follow-up must not be replaced with a guessed product fact.
- Perform a final cross-document review when the JSON contracts are approved. Keep live provider reliability testing separate from frozen evidence reasoning tests.

## 7. Additional Contract and Delivery Tests (October 16, 2026)

- **EV-19 — Research is collection-only:** With sources of mixed quality, ResearchResult preserves relevant claims, conditions, and URLs without issuing credibility judgments or replacement decisions.
- **EV-20 — Conservative manufacturer early stop:** Directly applicable, decisive manufacturer guidance stops further searches; merely conditional guidance without known triggering facts does not automatically stop fallback research.
- **EV-21 — Configurable budget:** Research stops at configured query/source limits, returns valid partial or empty evidence, and records budget exhaustion in temporary diagnostics without exposing technical counters in the user response.
- **EV-22 — Claim ID join:** DecisionResult references only IDs in ResearchResult; renderer includes the referenced evidence and source links; missing IDs cause deterministic validation failure.
- **EV-23 — Plain uncertainty:** A condition-dependent or insufficient-evidence outcome includes a concrete plain-language uncertainty explanation; a nested uncertainty taxonomy and numeric confidence are not required.
- **EV-24 — Component-first testing:** Research fixtures, decision fixtures, and validator unit tests run independently before the full pipeline integration/regression suite.
- **EV-25 — No evidence is not schema failure:** An empty but structurally valid ResearchResult reaches Decision Agent, which returns **Insufficient evidence**; malformed JSON fails fast as a system error.

**Release gate:** All EV-01–EV-25 must pass against controlled fixtures before treating V1 as ready for a public demo. Exact budget values and technology selection remain open.

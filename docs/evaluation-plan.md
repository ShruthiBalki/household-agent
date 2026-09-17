# Household Agent — V1 Evaluation Plan

**Updated:** September 17, 2026

## 1. Objective

Validate whether the system behaves according to the V1 requirements before architecture and implementation choices bias behavior.

## 2. Evaluation Method

- Use deterministic scenario fixtures containing user input plus a controlled evidence set.
- Evaluate outcome correctness, clarification behavior, evidence selection, claim fidelity, conflict handling, uncertainty wording, and source presentation.
- A case fails if the final recommendation is unsupported even when retrieval was correct.
- Retain these cases as regression coverage when prompts, models, retrieval, ranking, or architecture change.

## 3. Evaluation Cases

### EV-01 — Explicit manufacturer guidance: happy path

**Scenario:** GreenPan ceramic nonstick pan; purchased June 2021; used several times/week; coating visibly peeling. Explicit applicable manufacturer guidance says replace when peeling.

**PASS:** Recommend **Replace**; show manufacturer evidence; no second source required; no invented uncertainty.

**Coverage:** FR-08, FR-15, FR-18, FR-19

### EV-02 — Unresolved credible-source conflict

**Scenario:** Ceramic nonstick pan; purchased 2021; regular use; no major damage; no manufacturer guidance. Two equally credible independent sources disagree: age-based 3–5 years vs condition-only replacement; conflict cannot be reconciled.

**PASS:** Detect and surface both positions; do not choose, blend, or majority-vote; abstain with **Unresolved evidence conflict**.

**Coverage:** FR-10, FR-14, FR-16, FR-17

### EV-03 — Condition-dependent clarification

**Scenario:** Ceramic nonstick pan; purchased 2022; regular use; condition not provided. Two credible sources agree replacement depends on significant scratching/peeling.

**PASS:** Ask about condition first. If the user cannot establish it after appropriate clarification, return **Condition dependent** and name the missing condition.

**Coverage:** FR-05, FR-10, FR-16, FR-17

### EV-04 — Insufficient evidence

**Scenario:** Identifiable reusable silicone food-storage pouch; purchased 2021; regular use; undamaged. No manufacturer replacement guidance; available general sources fail credibility requirements.

**PASS:** Return **Insufficient evidence**; explain that reliable guidance could not be established; do not turn weak sources into a recommendation.

**Coverage:** FR-09, FR-11, FR-12, FR-16, FR-17

### EV-05 — Iterative product clarification

**Scenario:** User says “kitchen item,” then “pan,” and cannot identify material/coating even after simple observable clarification.

**PASS:** Ask targeted narrowing questions; if identity remains materially ambiguous, stop with **Insufficient product information**. Do not guess a pan type.

**Coverage:** FR-03, FR-04, FR-16, FR-17

### EV-06 — General guidance succeeds

**Scenario:** Ceramic nonstick pan; purchased 2020; regular use; coating **significantly worn**. No manufacturer guidance. Two credible independent sources agree to replace when significantly worn.

**PASS:** Recommend **Replace**; explain that the known condition matches the criterion; cite both independent sources; clearly label the evidence as general guidance.

**Coverage:** FR-09, FR-10, FR-15, FR-18, FR-19

### EV-07 — Claim fidelity / no reverse inference

**Scenario:** Ceramic nonstick pan; purchased 2021; regular use; coating is not peeling. Manufacturer only says “replace if coating peels”; no other criteria.

**PASS:** Do **not** conclude **Not yet** from absence of peeling. Continue to credible general guidance because the manufacturer claim does not establish the reverse conclusion.

**Coverage:** FR-09, FR-13, FR-15

### EV-08 — Weak sources do not count as corroboration

**Scenario:** Ceramic nonstick pan; purchased 2020; regular use; coating significantly worn. No manufacturer guidance. Three retailer sites say replace every three years, but no qualifying credible independent source is found.

**PASS:** Return **Insufficient evidence**; explain that the retailer sources do not satisfy the credibility/corroboration requirement.

**Coverage:** FR-10, FR-11, FR-12, FR-16, FR-17

## 4. Regression Rule

These scenarios form the initial behavioral regression suite. Any later change to prompts, models, retrieval, source ranking, evidence processing, or architecture should be checked against them.

## 5. Traceability Review

Before architecture:

1. Verify every evaluation case maps to one or more requirements.
2. Verify every important behavioral requirement has appropriate evaluation coverage.
3. Resolve contradictions or terminology drift across overview, requirements, evaluation plan, and decision log.
4. Add new evaluation cases only where a meaningful uncovered behavior or failure mode exists.

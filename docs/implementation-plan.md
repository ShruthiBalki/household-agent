# Household Agent — V1 Implementation Plan (Draft)

**Updated:** October 16, 2026  
**Status:** Proposed sequence; no stack or model chosen yet.

## Delivery sequence

1. **Freeze minimal data contracts:** input, ResearchResult with claim IDs and links, DecisionResult with claim references, and controlled system-error shape. Define mechanical invariants and optional fields.
2. **Build deterministic validators:** required product name, optional date/link/notes, research JSON schema, final outcome/claim-reference/uncertainty checks. Fail fast without agent retries.
3. **Implement Research Agent behind an interface:** manufacturer-first retrieval, conservative early stop, conditional general fallback, configurable query/source limits, structured claims, and explicit retrieval errors. No credibility scoring.
4. **Implement Decision Agent behind an interface:** source credibility, independence, applicability, conflict resolution, claim fidelity, six outcome states, simple uncertainty, and evidence ID selection.
5. **Compose backend/API pipeline:** input → research → research validation → decision → final validation → join selected evidence → response. Separate valid insufficient evidence from infrastructure/system errors.
6. **Test each component first:** fixture-driven research, decision, and validator tests; then integration tests and EV-01–EV-25 end-to-end regression suite.
7. **Build minimal web UI:** product name required, purchase date/link/notes optional; render outcome, explanation, cited evidence, uncertainty, and next action. No follow-up interaction.
8. **Evaluate and iterate:** compare model/provider behavior on fixed fixtures, verify source links, inspect temporary privacy-conscious diagnostics, and adjust prompts/configuration without relaxing evidence rules.

## Technology options (not accepted decisions)

- Backend candidate: **Python + FastAPI + Pydantic** for typed API contracts and deterministic validation.
- Coding assistant candidate: **GPT-6** for design, implementation, test generation, and code review; IDE-based coding agent optional. Choose based on local workflow, quality on the evaluation suite, and costs.
- Runtime research/decision models and web retrieval/search providers: **TBD**. Coding model and application runtime model are separate decisions.
- Hosting, frontend framework, authentication, storage, and fixed performance targets: **TBD or outside V1 scope**.

## Acceptance criteria

- All mandatory input and evidence contracts validated deterministically.
- No fabricated manufacturer applicability, reverse inference, or unjustified one-source general recommendation.
- No clarification questions or agent feedback loops.
- Empty/weak research evidence yields a valid outcome; invalid schemas yield controlled system errors.
- Cited claims and URLs are traceable to ResearchResult; temporary diagnostics do not become a persistent user profile.
- Regression suite EV-01–EV-25 passes with documented fixtures.

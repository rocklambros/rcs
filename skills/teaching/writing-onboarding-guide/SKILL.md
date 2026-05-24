---
name: writing-onboarding-guide
description: >
  Writes a multi-audience onboarding guide that explains the same system to
  multiple reader profiles (engineer, scientist, executive, security,
  auditor, learner) without collapsing into one generic-voice document that
  serves nobody well. Produces a per-audience section with an
  audience-specific value-sentence opener, a per-audience depth ceiling
  (engineers get API surface, executives get the decision summary,
  scientists get methodology), and a shared glossary that defines terms in
  the voice of the audience most likely to need each one. Triggers when
  shipping a new system, tool, library, dataset, or service that has more
  than one reader profile in its launch audience; when an existing
  onboarding doc gets conflicting feedback from different cohorts in the
  same week; or when a single README is being asked to do the job of three
  documents. Refuses to engage when the audience is genuinely
  single-profile and refuses to write a middle-voice document that pleases
  nobody.
version: 0.1.0
status: shipped
track: teaching
audience:
  - instructor
  - technical-writer
  - product-manager
  - skill-author
evidence:
  - ai-security-framework-crosswalk
  - genai_agentic_incidents
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Writing an Onboarding Guide

## When to use

Trigger this skill when:

- The user is shipping a new system, tool, library, dataset, model, or internal service and writing the first onboarding document for it
- The launch audience has more than one reader profile in it (e.g., engineers who will integrate it + scientists who will validate it + executives who will sponsor it)
- The user says "I need to onboard the team" and the team is heterogeneous (mix of roles, mix of seniority, mix of technical depth)
- An existing onboarding doc is getting feedback like *"too technical for me"* from one cohort and *"too hand-wavy"* from another — both complaints in the same week, often the same doc
- A README is being asked to serve as the launch doc, the API reference, AND the executive briefing simultaneously (one document, three jobs)
- The user is migrating a system between teams and the receiving team has a different role mix than the originating team
- A regulatory, governance, or audit context requires a doc that an auditor (non-engineer) AND a maintainer (engineer) can both consume

## When NOT to use

Skip this skill and hand off when:

- The audience is genuinely single-profile — e.g., an internal API reference targeted exclusively at backend engineers who will call it; force-fitting a multi-audience format wastes pages
- The artifact is a model card, dataset card, or SBOM where a domain-specific format already exists (use `ml-datasci/writing-model-cards` instead)
- The artifact is a security finding write-up (use `security/writing-pentest-finding` (planned) instead)
- The artifact is a problem-set walkthrough or grading rubric (use `teaching/writing-pset-walkthrough` or `teaching/writing-graded-rubric`)
- The user wants a tutorial for one specific role on one specific task — that is a single-role runbook, not an onboarding guide; the multi-audience overhead is wrong for it
- The system is throwaway / prototype-only with no plans to onboard anyone beyond the author

## Quick start

User: *"We just launched our internal RAG-over-incident-corpus service. I need an onboarding doc for the cross-functional launch — backend engineers will integrate it, ML scientists will validate retrieval quality, and our VP of Engineering signs off on the launch. One document. Help."*

Response: write a single document with three explicit audience sections (Engineer / Scientist / Executive), each opening with an audience-specific "why this matters to you" sentence and each capped at the depth ceiling that role actually needs. Share one glossary across all three sections. Front-load a one-page summary that all three audiences can skim without reading the rest. Refuse to collapse the sections into a single generic-voice document.

```markdown
# Incident-RAG service: launch onboarding

## TL;DR (60 seconds, all audiences)
- What it is, what it does, what it does not do, who owns it, where the slack channel is.

## For engineers (integration)
**Why you care:** you will call this API from your incident-triage pipeline...
- Endpoint, auth, rate limits, error codes, SLA, runbook link.

## For scientists (validation)
**Why you care:** retrieval quality directly affects downstream model recall...
- Eval set, baseline retrieval@k, drift monitoring, how to file a quality regression.

## For executives (decision)
**Why you care:** this replaces a 3-FTE manual triage workflow...
- Cost, risk surface, dependency map, exit criteria, audit posture.

## Glossary
- Incident: ... · Retrieval@k: ... · MTTR: ...
```

See `reference/audience-archetypes.md` for the depth-ceiling-per-role table, `reference/onboarding-template.md` for the full markdown skeleton, and `reference/audience-discovery-prompts.md` for the questions that map a launch audience to the right section set.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `system_name` | string | yes | — | Short name of the thing being onboarded into (service, library, dataset, model, course module). |
| `audiences` | list of role tags | yes | — | The reader profiles the doc must serve. Typical sets: `[engineer, scientist, executive]`, `[engineer, security, compliance]`, `[student, ta, instructor]`. ≥ 2 audiences required; ≤ 5 in one document (above 5, split). |
| `ownership` | string | yes | — | Who owns the system + how to reach them (Slack channel, mailing list, on-call rotation). Goes in the TL;DR for every audience. |
| `system_kind` | enum | yes | — | `service` \| `library` \| `dataset` \| `model` \| `course-module` \| `internal-tool`. Drives which audience-specific sections are skipped (e.g., a dataset has no "API surface" section). |
| `existing_doc` | path | no | none | Path to a prior onboarding doc being replaced. If present, the skill produces a migration map: which sections move where, what is deleted, what is new. |
| `audit_context` | bool | no | `false` | If `true`, add a "for auditors" audience section (compliance / regulatory / external review). Mutually exclusive with throwaway-prototype framing. |
| `single_audience_override` | bool | no | `false` | Set to `true` to deliberately produce a single-audience doc. Forces the skill to first confirm that the audience genuinely is single-profile (and explain why the multi-audience format was not chosen). |

## Workflow

```
Onboarding-guide authoring progress:
- [ ] 0. Confirm scope: ≥ 2 distinct reader profiles in the launch audience; if only 1, stop and explain why
- [ ] 1. Audience discovery: identify each audience's primary decision (integrate / validate / approve / comply / learn)
- [ ] 2. Audience depth ceiling: pick the depth this audience needs and CAP at it; engineers get API not strategy; executives get decision not API
- [ ] 3. TL;DR (60-second skim): name, one-line purpose, owner, channel, "do not use it for X"
- [ ] 4. Per-audience opener: first sentence answers "why this matters to you, specifically"
- [ ] 5. Per-audience body: structured by what THIS audience will do with the system
- [ ] 6. Shared glossary: one definition per term; defined in the voice of the audience most likely to need it
- [ ] 7. Cross-audience links: each section ends with "if you also need <other audience's section>"
- [ ] 8. Out-of-scope statement: what the system is NOT for (prevents one cohort showing up with the wrong expectation)
- [ ] 9. Feedback loop: a single channel where ALL audiences send onboarding feedback; one owner triages
```

### Step 1: Audience discovery — name the primary decision each audience must make

The single biggest failure mode of a multi-audience doc is treating every audience as wanting "to understand the system." That is too vague. Each audience must make ONE specific decision after reading their section. Name it.

| Audience | Primary decision (after reading) |
|---|---|
| Engineer | *Can I integrate this into my service this sprint?* → needs API surface + error model + auth + SLA |
| Scientist | *Is the output reliable enough for my downstream model?* → needs eval set + baseline metrics + drift monitoring + how-to-file-regression |
| Executive | *Should I sponsor / fund / approve this?* → needs cost + risk + dependency map + exit criteria |
| Security / compliance | *Does this clear our policy bar?* → needs threat model + data flows + audit log location + DSR readiness |
| Auditor / external reviewer | *Can I attest to its operation?* → needs governance owner + change log + incident log + control mapping |
| Student / learner | *What do I need to know before I touch this?* → needs prerequisites + tutorial path + escalation channel |
| Instructor / TA | *How do I teach this with it?* → needs pedagogy notes + common student pitfalls + reference solutions |

If you cannot name the primary decision for an audience, drop that audience from the doc. A reader without a decision to make does not need an onboarding section.

### Step 2: Depth ceiling — when in doubt, undershoot

| Audience | Depth ceiling | What goes BELOW the ceiling |
|---|---|---|
| Engineer | API surface, error model, performance envelope, runbook | Internal architecture, model training details (link out) |
| Scientist | Evaluation methodology, baselines, drift signals, regression workflow | Production SLOs, on-call rotation (link out) |
| Executive | TL;DR, decision summary, cost / risk / dependency, exit criteria | API code, eval methodology details (link out) |
| Security / compliance | Threat model, data classification, audit trail, DSR | Code-level implementation (link out) |
| Auditor | Control mapping, evidence pointers, change history | Operational debugging details (link out) |

The ceiling matters because **each audience pays a tax for every word above their ceiling**. An executive reading a curl example is being slowed down. A scientist reading a quarterly cost projection is being slowed down. Section the document so each reader pays only their tax.

### Step 3: TL;DR — the one section everyone reads

Every multi-audience doc earns a TL;DR by being more than 2 pages. The TL;DR is the only section every audience reads. Required fields:

- **What it is** (one line, no jargon above any audience's ceiling)
- **Primary purpose** (one line, names the user job the system performs)
- **Owner + channel** (Slack channel, mailing list, on-call rotation, escalation path)
- **What it is NOT for** (one to three lines; prevents the wrong-cohort-shows-up failure)
- **Status** (alpha / beta / GA / sunset; sets reader expectation about reliability)

### Step 4: The audience opener — the first sentence is the entire game

Every audience-specific section opens with **one sentence that says why this audience specifically should keep reading**. This sentence is the difference between "I'll skim my section" and "I'll close this tab."

- ❌ *"This section describes the API."*
- ✅ *"Engineers: you will call this API at most once per incident triage; the rate limit is 50/min/team. Read this before your next on-call shift."*

- ❌ *"This section is for executives."*
- ✅ *"Executives: this replaces a 3-FTE manual triage workflow with a service that costs \$28K/year; the dependency on Pinecone is the largest risk to flag."*

The opener does three things at once: identifies the audience, states the value, and names the cost of NOT reading. Do not skip it.

### Step 6: Glossary — define once, in the voice of the audience that needs it most

A shared glossary across audience sections prevents drift. The convention: define each term in the voice of the audience most likely to look it up.

- "Retrieval@k" — defined in the scientist's voice (recall, evaluation, baseline)
- "Rate limit" — defined in the engineer's voice (per-team token budget, 429 response, backoff)
- "Total cost of ownership" — defined in the executive's voice (FTE-equivalent, infra spend, license)
- "DSR" — defined in the compliance voice (data subject request, deletion within 30 days, audit log)

Each audience section references the glossary instead of redefining inline.

### Step 8: Out-of-scope statement — name what the system is NOT

The cheapest insurance against the wrong-cohort-shows-up failure: a `## Out of scope` section that says, in plain language, what the system is not for. Examples:

- "Not for real-time inference loads above 100 QPS."
- "Not a substitute for the human review step in incident triage."
- "Not approved for use on EU-resident data (compliance: see GDPR section)."
- "Not for student grading; use the assessment service instead."

This section often deflects 30-50% of onboarding-channel questions.

## Outputs

A single markdown document containing:

1. **TL;DR** (≤ 200 words, all audiences) — name, owner, channel, status, what-it-is-NOT
2. **One section per audience** (typical: 200-500 words each), structured per the audience archetype, opened with the audience-specific value sentence
3. **Shared glossary** — terms defined once, in the voice of the audience most likely to need each one
4. **Out-of-scope statement** — explicit list of what the system is NOT for
5. **Feedback channel** — one channel, one owner, one triage cadence
6. **Cross-audience navigation** — each section ends with a pointer to the most-likely-adjacent audience's section

Length: 5-15 pages depending on audience count. Above 15 pages, split into a launch doc (everyone reads) + a per-audience deep-dive (linked from each section).

## Failure modes

Known anti-patterns and how this skill catches them:

- **Generic-voice doc that satisfies nobody** — caught by mandatory per-audience sections with depth ceilings; the doc cannot collapse to a single tone
- **One audience's section over-runs the doc** — caught by the depth-ceiling table; engineers' API surface stays in the engineer section, not the executive section
- **Missing primary-decision-per-audience** — caught by step 1; if an audience has no decision to make, drop the section
- **No TL;DR, so executives bounce after page 1** — caught by step 3 as a mandatory front section
- **Wrong cohort shows up expecting wrong thing** — caught by step 8 out-of-scope statement
- **Audience opener written as "this section describes..."** — caught by step 4; the opener must name a value to the audience, not the section topic
- **Glossary duplicated inline per section, drifts between sections** — caught by step 6 shared glossary
- **Feedback channels fragmented per audience** — caught by step 9 single channel with one owner
- **Doc shipped without a "not for" statement, leading to audience mismatch** — caught by step 8
- **5+ audiences crammed into one document** — caught by the input contract (≤ 5 audiences in one doc; split above that)

## References

- `reference/audience-archetypes.md` — the depth-ceiling-per-role table, expanded with structural prompts per archetype
- `reference/onboarding-template.md` — the full markdown skeleton, copy-paste-ready, for the common 3-audience set
- `reference/audience-discovery-prompts.md` — questions to ask the launching team to map a launch audience to the right section set
- [Diátaxis framework, Procida](https://diataxis.fr/) — the four-quadrant taxonomy of technical documentation (tutorials / how-to / reference / explanation); onboarding docs span more than one quadrant per audience
- [Write the Docs: audience-first documentation](https://www.writethedocs.org/guide/writing/docs-principles/) — practitioner guidance on audience analysis

## Examples

### Example 1: Cross-functional service launch (happy-path)

Input: *"We just launched our internal RAG-over-incident-corpus service. I need an onboarding doc for the cross-functional launch — backend engineers will integrate, ML scientists will validate retrieval quality, and our VP of Engineering signs off."*

Output: skill produces a single doc with TL;DR + Engineer + Scientist + Executive sections. The TL;DR names the owner team, the Slack channel, the alpha status, and "not for real-time use above 100 QPS." Engineer section opens *"You will call POST /v1/retrieve from your triage pipeline; the rate limit is 50 req/min/team and the SLA is p95 < 800ms"* and covers API + errors + runbook. Scientist section opens *"Retrieval@5 on the GoldenSet-v2 eval set is 0.78 (baseline lexical = 0.41); regressions below 0.70 page the owner"* and covers eval methodology + drift monitoring + how-to-file-regression. Executive section opens *"This replaces 3 FTE of manual triage with a service costing \$28K/year + 0.5 FTE for maintenance; Pinecone is the single-vendor dependency to flag"* and covers cost + risk + exit criteria. Shared glossary defines Retrieval@k (scientist voice), rate limit (engineer voice), TCO (executive voice). Out-of-scope explicitly names "not for compliance-restricted data" and "not a substitute for human review." Feedback channel: #incident-rag-onboarding, owner: J. Smith.

### Example 2: Existing doc getting one-star reviews (edge-case)

Input: *"Our onboarding README for the feature store is getting feedback like 'too technical' from PMs and 'not technical enough' from new engineers in the same Slack thread. Fix it."*

Output: skill diagnoses the failure as a single-voice document being asked to serve two audiences with opposite depth needs. Refuses to "split the difference" (which would degrade further). Produces a migration map: TL;DR stays. The existing prose body splits into an Engineer section (API + schema + ingestion patterns + error model) and a PM section (what-it-is + decision-grade tradeoffs + cost summary + when-to-use-vs-when-not). Glossary becomes shared. The "advanced topics" section that PMs complained about becomes a clearly-labeled Engineer-only deep dive. The "executive summary" that engineers found insulting becomes a TL;DR everyone reads once. Names the failure mode (single-voice + multi-audience) so the team avoids re-introducing it.

### Example 3: Genuine single-profile audience (anti-trigger)

Input: *"I'm writing the API reference for our internal billing service. It's only called by our payments engineering team. Help me onboard them."*

Output: skill identifies this as a genuinely single-profile audience (one engineering team, single role, one purpose). Refuses to produce a multi-audience document — the overhead is wrong for the use case. Instead recommends a single-audience reference: API endpoints, auth, error codes, runbook, on-call. Notes that the multi-audience format applies when ≥ 2 distinct reader profiles exist in the launch audience; one engineering team is not "engineer + executive" even though the team includes a manager. Hands off to a single-audience API reference template and explains why the multi-audience overhead does not earn its keep here.

## See also

- `teaching/writing-pset-walkthrough` — multi-step problem walkthrough for a single audience (student); single-audience cousin of this skill
- `teaching/writing-graded-rubric` — assessment artifact, also audience-targeted (student / TA / instructor)
- `teaching/explaining-statistical-concept` — explains one concept to one audience tier at a time; complementary, not multi-audience in the same doc
- `ml-datasci/writing-model-cards` — domain-specific single-format doc (model card); use when the artifact is a model and the audience is known
- `workflow/scaffolding-ml-research-notebook` (planned) — sets up the surrounding repo structure; this skill handles the doc that lives in it
- `claude-code-meta/writing-claude-code-skill` (planned) — sibling for skills themselves

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v6-batch-3, skill 5) via PRAGMATIC discipline

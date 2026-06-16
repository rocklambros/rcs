# AIBOM 100% Compliance

How to make a model card score 100% on the genai-security-project/aibom-generator completeness evaluator, with the requirements fetched dynamically so the card stays compliant as that public repo changes.

## Contents

- What the evaluator scores
- Why the requirements are fetched at runtime, never hard-coded
- The generate-verify loop
- Honesty caveat
- Script usage
- Security note

## What the evaluator scores

The evaluator (`src/models/scoring.py`, `calculate_completeness_score`) grades a CycloneDX AIBOM JSON document, not a markdown card. It is registry-driven: `src/models/field_registry.json` defines every scored field, its tier (critical, important, supplementary), its category, and a jsonpath where the value must live.

Scoring is category-based. Five categories carry weights that sum to 100:

| Category | Weight |
|----------|--------|
| required_fields | 20 |
| metadata | 20 |
| component_basic | 20 |
| component_model_card | 30 |
| external_references | 10 |

Each category score is (present fields / total fields) times its weight. A field counts as present when its jsonpath resolves to a non-empty value. The subtotal is the sum of category scores. Penalties then apply: missing critical fields cut the score (more than three missing multiplies by 0.8, two or more by 0.9), and five or more missing important fields multiply by 0.95. A 100 requires every field present and zero penalty.

## Why the requirements are fetched at runtime, never hard-coded

The field set and weights live in the public repo and change over time. A model card that hard-codes today's fields silently falls below 100 the moment the repo adds a field. The bundled engine clones the repo at run time, reads the current `field_registry.json`, and scores with the repo's own scorer. The required-field list is therefore always the live one.

## The generate-verify loop

This is a validator-driven loop (run, read failures, fix, repeat), the pattern this kind of completeness check rewards.

```
AIBOM 100% loop:
- [ ] 1. Fetch live requirements:   python3 scripts/aibom_compliance.py requirements
- [ ] 2. Scaffold the structure:    python3 scripts/aibom_compliance.py scaffold model.aibom.json
- [ ] 3. Replace every <FILL:...> placeholder with real content from the model card
- [ ] 4. Score it:                  python3 scripts/aibom_compliance.py score model.aibom.json
- [ ] 5. If RESULT is FAIL, read missing_fields, add each at its jsonpath, return to step 4
- [ ] 6. Stop when RESULT is PASS (100%)
```

The scaffold places a value at every live jsonpath, so a freshly scaffolded document already scores 100 structurally. The work is replacing placeholders with the real model's values drawn from the markdown model card you authored in the main workflow.

## Honesty caveat

The evaluator measures structural completeness, presence of a non-empty value at each jsonpath. It does not check truthfulness. A document full of placeholder strings scores 100 and is worthless. Every `<FILL:...>` must carry the model's real content: the real datasets, the real limitations, the real energy figures, the real download location. A model card submitted with placeholders is dishonest and fails any serious review. Treat 100% as the floor for structural completeness, not a substitute for accurate content.

## Script usage

The engine lives at `scripts/aibom_compliance.py`. It needs only Python 3 and git. It clones the public repo to a temporary directory and removes it after the run.

```bash
# 1. See the live required fields, categories, and weights
python3 scripts/aibom_compliance.py requirements

# 2. Generate a maximal CycloneDX AIBOM populated at every live jsonpath
python3 scripts/aibom_compliance.py scaffold model.aibom.json

# 3. After filling real values, verify the score
python3 scripts/aibom_compliance.py score model.aibom.json

# Pin a reviewed commit for a sensitive run
python3 scripts/aibom_compliance.py --ref <git-sha> score model.aibom.json
```

The `score` command exits 0 only when the total is 100.0 with no penalty, so it drops into CI or a pre-submission gate.

## Security note

Scoring runs the repo's `scoring.py` and `registry.py`, pure functions over local files with no network calls or side effects beyond reading the clone. For a sensitive environment, review those two modules or pin `--ref` to a commit SHA you have read. The default run targets the repo's default branch HEAD, which is what "stay current as the repo changes" requires.

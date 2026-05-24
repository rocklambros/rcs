<!-- THREAT-MODEL.md — research-corpus variant. -->
<!-- Used for projects whose deliverable is a dataset (incident corpus, attack -->
<!-- transcript collection, exploit catalog) rather than a tool. -->

# Threat Model — `<project_name>` (research corpus)

> **Status:** Starter template. Fill in every `<!-- TODO -->` block before
> publishing v0.2 or later.

## Data sensitivity

What is the most sensitive class of data in this corpus?

<!-- TODO: classify (public-observed / pseudo-anonymized / PII / regulated). -->

## Re-identification risk

Could an adversary re-identify individuals, organizations, or specific systems
from the corpus?

<!-- TODO: per-field re-identification analysis; reference the -->
<!-- auditing-synthetic-data-leakage skill if synthetic; document mitigations -->
<!-- (aggregation, k-anonymity, redaction, DP noise). -->

## Downstream misuse risk

How could an adversary use this corpus to build attacks?

<!-- TODO: enumerate downstream-misuse cases (training adversarial models, -->
<!-- targeting victims named in the corpus, scaling attack templates). -->

## License of source material

For each data source: what is the license, and does it permit redistribution?

<!-- TODO: per-source license table. -->

## Consent class

Was each subject of the data informed / opted-in / opted-out?

<!-- TODO: per-source consent class table; reference the -->
<!-- building-data-dictionary-with-consent-class skill. -->

## Disclosure window for source-system vulns

If the corpus surfaces vulnerabilities in upstream systems (e.g., incident
write-ups that reveal unpatched issues), document the disclosure path.

<!-- TODO: per-source disclosure procedure. -->

## Residual risk

What misuse risks remain after the mitigations above?

<!-- TODO: explicit list. -->

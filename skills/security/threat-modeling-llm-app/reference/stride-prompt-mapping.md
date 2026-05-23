# STRIDE × LLM-app boundary — mapping examples

This file is **illustrative**, not a threat catalog. The skill always works against a user-supplied catalog (OWASP LLM Top 10, MITRE ATLAS, MAESTRO, etc.). These examples show how common LLM-app threats are commonly classified — use them to calibrate your own register entries.

## Notation

- **Boundary** is shorthand for the data crossing referenced in `SKILL.md` § Step 3.
- **STRIDE letter:** S=Spoofing, T=Tampering, R=Repudiation, I=Information disclosure, D=Denial of service, E=Elevation of privilege.
- A single threat commonly hits multiple cells; one row per (boundary, STRIDE) pair.

## Examples

### User → app

| Threat (illustrative) | STRIDE | Notes |
|---|---|---|
| User crafts a message that impersonates the system role ("ignore previous instructions, you are now…") | T, S | Most direct prompt-injection vector. |
| User submits a megabyte-scale prompt designed to exhaust context window | D | Token-bomb / context-flood. |
| User submits content laden with PII that the app will then echo back or store | I | Sensitive-data ingress; downstream policy violation. |

### App → model

| Threat (illustrative) | STRIDE | Notes |
|---|---|---|
| System prompt contains secrets that a successful injection could exfiltrate | I | Leak of operator credentials, internal URLs, instructions. |
| Model gateway lacks per-tenant isolation; one tenant's prompt leaks into another's session | I, S | Multi-tenant SaaS hosting. |
| Outbound traffic to model API is unmonitored / unaudited | R | No log → cannot reconstruct what was sent. |

### Retriever → context

| Threat (illustrative) | STRIDE | Notes |
|---|---|---|
| RAG corpus contains attacker-controlled content (e.g., scraped web pages, public wiki, customer-uploaded files) that carries injected instructions | T, E | Indirect prompt injection — the most common modern attack class. |
| Embedding similarity returns sensitive document the requesting user is not authorized to see | I | RBAC bypass via vector search. |
| Retrieval source can be rewritten by a low-privilege user (e.g., shared Confluence space) | T | Supply-chain attack on retrieval. |

### Model → tool

| Threat (illustrative) | STRIDE | Notes |
|---|---|---|
| Model emits a tool call with attacker-influenced arguments (e.g., `refund_order(order_id="…' OR 1=1 --")`) | T, E | Tool arguments treated as trusted by downstream system. |
| State-changing tool can be called without human-in-the-loop gate | E | Excessive agency (OWASP LLM08). |
| Tool dispatcher logs prompt + tool-call but logs are unprotected | I, R | Sensitive audit trail. |

### Model → output sink

| Threat (illustrative) | STRIDE | Notes |
|---|---|---|
| Model output rendered as HTML / markdown without sanitization; can embed clickable phishing links | T, S | Insecure output handling (OWASP LLM02). |
| Output stored in a database queried by other downstream services | T | Stored-XSS-style propagation. |
| Output forwarded to a downstream LLM (chain-of-models) without validation | T | Compounding injection across stages. |

## How to use this file

1. Identify your real boundaries from the user's app description (do not assume the boundaries listed here exhaustively cover your case).
2. For each catalog item the user supplied, ask which boundary(ies) it lives at and which STRIDE category(ies) it implicates.
3. Use this table only to sanity-check your classifications, never as a substitute for walking the user-supplied catalog.

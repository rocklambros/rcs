---
name: auditing-graphql-nullability
description: >
  Walks a practitioner through auditing a GraphQL schema for over-permissive
  nullability — fields and arguments that are nullable when they should not be,
  root query/mutation return types that allow null silently swallowing errors,
  and list element nullability that propagates failures to parent resolvers.
  Identifies specific field paths, explains the downstream consequence of each
  violation (silent null propagation, incomplete error surfacing, client
  defensive-code burden), and recommends concrete SDL fixes. Triggers when the
  user provides a .graphql or SDL snippet and asks for a nullability audit,
  schema review, or GraphQL hardening assessment. Skips when the request is
  about GraphQL authorization, rate-limiting, field-level access control, or
  query complexity without a schema to audit.
version: 0.1.0
status: shipped
track: security
audience: [api-eng, backend-eng, security-eng]
evidence:
  - graphql-spec-nullability
  - graphql-best-practices-error-handling
last-updated: 2026-05-23
---

# Auditing GraphQL Nullability

## When to use

Trigger this skill when the user:

- Provides a `.graphql` file, SDL snippet, or schema dump and asks for a
  nullability review, hardening assessment, or schema audit
- Asks "should these fields be nullable?" or "what does nullable mean for my
  GraphQL API?"
- Is designing a new schema and wants to bake in correct nullability before
  first deploy
- Is preparing a schema change and needs to evaluate whether loosening
  nullability (adding `!` removals) is safe or whether tightening it is
  warranted

## When NOT to use

Skip this skill when:

- The user asks about field-level authorization, `@auth` directives, resolver
  access control, or row-level security — that is a different skill
  (authorization enforcement), not a nullability audit
- The user asks about query complexity, rate limiting, or depth limiting —
  separate concerns
- The user asks about GraphQL subscription semantics, batching, or N+1
  resolver patterns without providing a schema to audit
- The schema provided is already fully non-null (`!` on all appropriate fields)
  and the user's question has nothing to do with nullability

## Quick start

User says: "Here's my GraphQL schema. Audit it for over-permissive nullability."

Skill response: walks every type definition. Per finding: field path · current
SDL · recommended SDL · violation category · downstream consequence. Produces a
verdict table. Recommends `!` additions at the type level (not resolver level)
so the constraint is enforced by the GraphQL runtime, not opt-in per resolver.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| schema | SDL string or file path | yes | — | The GraphQL schema to audit. Inline SDL, a `.graphql` file, or `schema.graphql`. |
| federation_context | bool | no | false | Set true if the schema is a federated subgraph. Nullable fields resolved by external services are annotated, not automatically flagged. |
| mutation_coverage | bool | no | true | Include mutation input types and mutation return types in scope. |
| severity_threshold | "low" \| "medium" \| "high" | no | "low" | Show all findings at or above this threshold. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist and check off each step as the audit progresses:

```
GraphQL nullability audit progress:
- [ ] Identify all object types and their fields; record current nullability
- [ ] Flag nullable identifier fields (id, uuid, key) — these should almost always be non-null
- [ ] Flag nullable required scalar fields (email, name, createdAt) — business logic non-null
- [ ] Audit root Query/Mutation return types for nullable single-object returns
- [ ] Audit list types: [T] vs [T!] vs [T!]! — identify which tier applies
- [ ] Audit input type arguments for non-null enforcement at the boundary
- [ ] If federation_context=true, annotate intentionally nullable external fields rather than flagging
- [ ] Produce per-field findings table with SDL fix for each violation
- [ ] Final verdict: pass / pass-with-warnings / fail
```

### Step 1: Nullable identifier fields (always high severity)

Every field that is semantically a primary key, foreign key, or unique
identifier should be non-null. The server ALWAYS knows this value if the object
exists; a nullable id is a schema contract that says "I might not give you the
id," which is almost never intentional.

Patterns to flag (high severity):
- `id: ID` → `id: ID!`
- `userId: ID` → `userId: ID!`
- `productId: ID` → `productId: ID!`
- Any field whose name ends in `Id`, `Key`, `Uuid`, or `Ref` and is typed `ID`
  or `String` without `!`

### Step 2: Required scalar fields (medium-to-high severity)

Fields whose values are always present when the object exists and carry
required business semantics:

- `email: String` → `email: String!` (a User without an email is a broken User)
- `name: String` → `name: String!` (a Product without a name is invalid)
- `createdAt: String` → `createdAt: String!` (timestamp always exists for a
  persisted record)
- `total: Float` → `total: Float!` (an Order total is always calculable)

**Exception**: fields that are genuinely optional in the domain (e.g.,
`middleName`, `bio`, `avatarUrl`, `phoneNumber`) remain nullable. The auditor
must use domain judgment, not a mechanical rule. When in doubt, ask the user.

### Step 3: Root Query and Mutation return type nullability

A nullable Query return type means errors are silently swallowed:

```graphql
# Over-permissive: resolver crash returns null, client sees no error
user(id: ID!): User

# Preferred: resolver crash surfaces as a GraphQL error, not null
user(id: ID!): User!
```

The tradeoff: `User!` means the resolver MUST throw a GraphQL error (not return
null) for the not-found case. That is the correct behavior — a missing user is
an error, not a nullable result.

Flag nullable single-object Query returns as high severity when the query
takes an id argument (implying a specific lookup). Flag nullable list returns
at medium severity.

### Step 4: List type nullability tiers

GraphQL has four list nullability tiers. Explain which applies and why:

| SDL | Meaning | When to use |
|-----|---------|-------------|
| `[T]` | nullable list of nullable items | Almost never — both errors are hidden |
| `[T!]` | nullable list of non-null items | Avoid — list itself can be null |
| `[T]!` | non-null list of nullable items | Avoid — items can still be null |
| `[T!]!` | non-null list of non-null items | Preferred for collections that always exist |

A nullable list means the resolver can return null (distinct from an empty
list `[]`). A nullable list item means a resolver for one item in the list
can crash and the position becomes null, poisoning the whole list silently.

Flag `[T]` (both nullable) as high severity. Flag `[T!]` or `[T]!` (one
nullable layer) as medium severity. Only `[T!]!` passes.

**Exception**: the list itself may be nullable (`[T!]`) if the outer field
represents a genuinely optional association (e.g., `relatedArticles: [Article!]`
where a post may have no related articles and null is semantically distinct from
empty).

### Step 5: Input type and argument nullability

Input arguments that are required for the operation to make sense should be
non-null at the schema level:

- `createUser(input: UserInput)` → `createUser(input: UserInput!)` — if the
  mutation requires input, make the schema enforce it
- Scalar arguments like `(userId: ID)` → `(userId: ID!)` when the resolver
  will always require the value

Nullable arguments are correct for optional filters and optional fields in
patch/update operations.

### Step 6: Federation context handling

When `federation_context=true`, a nullable field may be intentional because it
is resolved by an external subgraph. In this case:

- Annotate the field as "externally resolved — nullable by federation design"
  rather than flagging it as a violation
- Still flag fields within the external type that are nullable without a
  clear external-resolution justification
- Ask the user: "Is this field's nullability intentional because another
  service populates it, or is it a default that was never revisited?"

### Step 7: Produce findings table

Per finding:

```
| Field Path | Current SDL | Recommended SDL | Category | Severity | Consequence |
|---|---|---|---|---|---|
| User.id | id: ID | id: ID! | nullable-identifier | High | Client must null-check before use; resolver crash returns null silently |
| Query.users | users: [User] | users: [User!]! | nullable-list | High | Individual resolver failures poison list positions silently |
| Order.total | total: Float | total: Float! | required-scalar | Medium | Order without total is invalid business state; null treated as zero by some clients |
```

### Step 8: Final verdict

- **Pass**: All identifier fields non-null, all list fields use `[T!]!` or
  justified nullable tier, no silent-null root queries
- **Pass-with-warnings**: Minor optional scalar fields remain nullable
  (acceptable), or federation-justified nullability is documented
- **Fail**: Any nullable identifier field, any `[T]` (doubly nullable list)
  on a core collection, or any root Query returning nullable on an id-lookup

## Outputs

A markdown audit report:

1. **Schema identity** — type count, field count, audit date, federation scope
2. **Per-field findings table** — Field path · Current SDL · Recommended SDL ·
   Category · Severity · Consequence
3. **Counts summary** — high / medium / low findings per category
4. **Final verdict** — pass / pass-with-warnings / fail
5. **Recommended SDL diff** — a before/after SDL snippet showing all `!`
   additions in one place the user can apply directly

## Failure modes

Known pitfalls in nullability audits and how this skill avoids them:

- **Flagging genuinely optional fields** — `bio`, `avatarUrl`, `phoneNumber`
  are nullable by domain design, not negligence. Caught by: domain-judgment
  rule in Step 2 and the "ask when in doubt" instruction.
- **Missing list item nullability** — auditors often check the list wrapper but
  miss the item tier (`[User]!` looks non-null but items are nullable). Caught
  by: Step 4 four-tier table requiring both tiers to be addressed.
- **Federation false positives** — flagging externally resolved fields as
  violations in a federated subgraph. Caught by: `federation_context` flag and
  Step 6 annotation protocol.
- **Auth-question redirect** — applying this skill to an authorization question
  that happens to include a schema. Caught by: "When NOT to use" gate and
  anti-trigger behavior requirement.
- **SDL fix theater** — producing "add ! to all fields" wholesale without
  explaining the consequence of tightening each field. Caught by: per-field
  consequence column requirement in Step 7.

## References

- [GraphQL specification — Non-Null](https://spec.graphql.org/October2021/#sec-Non-Null)
- [GraphQL best practices — Nullability](https://graphql.org/learn/best-practices/#nullability)
- [Shopify GraphQL Design Tutorial — Nullable is a default, not a choice](https://github.com/Shopify/graphql-design-tutorial/blob/main/TUTORIAL.md#nullable-vs-non-nullable)
- [Apollo Federation — External field resolution](https://www.apollographql.com/docs/federation/entities/)
- `reference/graphql-nullability-patterns.md` — internal pattern catalog

## Examples

### Example 1: Basic schema with widespread nullable identifiers (happy-path)

Input: schema with `id: ID` on every type, `[User]` list returns on Query,
no `!` anywhere.

Output: Skill flags every `id: ID` as high severity (nullable identifier).
Flags `users: [User]` as high severity (doubly nullable list). Provides
SDL diff showing `id: ID!` and `[User!]!`. Explains that a resolver crash
on any User in the list will produce a null position, and the client
receives a partial result with no error unless it inspects `errors[]`.

### Example 2: Federated subgraph with intentional nullability (edge-case)

Input: schema with `federation_context=true`, `externalRating: Float` and
`supplierInfo: SupplierInfo` nullable by design (resolved externally), but
`SupplierInfo.name: String` and `SupplierInfo.contactEmail: String` nullable
without justification.

Output: Skill annotates `externalRating` and `supplierInfo` as
"federation-justified nullable — verify external resolver guarantees."
Does NOT flag `Product.id`, `Product.name`, `Product.price`, or
`[Product!]!` — those are already correctly non-null. Flags
`SupplierInfo.name` and `SupplierInfo.contactEmail` as medium severity
with explanation: if the external resolver for SupplierInfo fails, both
fields are silently null, and client code relying on `name` for display
will render blank without an error signal.

### Example 3: Authorization question with a non-null schema (anti-trigger)

Input: "How do I enforce that users can only access their own orders?"
Schema provided: `orders(userId: ID!): [Order!]!`, `Order { id: ID! userId: ID! total: Float! }`.

Output: Skill does NOT generate a nullability audit report. Addresses the
authorization question directly: explains the tradeoffs between
`@auth`-style directive enforcement (schema-level, consistent, requires
a directive implementation) vs resolver-layer authorization (flexible,
no extra tooling, but easy to forget for new resolvers). If nullability
is mentioned at all, one sentence noting the schema is already correctly
non-null — no further audit warranted.

## See also

- `security/threat-modeling-llm-app` — if the GraphQL API serves an LLM
  backend, threat model the full surface
- `security/auditing-transitive-vulnerabilities` — pairs naturally for
  GraphQL library CVE scanning (graphql-js, Apollo Server)
- `workflow/validating-schema-evolution` — use alongside this audit when
  the schema is changing and backward compatibility matters

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: eval-driven authoring via running-eval-driven-skill-development
  skill; 3 eval scenarios co-authored before body

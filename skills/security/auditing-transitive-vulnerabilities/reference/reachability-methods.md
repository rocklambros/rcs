# Reachability methods

The audit's reachability step has three modes: `callgraph`, `import-only`, and `skip`. This reference details per-language tools and patterns.

## Mode: callgraph (slow, accurate)

Build a static call graph and check whether any path from a project entry point reaches a symbol exported by the vulnerable package.

### Python

- `pyan3` — produces a static call graph; supports DOT / JSON output
- `pyright` + custom AST walk — extract import graph + call graph from type-checked sources
- `pycg` — research-grade Python call graph; high precision, slower

```bash
pyan3 src/**/*.py --uses --no-defines --colored --grouped --annotated --dot > callgraph.dot
```

Walk the resulting graph: starting from each entry-point module (CLI scripts, FastAPI routers, Flask blueprints, AWS Lambda handlers, etc.), check whether any reachable node imports or calls a symbol from the vulnerable package.

### JavaScript / TypeScript

- `madge` — module-level import graph
- `dependency-cruiser` — module + symbol-level
- `ts-prune` — TypeScript-specific dead-code detection (proxy for reachability)

```bash
madge --json src/ > module-graph.json
depcruise --include-only "^src" --output-type json src > full-graph.json
```

Reachable if any path from a defined entry point reaches an import of the vulnerable package.

### Go

- `go build -tags=...` analysis + `go list -deps -test=false`
- `nancy` / `govulncheck` — Google's tool has native callgraph reachability

`govulncheck` is the best in class for Go — it ships with the standard tool chain and produces precise call-reachability reports:

```bash
govulncheck ./...
```

### Java

- `jdeps -verbose:class` — class-level dependency graph
- `Soot` — full static analysis framework with call graph (research-grade, complex setup)
- Build-tool integration: Gradle / Maven dep-tree plus class-file analysis

### Rust

- `cargo-call-stack` — static call-stack analysis (experimental)
- `cargo-audit` reports vuln finding but does not do reachability; combine with manual review

### Caveats for callgraph mode

- Reflection / dynamic dispatch / runtime loading is invisible to static analysis
- Vulnerabilities triggered by data (e.g., deserialization gadgets) may not require a direct call to the vulnerable symbol
- Always report reachability with explicit confidence (high / medium / low), never a binary safe / unsafe

## Mode: import-only (fast, conservative)

Grep / AST-walk the source code for any import of the vulnerable package:

```bash
# Python
grep -rE "from (lodash\.template|lodash_template)|import (lodash\.template|lodash_template)" src/

# JS / TS
grep -rE "(import|require).*['\"]lodash\.template['\"]" src/

# Go
grep -rE "^\s*\"github\.com/.../vulnerable-pkg" src/

# Java
grep -rE "^\s*import\s+com\.vulnerable\." src/
```

If any match: `reachability: reachable` (over-states, but safe).
If no match: `reachability: likely-unreachable` (note: still might be loaded by a transitive dep at runtime).

## Mode: skip (assume reachable)

Use when callgraph tools are unavailable or too slow. Treats every finding as `reachability: assume-reachable`. Over-states risk but avoids missing real exposure.

## Per-ecosystem nuance

- **JS dynamic require**: `require(process.env.MODULE)` defeats import-only and callgraph mode. Document as `confidence: low` regardless of mode.
- **Python conditional import**: `if SOMETHING: import lodash_template`. Static analyzers may flag both branches. Import-only catches it; callgraph mode marks it as reachable from the conditional.
- **Go build tags**: `//go:build linux` builds may exclude the file containing the vulnerable import. `govulncheck` is aware of build tags; ad-hoc grep is not.
- **Java reflection**: `Class.forName("com.vulnerable.Bad")` defeats static analysis. Mark `confidence: low`.

## Confidence levels recorded in output

| Mode | Result | Confidence |
|---|---|---|
| callgraph | unreachable + no reflection patterns detected | high |
| callgraph | unreachable + reflection patterns present | medium |
| import-only | no import found | medium |
| import-only | no import found + reflection / dynamic-loading patterns in code | low |
| skip | n/a | n/a (treat as reachable) |

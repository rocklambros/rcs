# Red-flag patterns to look for in MCP server source review

These patterns are not automatically disqualifying, but each one warrants a deeper look and either an explicit safe-explanation or a downgraded verdict.

## Dynamic code execution with user-controlled input

Any function that takes user-provided text and runs it as code or shell — Python's dynamic-execution builtins, the Node child-process family, JavaScript's dynamic-eval family — is the highest-priority pattern to find. Confirm the source either (a) does not contain it, or (b) uses it only on inputs the MCP itself controls.

## Dynamic import with user-controlled string

Pattern where the module/library to load is determined at runtime from caller input. In Python this is `importlib.import_module(user_input)`; in Node this is requiring or importing a path that came from the request. Both can be vehicles for arbitrary-code execution.

## Hardcoded credentials in source

Strings matching API-key formats (e.g. `sk-` prefixes followed by 40+ characters, AWS `AKIA…` patterns, GitHub personal-access-token patterns). Literal `password = "…"` or `api_key = "…"` assignments. Any of these in source are blocking.

## Obfuscated payloads

Look for: long base64 literals followed by decoding-and-execution patterns; hex-encoded byte strings followed by binary execution; one-line minified JavaScript with no source map. Each is a strong indicator of intentional obfuscation.

## Suspicious telemetry

Outbound calls to free-tier analytics services with PII in the payload. Calls to non-author-owned domains for "update checks" that are not declared in the README.

## Excessive permissions

Filesystem-MCP that requires `network` permission. Read-only MCP that requires `write` permission. Single-purpose MCP that exposes ≥ 10 tools.

## Suspicious commit patterns

A single commit replacing all source with new content from a one-off contributor. Squash-merge from a fork that was not reviewed. Commits dated in the future.

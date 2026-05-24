---
name: authoring-tool-hook
description: >
  Walks the Claude Code hook authoring workflow — PreToolUse / PostToolUse /
  SessionStart / SessionEnd / UserPromptSubmit / Stop / SubagentStop /
  Notification event semantics, the stdin/stdout JSON I/O contract, exit-code
  vs structured-response gating, settings.json or plugin-manifest registration,
  and the hook-as-elevated-permission-artifact security review (source review,
  pinning, audit logging, fail-open vs fail-closed). Use when the user is
  writing a hook script to gate tool calls, audit session starts, log
  conversations, or enforce a deny rule at runtime. Hands off to declarative
  settings for statusline, theme, or model configuration.
version: 0.2.0
status: shipped
track: claude-code-meta
audience: [skill-author, security-eng, devops]
evidence:
  - RCS
  - rocks-mac-harness
  - claude-plugins-official
last-updated: 2026-05-23
---

# Authoring a Tool Hook

## When to use

Trigger this skill when the user asks for or implies one of:

- "Help me write a PreToolUse / PostToolUse / SessionStart hook"
- They want to gate a tool call at runtime (block Bash commands matching a deny list, require approval for write tools, log every Edit)
- They want to enforce a policy decision (centralized rule server, local allow/deny rules) before a tool executes
- They want to audit or log conversation events (every user prompt, every session start)
- "How do I block X before it runs?" or "How do I run something before/after each tool call?"

## When NOT to use

Skip this skill and hand off when:

- The user wants statusline, theme, model, or other declarative configuration → that is `~/.claude/settings.json` config, not a hook. Use the `/statusline-setup` skill or the `update-config` skill instead
- The user wants to write a deny/allow rule, not a script that enforces one → use `claude-code-meta/writing-deny-allow-rules`
- The user wants to write a slash command, a subagent definition, or a skill — those are different artifacts with different authoring disciplines
- The user is registering a third-party hook in their own settings and wants the config format only — point at the Claude Code settings.json reference

## Quick start

User says: *"I want a PreToolUse hook that blocks `rm -rf /`, `git push --force` on main, and `--dangerously-skip-permissions`."*

Skill response:

1. Pick the event — PreToolUse for "before the tool runs" gating.
2. Pick the matcher — `Bash` so the hook only fires on Bash calls.
3. Write the script: read JSON payload from stdin, decide allow/block, emit a structured response.
4. Register in `~/.claude/settings.json` or a project `.claude/settings.json` or a plugin manifest.
5. Security review: the hook runs with the user's privileges; pin the script, audit-log every decision, no destructive side effects.
6. Test by triggering the gated case and an allowed case.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| event | one of PreToolUse / PostToolUse / SessionStart / SessionEnd / UserPromptSubmit / Stop / SubagentStop / Notification | yes | — | When the hook fires. See "Event reference" below. |
| matcher | string or null | conditional | null | For PreToolUse / PostToolUse, the tool name(s) the hook fires on. Null means all tools (rare; usually too broad). |
| script_language | "bash" \| "python" \| "node" \| other executable | yes | — | The hook script's language. Hook is invoked as an executable; language must be installed on the user's machine. |
| install_scope | "user" \| "project" \| "plugin" | yes | — | Where the hook is registered. Affects blast radius. |
| failure_mode | "fail-open" \| "fail-closed" | yes | — | What happens if the hook errors or times out. Security gates default fail-closed; observability hooks default fail-open. |

## Workflow

Copy this checklist into the response and check off items as the hook is authored:

```
Hook authoring progress:
- [ ] Event chosen (PreToolUse / PostToolUse / SessionStart / etc.)
- [ ] Matcher scoped to the smallest set of tools needed (NOT unscoped if avoidable)
- [ ] Script reads payload from stdin as JSON (or the documented per-event format)
- [ ] Script emits response per the event's contract (exit code + stdout JSON)
- [ ] Registration in settings.json or plugin manifest with explicit event + matcher + command path
- [ ] Failure mode chosen explicitly (fail-open vs fail-closed) and documented in the script header
- [ ] If hook performs HTTP egress (or any out-of-process I/O): aggressive timeout AND client-side caching of the decision with bounded TTL — REQUIRED, not optional
- [ ] Audit log: every decision logged with timestamp + tool + decision + reason
- [ ] Source review: no unescaped shell interpolation, no eval, no unexpected side effects
- [ ] Pinned: script path is absolute or repo-relative; not a moving target
```

### Event reference

| Event | Fires | Payload (stdin) | Response contract |
|---|---|---|---|
| `PreToolUse` | Before a tool call is dispatched | JSON: tool name + tool input | Exit 0 + JSON `{"decision": "allow"\|"block", "reason": "..."}` |
| `PostToolUse` | After a tool call returns | JSON: tool name + input + output | Exit 0 (mutate-output not typical; logging only) |
| `SessionStart` | At session start, before any user prompt | JSON: session metadata | Exit 0; can emit `<system-reminder>` text on stdout that gets injected |
| `SessionEnd` | At session end | JSON: session summary | Exit 0; logging only |
| `UserPromptSubmit` | When the user submits a prompt | JSON: prompt text | Exit 0; can block by emitting JSON `{"decision": "block", "reason": "..."}` |
| `Stop` | When Claude wants to end the turn | JSON: turn metadata | Exit 0 allows stop; exit nonzero or JSON `{"decision": "block"}` keeps the loop running |
| `SubagentStop` | When a subagent wants to end | Like Stop, but for subagent context | Like Stop |
| `Notification` | On certain notifications (e.g., permission requests) | JSON: notification type + payload | Exit 0; logging only |

Exit-code semantics: exit 0 = allow (or no decision); exit 2 = block (legacy). Modern hooks should emit structured JSON on stdout and rely on the `decision` field rather than exit codes.

### Step 1 — Script structure (PreToolUse example)

```python
#!/usr/bin/env python3
"""PreToolUse hook: block destructive Bash commands.

Reads a JSON payload from stdin describing the tool call. Emits a JSON
decision on stdout. Logs every decision to ~/.claude/hooks/audit.log.

Failure mode: fail-closed (any unexpected exception blocks the call).
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

AUDIT_LOG = Path.home() / ".claude" / "hooks" / "audit.log"

DENY_PATTERNS = [
    re.compile(r"\brm\s+-rf\s+/"),
    re.compile(r"\bgit\s+push\s+(--force|-f)\b.*\b(main|master)\b"),
    re.compile(r"--dangerously-skip-permissions"),
]


def decide(tool_name: str, tool_input: dict) -> tuple[str, str]:
    if tool_name != "Bash":
        return "allow", "non-Bash tool"
    cmd = tool_input.get("command", "")
    for pat in DENY_PATTERNS:
        if pat.search(cmd):
            return "block", f"matches deny pattern {pat.pattern!r}"
    return "allow", "no deny pattern matched"


def audit(decision: str, tool_name: str, reason: str, payload: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps({
        "ts": datetime.utcnow().isoformat() + "Z",
        "tool": tool_name,
        "decision": decision,
        "reason": reason,
    })
    with AUDIT_LOG.open("a") as f:
        f.write(line + "\n")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})
        decision, reason = decide(tool_name, tool_input)
        audit(decision, tool_name, reason, payload)
        json.dump({"decision": decision, "reason": reason}, sys.stdout)
    except Exception as e:
        # fail-closed
        json.dump({"decision": "block", "reason": f"hook error: {e!r}"}, sys.stdout)
        sys.exit(2)


if __name__ == "__main__":
    main()
```

Make the script executable (`chmod +x`) and place it at a stable absolute or repo-relative path.

### Step 2 — Register in settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "/Users/you/.claude/hooks/gate-bash.py" }
        ]
      }
    ]
  }
}
```

For a project-scoped hook, register in `./.claude/settings.json` with a repo-relative path. For a plugin-scoped hook, declare in the plugin's `plugin.json` (see `claude-code-meta/authoring-plugin` reference for the manifest schema).

### Step 3 — Failure mode

Choose ONE explicitly and document at the top of the script:

- **fail-closed**: any exception, timeout, or malformed input blocks the tool call. Use for security gates. Cost: a buggy hook breaks the user's workflow until fixed.
- **fail-open**: any exception allows the tool call to proceed. Use for logging or observability hooks. Cost: a buggy hook silently disables the policy.

Never leave the failure mode ambiguous. A hook that crashes with no documented behavior is a hook whose policy is unknown.

### Step 4 — HTTP egress: timeout AND client-side cache (REQUIRED if applicable)

Hooks fire on the hot path of every matched tool call. If the hook performs HTTP egress (central policy server, remote rule registry, audit-log sink), an unbounded or uncached HTTP round-trip will stall every Bash / Edit / Write the user issues. Two disciplines apply together, neither sufficient alone:

- **Aggressive timeout** (≤ 500 ms typical for a policy gate; ≤ 2 s for richer enrichment). Pair the timeout with the explicit fail-open vs fail-closed choice from Step 3 — what does the hook do when the timeout fires? Security gates fail-closed (block on timeout); observability hooks fail-open (allow + log the gap).
- **Client-side caching** of the policy decision with a bounded TTL (30-120 s typical). Key the cache on `(tool_name, hash(tool_input))` or a coarser bucket if the policy is stack-invariant. Caching is REQUIRED for any HTTP-egress hook: it is the only way the hot path stays sub-millisecond on cache hits. Timeout protects against the slow case; cache prevents the slow case from happening on every call.

Timeout and cache TTL must be tuned together — too-short TTL means too many HTTP calls (defeats the cache); too-long TTL means stale policy decisions (defeats the gate). Document both numbers in the hook README and revisit when the policy-server SLA changes.

If the hook does NOT make out-of-process calls, skip this step.

### Step 5 — Security review (hook = elevated artifact)

The hook script runs with the user's shell privileges. Treat it like any privileged binary:

- **Source review**: no unescaped shell interpolation, no `eval`, no `exec`, no dynamic import based on hook input
- **Pinning**: register the script by absolute path or repo-relative path; never a path that resolves via PATH (could be hijacked)
- **Audit log**: write every decision (allow + block) to a log file the user can review
- **No destructive side effects**: hook should observe + decide, not mutate state. Side effects (writing to user files, making HTTP calls) need explicit justification — and trigger Step 4 if HTTP is in the mix

### Step 6 — Test

Trigger the gated case (e.g., `rm -rf /tmp/test` if the hook blocks `rm -rf /`) and confirm the block. Trigger an allowed case (e.g., `ls`) and confirm allow. Review the audit log; the decision rows must match what you observed. For HTTP-egress hooks, also test: policy-server slow (timeout fires correctly), policy-server unreachable (failure mode behaves as documented), repeated identical tool calls (second and subsequent calls served from cache, not HTTP).

## Outputs

A complete hook artifact:

```
hooks/
├── gate-bash.py            # the hook script (executable, pinned path)
├── README.md               # what the hook does, what it can block, failure mode, audit log location
└── tests/
    ├── test_deny_patterns.py
    └── test_audit_log.py
```

Plus a settings.json (user, project, or plugin) entry registering the hook by event + matcher + command path.

## Failure modes

Known pitfalls in hook authoring and how this skill catches them:

- **Unscoped matcher.** `PreToolUse` with no `matcher` fires on every tool, including Read and Grep, slowing every interaction. Caught by: workflow checklist requires the smallest matcher that meets the need.
- **Ambiguous failure mode.** Hook crashes with no documented behavior; user discovers the policy is silently disabled after an incident. Caught by: Step 3 requires explicit fail-open vs fail-closed with rationale.
- **Hook hangs the session.** Hook makes an HTTP call with no timeout; policy server is slow; every Bash call stalls. Caught by: Step 4 explicit timeout + Step 3 failure-mode choice.
- **HTTP-egress hook with no cache.** Hook has a timeout but no client-side cache, so every Bash invocation pays the HTTP round-trip; the session feels slow even when the policy server is healthy. Caught by: Step 4 requires both timeout AND cache; workflow checklist names caching as REQUIRED for HTTP-egress hooks.
- **Path hijack.** Hook registered as `gate-bash.py` (relative, PATH-resolved); attacker drops a malicious `gate-bash.py` earlier in PATH. Caught by: Step 4 requires absolute or repo-relative path.
- **No audit log.** Hook blocks a tool call; user has no record of why. Caught by: Step 4 requires audit-log writes for every decision.
- **Hook script unpinned in plugin.** Plugin ships a hook script that gets overwritten by an `npm update` of the plugin's deps. Caught by: bundle the script inside the plugin repo, do not depend on an upstream package for the hook body.
- **Confusing a hook with declarative config.** User wants a statusline change and ends up writing a SessionStart hook. Caught by: this skill's When-NOT-to-use hands off to `update-config` / `/statusline-setup`.

## References

- `reference/event-payloads.md` — per-event stdin payload schema and stdout response contract
- `reference/hook-skeleton.md` — copy-paste Python hook skeleton with audit log + fail-closed default
- [Claude Code hooks documentation](https://code.claude.com/docs/en/hooks.md) — official hook reference
- RCS `claude-code-meta/authoring-plugin` — plugin manifest schema for bundling hooks
- RCS `claude-code-meta/writing-deny-allow-rules` — rule authoring (the data this kind of hook enforces)

## Examples

### Example 1: PreToolUse hook gating Bash (happy-path)

Input: *"I want a PreToolUse hook that blocks `rm -rf /`, `git push --force` on main, and `--dangerously-skip-permissions`."*

Output: Skill picks `event: PreToolUse` and `matcher: Bash` to scope to Bash calls only. Walks the script structure: read JSON payload from stdin, parse `tool_input.command`, check against three regex deny patterns, emit `{"decision": "allow"\|"block", "reason": "..."}` on stdout. Defaults to fail-closed: any unexpected error blocks. Writes every decision to `~/.claude/hooks/audit.log`. Registers in `~/.claude/settings.json` under `hooks.PreToolUse` with the absolute script path. Cross-references the source-review and pinning guidance from Step 4.

### Example 2: Hook with HTTP egress to a policy server (edge-case)

Input: *"My PreToolUse hook needs to check a central policy server over HTTP. What do I need to handle?"*

Output: Skill recommends documenting `api.policy.internal.example.com` as the egress target in the hook README; bounding the HTTP call with a 500ms timeout; choosing fail-closed (block) for a security gate or fail-open (allow + log) for an observability hook — and documenting the choice at the top of the script. Recommends client-side caching: cache the policy decision keyed on (tool_name, hash(tool_input)) with a 60-second TTL so the hot path does not make an HTTP call on every Bash invocation. Notes that the timeout AND the cache TTL must be tuned together — too-short TTL means too many HTTP calls; too-long TTL means stale policy decisions.

### Example 3: Statusline configuration handoff (anti-trigger)

Input: *"Help me write a hook that changes my Claude Code statusline to show the current branch and the model name."*

Output: Skill answers that statusline is declarative configuration, not a hook. Recommends configuring `statusLine` in `~/.claude/settings.json` via the `/statusline-setup` skill or the `update-config` skill. Explains that hooks fire on runtime events (PreToolUse, PostToolUse, SessionStart, Stop) and are the wrong artifact for UI / display customization.

## See also

- `claude-code-meta/authoring-skill` — skill-authoring discipline (different artifact)
- `claude-code-meta/authoring-plugin` — plugin manifest schema for bundling hooks
- `claude-code-meta/writing-deny-allow-rules` — rule authoring (the data this hook enforces; rules are declarative, hooks execute)
- `claude-code-meta/writing-mcp-server-securely` — sibling elevated-permission authoring discipline
- `security/auditing-mcp-server-pre-trust` — six-check pattern; applies to bundled hooks the same way it applies to MCP servers

## Status & version

- Status: shipped
- Version: 0.2.0
- Last-updated: 2026-05-23
- Validation note: v0.1.0 PRAGMATIC Sonnet eval scored 3/3 happy-path, 2/3 edge-case (missed the client-side caching rubric for the HTTP-egress hook variant), 3/3 anti-trigger. v0.2.0 reorders the Workflow to make HTTP-egress caching a top-level step (Step 4) and adds an explicit Workflow-checklist item naming caching as REQUIRED for HTTP-egress hooks. Re-validated under PRAGMATIC for v6.0.2 promotion.

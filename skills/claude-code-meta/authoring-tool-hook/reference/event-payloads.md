# Event payloads and response contracts

Per-event stdin payload schema and stdout response contract for Claude Code hooks.

## PreToolUse

**Fires:** before a tool call is dispatched.

**Stdin payload:**
```json
{
  "session_id": "abc-123",
  "transcript_path": "/Users/you/.claude/projects/.../transcript.jsonl",
  "tool_name": "Bash",
  "tool_input": { "command": "ls /tmp", "description": "List /tmp" }
}
```

**Stdout response:**
```json
{
  "decision": "allow",
  "reason": "ls is in the allowlist"
}
```

Or to block:
```json
{
  "decision": "block",
  "reason": "matches deny pattern 'rm -rf /'"
}
```

**Exit codes:** legacy contract: exit 0 = allow, exit 2 = block. Prefer the structured response.

## PostToolUse

**Fires:** after a tool call returns.

**Stdin payload:** PreToolUse payload + `tool_response: { ... }` field.

**Stdout response:** typically none (exit 0). Logging-only.

## SessionStart

**Fires:** at session start, before the first user prompt.

**Stdin payload:**
```json
{
  "session_id": "abc-123",
  "source": "startup" | "resume" | "compact",
  "cwd": "/Users/you/some-project"
}
```

**Stdout response:** optional `additional_context` field whose value is injected as a `<system-reminder>` into the conversation:
```json
{
  "additional_context": "Project context: working in ML repo; pre-commit gate is enabled."
}
```

## SessionEnd

**Fires:** at session end.

**Stdin payload:**
```json
{
  "session_id": "abc-123",
  "reason": "user_quit" | "context_full" | "subagent_done"
}
```

**Stdout response:** typically none.

## UserPromptSubmit

**Fires:** when the user submits a prompt, before the model sees it.

**Stdin payload:**
```json
{
  "session_id": "abc-123",
  "prompt": "the user's prompt text",
  "cwd": "/Users/you/some-project"
}
```

**Stdout response:** can block by emitting:
```json
{
  "decision": "block",
  "reason": "prompt contained a known prompt-injection signature"
}
```

Or inject additional context for the model to see:
```json
{
  "additional_context": "Note: project README says all changes go on feature branches."
}
```

## Stop

**Fires:** when Claude wants to end the turn.

**Stdin payload:**
```json
{
  "session_id": "abc-123",
  "stop_hook_active": true
}
```

**Stdout response:** to keep the loop running:
```json
{
  "decision": "block",
  "reason": "tests have not been run yet"
}
```

Or exit 0 to allow the stop.

## SubagentStop

**Fires:** when a subagent (dispatched via the Agent tool) wants to end.

Same contract as Stop, scoped to the subagent's context.

## Notification

**Fires:** on certain notifications (permission requests, etc.).

**Stdin payload:**
```json
{
  "session_id": "abc-123",
  "notification": { "type": "permission_request", "tool_name": "Bash", "..." }
}
```

**Stdout response:** typically none. Logging only.

## Environment variables available to all hooks

- `CLAUDE_PROJECT_DIR` — the project root (where `.claude/` lives)
- `CLAUDE_SESSION_ID` — the session ID
- All env vars from the user's shell at session start

## Hook timeout

Default timeout per hook invocation: 60 seconds. If a hook exceeds the timeout, Claude Code logs an error and proceeds per the hook's documented failure mode (which the hook must declare; Claude Code's default-on-timeout is "warn and continue" but a security gate that wants fail-closed must enforce that itself by blocking on its own internal timeout).

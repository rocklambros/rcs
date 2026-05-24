# Hook script skeleton (Python, fail-closed)

Copy-paste starting point for a PreToolUse hook with audit logging and fail-closed default.

## Skeleton

```python
#!/usr/bin/env python3
"""<HOOK NAME>: <one-line purpose>

Event: PreToolUse
Matcher: <Tool name(s)>
Failure mode: fail-closed (any exception or timeout BLOCKS the tool call)
Audit log: ~/.claude/hooks/audit.log
"""
import json
import sys
from datetime import datetime
from pathlib import Path

AUDIT_LOG = Path.home() / ".claude" / "hooks" / "audit.log"


def decide(tool_name: str, tool_input: dict) -> tuple[str, str]:
    """Return ('allow' | 'block', reason)."""
    # Replace this with your decision logic.
    return "allow", "no policy match"


def audit(tool_name: str, decision: str, reason: str) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "tool": tool_name,
        "decision": decision,
        "reason": reason,
    }
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})
        decision, reason = decide(tool_name, tool_input)
        audit(tool_name, decision, reason)
        json.dump({"decision": decision, "reason": reason}, sys.stdout)
    except Exception as e:
        # fail-closed: any error blocks the tool call
        audit("(error)", "block", f"hook exception: {e!r}")
        json.dump({"decision": "block", "reason": f"hook error: {e!r}"}, sys.stdout)
        sys.exit(2)


if __name__ == "__main__":
    main()
```

## Register in settings.json

User scope (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "/Users/you/.claude/hooks/your-hook.py" }
        ]
      }
    ]
  }
}
```

Project scope (`./.claude/settings.json`): use a repo-relative path like `${CLAUDE_PROJECT_DIR}/.claude/hooks/your-hook.py`.

Plugin scope: declare in the plugin's `plugin.json` `hooks` array per `claude-code-meta/authoring-plugin` reference.

## Make executable

```bash
chmod +x ~/.claude/hooks/your-hook.py
```

## Test

```bash
echo '{"tool_name": "Bash", "tool_input": {"command": "ls /tmp"}}' | ~/.claude/hooks/your-hook.py
```

Expected output:
```json
{"decision": "allow", "reason": "..."}
```

Test a block case:
```bash
echo '{"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}}' | ~/.claude/hooks/your-hook.py
```

Expected output:
```json
{"decision": "block", "reason": "..."}
```

Then trigger the same tool call inside a Claude Code session and confirm the user-facing behavior matches.

## Fail-open variant

For observability or logging hooks where the policy decision is not the security boundary, replace the `except` block with:

```python
    except Exception as e:
        # fail-open: log the error but allow the tool call
        audit("(error)", "allow", f"hook exception (fail-open): {e!r}")
        json.dump({"decision": "allow", "reason": "hook errored; failing open"}, sys.stdout)
        sys.exit(0)
```

Pick one and document it at the top of the script. Do not leave it ambiguous.

# Security Policy

This repository ships text and prompts that Claude Code, Copilot CLI, Gemini CLI, and the Anthropic API consume directly. Bugs in those prompts can change agent behavior in security-sensitive ways. The policy below explains what to report, how to report it, and what to expect afterward.

## How to report a vulnerability

**Do not file a public issue or pull request for security problems.** Public disclosure before a fix is in place puts every user of the repository at risk.

Email: **rock@rockcyber.com**

Include in the report:

1. The skill, file path, or repository surface affected (for example: `skills/security/auditing-mcp-server-pre-trust/SKILL.md` line 42, or the install loop in `README.md`)
2. The behavior the bug causes (be specific: "the skill instructs Claude to skip a check when input contains X" is actionable; "the skill is broken" is not)
3. The conditions that trigger the behavior (which model, which Claude Code version, which user prompt or input)
4. The impact (what an attacker could do, what data could be exposed, what guarantee is silently violated)
5. A proposed fix if you have one

Encrypted email is supported. Request the public PGP key in your first message.

## Scope

**In scope:**

- Skill bodies (`skills/**/SKILL.md`) that contain instructions which could cause Claude to bypass a safety check, leak sensitive information, execute unintended code, or produce a confidently-wrong answer in a high-stakes domain
- Reference materials (`skills/**/reference/*.md`, `skills/**/reference/*.py`) that ship code or templates with security implications
- The lint and eval tooling (`tools/*.py`) where a bug could allow malicious frontmatter or bypassed validation to ship
- The CI workflows (`.github/workflows/*.yml`) where a bug could allow unsigned or unreviewed content to merge
- The install loop in `README.md` and any scaffolding pattern that could clobber or symlink-attack a user's `~/.claude/` directory
- Cross-skill interactions where one skill's output could mislead another skill that consumes it

**Out of scope:**

- Bugs in Claude itself, Claude Code, Copilot CLI, Gemini CLI, or any model behavior unrelated to the contents of this repo. Report those to the respective vendor
- Bugs in user code that copy-pastes from a `reference/*.py` example without adapting it (these are integration mistakes. The reference files document themselves as patterns to adapt)
- Disagreements with a skill's recommendation that do not constitute a safety bug. Open a regular issue or PR for those
- AI attribution in commits or PR descriptions. That is a policy violation, not a security bug. See `CONTRIBUTING.md`

## What to expect

| Stage | Target | Notes |
|---|---|---|
| Acknowledgement | Within 3 business days | A human reply confirming receipt and the next step |
| Triage decision | Within 7 business days | Severity assigned (critical / high / medium / low / not-a-bug), scope confirmed, fix-or-defer named |
| Fix in main | Within 14 business days for critical and high; within 30 days for medium; best-effort for low | Public commit with a CHANGELOG entry crediting the reporter unless they prefer anonymity |
| Coordinated public disclosure | After the fix ships, with the reporter's consent on timing | A short writeup goes into `CHANGELOG.md` and an advisory under the repo's Security tab |

If the timeline above slips, the reporter is told why before the deadline passes. If the report is rejected as not-a-bug, the reporter receives the reasoning and may appeal once.

## Safe-harbor language for good-faith research

This policy authorizes good-faith research that:

- Stays within the scope above
- Avoids accessing, modifying, or destroying data belonging to anyone other than the researcher
- Avoids degrading the experience of other users of this repository
- Reports findings through the email channel above and does not disclose publicly before a fix or coordinated-disclosure timeline is agreed
- Does not exploit a finding beyond what is necessary to demonstrate it

Research conducted under these conditions will not be the subject of legal action initiated by the maintainer. This authorization does not bind any third party.

If you are unsure whether a given activity is in scope, ask first via the email above. A short clarifying exchange before testing is always preferred to a surprise disclosure.

## Credit

Reporters are credited in `CHANGELOG.md` for the release that fixes the issue, with the wording the reporter prefers. Anonymous credit is offered by default. Named credit is on request. There is no monetary bounty.

## What this policy does not do

This policy is one piece of the disclosure machinery. It does not:

- Bind Anthropic, GitHub, or any other third party
- Guarantee a fix will land at any specific date beyond the targets above. Reality intrudes on plans
- Substitute for professional security assessment of any deployed system that uses this repository

For the underlying discipline that informed this policy, see [`skills/security/writing-vdp-and-coordinated-disclosure`](skills/security/writing-vdp-and-coordinated-disclosure/) which encodes the full VDP authoring workflow.

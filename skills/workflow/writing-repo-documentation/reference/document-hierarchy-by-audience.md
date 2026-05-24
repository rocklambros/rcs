# Document Hierarchy by Audience

Reference for `writing-repo-documentation`. Maps audience tiers to the documents each tier reads, with file-name conventions per forge and a Diataxis-aligned `docs/` layout. Use this matrix in Step 2 of the workflow to decide which files the current project needs.

## The four-tier audience hierarchy

| Tier | Who | What they want from the docs |
|---|---|---|
| Novice | Has not used the tool. May not know the field. | Decide whether to keep reading. Then run something and see a result |
| Regular user | Uses the tool. Does not contribute. | Look up how to do specific tasks. Understand error messages |
| Contributor | Sends PRs. | Set up the dev environment. Run the tests. Match the project's conventions |
| Maintainer | Owns releases. | Cut a release. Triage incoming issues and PRs. Coordinate security disclosures |

A given project may have only some of these tiers. A personal-scratch repository has no contributor tier; a closed-source internal library may have no novice tier (every reader has been pre-briefed). Knowing which tiers are present tells the writer which documents to draft.

## Documents by tier

| Document | Novice | Regular user | Contributor | Maintainer | Security researcher |
|---|---|---|---|---|---|
| `README.md` | primary | primary | secondary | secondary | secondary |
| `CONTRIBUTING.md` | rare | rare | primary | secondary | secondary |
| `SECURITY.md` | rare | rare | secondary | secondary | primary |
| `CODE_OF_CONDUCT.md` | rare | rare | primary | primary | secondary |
| `CHANGELOG.md` | rare | primary (returning) | secondary | primary | secondary |
| `docs/tutorials/` | primary | secondary | rare | rare | rare |
| `docs/how-to/` | secondary | primary | secondary | rare | rare |
| `docs/explanation/` | secondary | secondary | primary | primary | secondary |
| `docs/reference/` | rare | primary | primary | secondary | secondary |
| `ROADMAP.md` (optional) | rare | secondary | secondary | primary | rare |
| Internal release runbook | n/a | n/a | rare | primary | n/a |

"Primary" means the reader will land here first. "Secondary" means the reader will visit when a primary document points there. "Rare" means the reader will only land here on a specific search.

## File-name conventions per forge

Most file names are forge-neutral. A few specific paths differ.

| File | GitHub | GitLab | Gitea / Forgejo / Codeberg |
|---|---|---|---|
| Issue templates | `.github/ISSUE_TEMPLATE/` | `.gitlab/issue_templates/` | `.gitea/issue_template/` or `.forgejo/issue_template/` |
| Pull-request templates | `.github/pull_request_template.md` | `.gitlab/merge_request_templates/` | `.gitea/PULL_REQUEST_TEMPLATE.md` |
| Funding | `.github/FUNDING.yml` | n/a | n/a |
| Workflows | `.github/workflows/*.yml` | `.gitlab-ci.yml` | `.gitea/workflows/*.yml` (act_runner) or `.forgejo/workflows/*.yml` |
| Repository-level Code of Conduct | `CODE_OF_CONDUCT.md` (recognized by GitHub) | `CODE_OF_CONDUCT.md` | `CODE_OF_CONDUCT.md` |
| Security policy auto-discovery | `SECURITY.md` (linked under Security tab) | `SECURITY.md` | varies; check forge docs |

Cross-forge: keep the canonical content in `SECURITY.md`, `CONTRIBUTING.md`, etc. at the repo root. Forge-specific files (issue templates, workflows) go in the forge-specific directory.

## The Diataxis split

The `docs/` directory is most useful when sub-divided along Diataxis lines (Daniele Procida, 2017). The four-quadrant framework separates documentation by the reader's posture:

```
                 Practical                Theoretical
            +-----------------+-------------------+
   Study    | Tutorials       | Explanation       |
            | (learning)      | (understanding)   |
            +-----------------+-------------------+
   Work     | How-to guides   | Reference         |
            | (doing)         | (looking up)      |
            +-----------------+-------------------+
```

Each quadrant optimizes for one reader posture and one writing discipline:

- **Tutorials** teach. A tutorial is a guided walkthrough from a known starting point to a known result. The reader is learning. Tutorials must work end to end; a broken tutorial is worse than no tutorial
- **How-to guides** help the reader achieve a goal. A how-to assumes the reader already knows the basics and now has a specific task. The shape is "to do X, run Y." Keep them recipe-shaped
- **Explanation** answers "why." Concepts, design decisions, the trade-offs taken and the trade-offs rejected. The reader is trying to build a mental model. Explanations can be long
- **Reference** is what the reader looks up. Function signatures, configuration options, error codes. Reference is usually auto-generated from the source. Reference is read in random-access order

When the four quadrants are conflated, each document does its job worse. A tutorial that tries to be exhaustive becomes a reference and loses the teaching arc. A reference that tries to be friendly becomes a tutorial and loses the lookup speed. The split is worth the up-front cost.

## What goes in the wiki vs. what goes in the repo

The wiki is a different surface with different properties:

| Repository docs | Wiki |
|---|---|
| Versioned with the code | Lives outside the code's version history |
| Reviewed in PRs | Edited inline by maintainers (sometimes by anyone) |
| Updates ship in releases | Updates ship immediately |
| Read by anyone (including offline `git clone`) | Read only via the forge's web UI |

Use the wiki for content that:

- Updates faster than the code releases (third-party-tool compatibility tables, dependency-upgrade notes, conference-talk slides)
- Targets the running deployment rather than the source (operational runbooks for the maintainer team)
- Documents external integrations whose behavior is owned outside the repo

Use the repo for content that:

- Is canonical (the README, CONTRIBUTING, SECURITY, the Diataxis-split docs)
- Needs to round-trip with the code (an `examples/` directory, a tutorial whose code must keep working as the API evolves)
- Must be available offline or in a clone (most things)

A project shipping both a repo and a wiki should cross-link explicitly. The wiki link belongs in the README's "Where to go next" section. The repo's `docs/` should not duplicate wiki content; pick one location per topic.

## Decision checklist for a fresh project

When the project is new and no docs exist yet, work down this list:

1. Always: `README.md`, `LICENSE`
2. If anyone outside the author may contribute: add `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
3. If the project handles credentials, processes user data, exposes a network surface, or might receive vulnerability reports: add `SECURITY.md`. See `security/writing-vdp-and-coordinated-disclosure` for the template
4. If the project ships releases with meaningful changes per release: add `CHANGELOG.md`. See `workflow/writing-release-notes-as-postmortem` for the per-release template
5. If the README is exceeding the target reading time (5 minutes for sections 1-3 by default), start a `docs/` directory and move material out
6. If `docs/` accumulates more than four or five files, adopt the Diataxis split

The order matters. Most projects need (1) and (2) on day one, (3) when the project goes public, (4) at the first release, (5) when the README becomes unwieldy, and (6) when `docs/` itself becomes unwieldy. Skip steps until the project earns them; over-scaffolding day-one docs is its own failure mode.

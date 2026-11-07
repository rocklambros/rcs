# Codex Skill Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A repeatable tool in RCS that builds 14 skills into `~/.codex/skills/` from declared sources, carries hand adaptations as data, and reports drift on demand, so the ChatGPT app's Codex loads them.

**Architecture:** A small package `tools/codex_port/` with one module per concern (manifest, sources, transform, patching, validate, install) and a `pipeline` module that runs them in order for one skill: materialize source, transform, apply patch, validate, install atomically with a sidecar hash record. A thin click CLI at `tools/port_to_codex.py` exposes `build`, `check`, `diff`, and `capture`. Hand adaptations live under `tools/codex_port/` as a TOML manifest, per-skill Markdown notes, and per-skill unified-diff patches, with a gitignored `local/` overlay for the private skill.

**Tech Stack:** Python 3.11+ (RCS venv is 3.13), `click`, `pyyaml`, stdlib `tomllib`, `zipfile`, `hashlib`, `subprocess` for `git apply` and Codex's `quick_validate.py`. Tests with `pytest` via `uv run`.

**Spec:** `docs/superpowers/specs/2026-11-06-codex-skill-port-design.md`

## Global Constraints

- Python `>=3.11`, dependencies already in `pyproject.toml` (`click`, `pyyaml`, `pytest`). No new dependencies.
- Every new file starts with a module docstring naming purpose, version `0.1.0`, and owner Rock Lambros. Comments explain why, never what.
- American English, active voice, no em dashes or semicolons in prose, no AI filler. No AI attribution anywhere (hook-enforced).
- Codex validator rules: top-level frontmatter keys limited to `name`, `description`, `license`, `allowed-tools`, `metadata`. `name` matches `^[a-z0-9-]+$`, at most 64 chars, equals the directory name. `description` is a string, at most 1024 chars, no `<` or `>`. `agents/openai.yaml` `interface.short_description` is 25 to 64 chars.
- The tool writes only under `codex_home` (default `~/.codex`) and never touches `<codex_home>/skills/.system`. It never writes into the RCS tree except through `capture`, which writes one patch file.
- No build timestamps in `SKILL.md`. Two builds from unchanged sources produce byte-identical installed trees.
- Descriptions are never edited by the tool.
- Tests never read or write the real home directory. Every path comes from `tmp_path`.
- Commits go on `feature/codex-port`. No push.

## Review Focus

1. The target `<codex_home>/skills/<name>` is a symlink. Expected: the gate refuses and nothing is deleted through the link. Test in Task 7.
2. A zip or directory source whose top-level folder name differs from the manifest entry name. Expected: that skill fails with a message naming both names, nothing installed. Test in Task 2.
3. A September copy that carries `metadata.ported-from` but no sidecar. Expected: `build` overwrites it, `check` reports it as `legacy` and non-zero so the first build is prompted. Test in Task 7.
4. `--only` names a skill not in the manifest. Expected: exit 2, the unknown name in the message, no file written. Test in Task 8.
5. A source directory reached through a symlink (the way `~/.claude/skills` reaches RCS). Expected: materialize follows it and the hash covers the real content. Test in Task 2.

---

## File structure

| Path | Responsibility |
|---|---|
| `tools/port_to_codex.py` | click CLI. Parses flags, loads the manifest, calls `pipeline`, prints reports, sets exit codes. No logic. |
| `tools/codex_port/__init__.py` | Empty package marker. |
| `tools/codex_port/manifest.py` | TOML loading, overlay merge, entry validation, dataclasses other modules consume. |
| `tools/codex_port/sources.py` | Turn a `SourceSpec` into a directory on disk. Tree hashing. Zip extraction with traversal guard. |
| `tools/codex_port/transform.py` | Frontmatter normalization, sibling-reference rewrite, path-token rewrite, runtime-notes append, `agents/openai.yaml` writer. |
| `tools/codex_port/patching.py` | `git apply` check and apply, patch capture between two trees. |
| `tools/codex_port/validate.py` | Built-in Codex rules and the subprocess call to Codex's `quick_validate.py`. |
| `tools/codex_port/install.py` | Sidecar read and write, overwrite gate, atomic swap, per-skill check report. |
| `tools/codex_port/pipeline.py` | `build_skill` and `check_skill`: the ordered calls across the modules above. |
| `tools/codex_port/manifest.toml` | Tracked manifest, 13 public skills. |
| `tools/codex_port/notes/_default.md`, `notes/<name>.md` | Runtime-notes bodies. |
| `tools/codex_port/patches/<name>.patch` | Hand adaptations as unified diffs. |
| `tools/codex_port/local/` | Gitignored overlay: `manifest.toml`, `notes/`, `patches/` for `brutal-grader`. |
| `tools/tests/codex_port_fixtures.py` | Helpers that build synthetic skills, zips, and manifests under `tmp_path`. |
| `tools/tests/test_codex_port_<module>.py` | One test file per module, plus `test_port_to_codex_cli.py`. |

## Shared types (defined in Task 1, used everywhere)

```python
@dataclass(frozen=True)
class SourceSpec:
    kind: str                      # "rcs" | "claude_ai" | "zip" | "dir"
    track: str | None = None       # rcs
    profile: str | None = None     # claude_ai
    path: Path | None = None       # zip, dir (expanded, absolute)

    def label(self, name: str) -> str:
        # Stable provenance string written to metadata.ported-from and the sidecar.
        # "rcs:workflow/<name>" | "claude.ai:<profile>/<name>" | "zip:~/..." | "dir:~/..."

@dataclass(frozen=True)
class SkillEntry:
    name: str
    source: SourceSpec
    display_name: str
    short_description: str
    default_prompt: str
    path_tokens: bool = False

@dataclass(frozen=True)
class Manifest:
    codex_home: Path
    cache_roots: dict[str, Path]
    rcs_root: Path
    skills: dict[str, SkillEntry]   # insertion order preserved
    data_dirs: tuple[Path, ...]     # directories searched for notes/ and patches/, local first
```

Manifest TOML shape, same for tracked and overlay files:

```toml
[defaults]
codex_home = "~/.codex"
rcs_root = "~/github_projects/RCS/skills"
[defaults.cache_roots]
Claude = "~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"
Claude-Zenity = "~/Library/Application Support/Claude-Zenity/local-agent-mode-sessions/skills-plugin"

[skills.writing-successor-primers]
source = { kind = "rcs", track = "workflow" }
display_name = "Writing Successor Primers"
short_description = "Hand-off primer that carries founding context forward"
default_prompt = "Use $writing-successor-primers to write a successor primer for this project."

[skills.defensible-premortem]
source = { kind = "claude_ai", profile = "Claude-Zenity" }
...
[skills.coffee-peer-voice]
source = { kind = "zip", path = "~/Library/CloudStorage/OneDrive-RockCyber/Templates/Prompts/coffee-peer-voice-portable.zip" }
path_tokens = true
...
```

Sidecar `<skills_root>/<name>/.rcs-port.json`:

```json
{"schema": 1, "name": "...", "source": "<SourceSpec.label>", "source_sha256": "...", "output_sha256": "...", "ported_on": "YYYY-MM-DD"}
```

`output_sha256` covers the installed tree minus the sidecar. `ported_on` equals `metadata.ported-to-codex` in the installed `SKILL.md`.

---

### Task 1: Manifest loading and overlay merge

**Files:**
- Create: `tools/codex_port/__init__.py`, `tools/codex_port/manifest.py`
- Create: `tools/tests/codex_port_fixtures.py`, `tools/tests/test_codex_port_manifest.py`

**Interfaces:**
- Produces: the dataclasses above and `load_manifest(tracked: Path, local: Path | None) -> Manifest`, raising `ManifestError(str)` on any problem. `ManifestError` is the one exception type the CLI maps to exit 2.

- [ ] **Step 1: Write the fixture helpers** in `tools/tests/codex_port_fixtures.py`: `write_manifest(path: Path, defaults: dict, skills: dict) -> Path` that serializes the dict shape above as TOML text (hand-format, no TOML writer dependency), and `entry(name, source: dict, **picker) -> dict` that fills `display_name`, `short_description` (a 30-char default), and `default_prompt` (`f"Use ${name} to do the thing."`) unless overridden.

- [ ] **Step 2: Write the failing tests**

```python
def test_loads_tracked_manifest(tmp_path):
    m = load_manifest(write_manifest(tmp_path / "m.toml", defaults_for(tmp_path), {"a-skill": entry("a-skill", {"kind": "rcs", "track": "workflow"})}), None)
    assert m.skills["a-skill"].source.label("a-skill") == "rcs:workflow/a-skill"
    assert m.codex_home == tmp_path / "codex"            # expanded and absolute
    assert m.data_dirs == ((tmp_path / "m.toml").parent,)  # tracked dir only

def test_local_overlay_adds_and_overrides(tmp_path):
    # overlay adds "private-skill" and changes a-skill's display_name; data_dirs lists local dir first
def test_missing_required_picker_field_raises(tmp_path):   # ManifestError names skill and field
def test_short_description_length_enforced(tmp_path):      # 24 chars raises, 25 and 64 pass, 65 raises
def test_unknown_source_kind_raises(tmp_path)
def test_claude_ai_profile_must_exist_in_cache_roots(tmp_path)
def test_skill_name_must_match_codex_rules(tmp_path):      # "Bad_Name" raises, 65 chars raises
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run python -m pytest tools/tests/test_codex_port_manifest.py -v`
Expected: FAIL with `ModuleNotFoundError: tools.codex_port`

- [ ] **Step 4: Implement `tools/codex_port/manifest.py`**: the dataclasses, `ManifestError`, `load_manifest`. Overlay merge: `[defaults]` keys from local replace tracked keys, `[skills.*]` entries from local replace same-named tracked entries and append new ones. Paths pass through `Path(...).expanduser().resolve()`. Validate per entry: required `display_name`, `short_description` (25 to 64 chars), `default_prompt`, source kind in the four, `track` present for `rcs`, `profile` present and a key of `cache_roots` for `claude_ai`, `path` present for `zip` and `dir`, name matches `^[a-z0-9-]+$` and `len <= 64`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run python -m pytest tools/tests/test_codex_port_manifest.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tools/codex_port/__init__.py tools/codex_port/manifest.py tools/tests/codex_port_fixtures.py tools/tests/test_codex_port_manifest.py
git commit -m "Add Codex port manifest loader with local overlay"
```

---

### Task 2: Source materialization and tree hashing

**Files:**
- Create: `tools/codex_port/sources.py`, `tools/tests/test_codex_port_sources.py`
- Modify: `tools/tests/codex_port_fixtures.py` (add `make_skill_dir(root, name, skill_md: str, extra: dict[str, str] = {}) -> Path` and `make_zip(path, top_folder, files: dict[str, str]) -> Path`)

**Interfaces:**
- Consumes: `SourceSpec`, `Manifest` from Task 1.
- Produces: `materialize(spec: SourceSpec, name: str, manifest: Manifest, dest: Path) -> Path` (copies the source skill tree into `dest/<name>` and returns it), `tree_sha256(root: Path) -> str`, `resolve_cache_dir(cache_root: Path, name: str) -> Path`, `SourceError(str)`. `IGNORED_NAMES = frozenset({"__pycache__", ".DS_Store"})` and any name starting with `.` is skipped by both copy and hash. `tree_sha256` hashes, in sorted order, each relative POSIX path and the file bytes, so a rename changes the hash.

- [ ] **Step 1: Write the failing tests**

```python
def test_rcs_source_copies_track_dir(tmp_path)          # rcs_root/workflow/a-skill/SKILL.md lands at dest/a-skill/SKILL.md
def test_dir_source_follows_symlinked_root(tmp_path)    # Review Focus 5: a symlink to the real dir works and hash equals the real dir's hash
def test_claude_ai_picks_newest_match(tmp_path)         # two <uuid>/<uuid>/skills/a-skill copies, older mtime set with os.utime, newest wins
def test_claude_ai_missing_raises(tmp_path)
def test_zip_extracts_single_top_folder(tmp_path)
def test_zip_top_folder_must_equal_name(tmp_path)       # Review Focus 2: folder "other" vs name "a-skill" raises SourceError naming both
def test_dir_basename_must_equal_name(tmp_path)         # Review Focus 2 for dir kind
def test_zip_rejects_path_traversal(tmp_path)           # member "a-skill/../../evil.txt" raises SourceError, nothing written outside dest
def test_ignored_names_not_copied_or_hashed(tmp_path)   # __pycache__/x.pyc and .DS_Store absent from dest, hash unchanged by adding them
def test_tree_sha256_changes_on_rename(tmp_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tools/tests/test_codex_port_sources.py -v`
Expected: FAIL with `ModuleNotFoundError: tools.codex_port.sources`

- [ ] **Step 3: Implement `tools/codex_port/sources.py`**. `materialize` dispatches on `spec.kind`. Copy with `shutil.copytree(src, dst, symlinks=False, ignore=...)`. For `zip`, open with `zipfile.ZipFile`, reject any member whose `(dest / member).resolve()` is not under `dest.resolve()`, require exactly one top-level folder. `resolve_cache_dir` globs `*/*/skills/<name>/SKILL.md` under the profile root and returns the parent of the newest by `st_mtime`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tools/tests/test_codex_port_sources.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/codex_port/sources.py tools/tests/codex_port_fixtures.py tools/tests/test_codex_port_sources.py
git commit -m "Add Codex port source materialization and tree hashing"
```

---

### Task 3: Frontmatter normalization

**Files:**
- Create: `tools/codex_port/transform.py`, `tools/tests/test_codex_port_transform.py`

**Interfaces:**
- Consumes: `parse_frontmatter(text) -> tuple[dict | None, list[LintError]]` from `tools/lint_frontmatter.py` (reuse, do not reimplement).
- Produces: `normalize_frontmatter(text: str, ported_from: str, ported_on: str) -> str` and `TransformError(str)`. `ALLOWED_TOP_LEVEL = ("name", "description", "license", "allowed-tools", "metadata")`.

- [ ] **Step 1: Add two constants to `tools/tests/codex_port_fixtures.py`**: `RCS_SKILL_MD` (frontmatter with `name: a-skill`, a one-line description, and the six RCS fields `version`, `status`, `track: workflow`, `audience: [skill-author]`, `evidence: [RCS]`, `last-updated: 2026-05-24`, then a body containing `` `workflow/other-skill` ``) and `CLAUDE_SKILL_MD` (frontmatter with `name`, `description`, `version: 0.1 (draft)`, `owner: Rock`, and a body containing `python3 -I SKILL_DIR/scripts/l.py` and `python3 -I SKILLS/a-skill/scripts/x.py`).

- [ ] **Step 2: Write the failing tests**

```python
def test_rcs_fields_nest_under_metadata():
    out = normalize_frontmatter(RCS_SKILL_MD, "rcs:workflow/a-skill", "2026-11-06")
    fm, _ = parse_frontmatter(out)
    assert set(fm) == {"name", "description", "metadata"}
    assert fm["metadata"]["track"] == "workflow"
    assert fm["metadata"]["audience"] == ["skill-author"]
    assert fm["metadata"]["ported-from"] == "rcs:workflow/a-skill"
    assert fm["metadata"]["ported-to-codex"] == "2026-11-06"

def test_existing_metadata_merges_not_replaced()        # source has metadata.owner, result keeps owner and adds ported-from
def test_allowed_keys_stay_top_level()                  # license and allowed-tools untouched
def test_body_is_byte_identical()                       # everything after the closing --- unchanged
def test_unparseable_frontmatter_raises_with_parser_message()   # unquoted "a: b: c" description raises TransformError containing "mapping values"
def test_description_is_not_touched()                   # 1030-char description passes through unchanged (validation is Task 5's job)
def test_output_is_stable():                            # normalize(normalize(x)) == normalize(x)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run python -m pytest tools/tests/test_codex_port_transform.py -v`
Expected: FAIL with `ImportError: cannot import name 'normalize_frontmatter'`

- [ ] **Step 4: Implement `normalize_frontmatter`** in `tools/codex_port/transform.py`. Serialize with `yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1_000_000)` so long descriptions stay on one line and reorderings do not churn. Key order: `name`, `description`, then any other allowed keys in source order, then `metadata` with source metadata keys first, moved keys next in source order, `ported-from` and `ported-to-codex` last.

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run python -m pytest tools/tests/test_codex_port_transform.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tools/codex_port/transform.py tools/tests/codex_port_fixtures.py tools/tests/test_codex_port_transform.py
git commit -m "Add Codex port frontmatter normalization"
```

---

### Task 4: Body rewrites and runtime notes

**Files:**
- Modify: `tools/codex_port/transform.py`
- Modify: `tools/tests/test_codex_port_transform.py`

**Interfaces:**
- Produces: `rewrite_sibling_refs(text: str) -> str`, `rewrite_path_tokens(text: str, skills_root: Path, name: str) -> str`, `append_runtime_notes(text: str, notes_body: str) -> str`, `load_notes(name: str, data_dirs: tuple[Path, ...]) -> str` (first `notes/<name>.md` found across `data_dirs`, else first `notes/_default.md`, else `TransformError`), and `transform_tree(skill_dir: Path, entry: SkillEntry, manifest: Manifest, ported_on: str) -> None` which applies normalization to `SKILL.md`, sibling and token rewrites to every `*.md` under `skill_dir`, and appends the notes to `SKILL.md`.
- `SIBLING_REF = re.compile(r"`(workflow|claude-code-meta|ml-datasci|security|teaching)/([a-z0-9-]+)`")`, replacement `` `$\2` ``.
- Token rewrite replaces `SKILL_DIR/` with `<skills_root>/<name>/` and `SKILLS/` with `<skills_root>/`, where `skills_root = manifest.codex_home / "skills"` as an absolute POSIX string. Only the slash-suffixed forms are rewritten, so prose mentions such as `` `SKILLS` `` survive for a patch to handle.
- Runtime notes section text is exactly: `"\n## Codex runtime notes\n\n" + notes_body.rstrip("\n") + "\n"`, appended once. A `SKILL.md` that already contains `## Codex runtime notes` raises `TransformError`.

- [ ] **Step 1: Write the failing tests**

```python
def test_sibling_refs_rewritten():     "`workflow/a` and `security/b` (planned)" -> "`$a` and `$b` (planned)"
def test_non_sibling_backticks_untouched():    "`scripts/x.py`" and "`workflow/`" unchanged
def test_path_tokens_rewritten(tmp_path):      "python3 -I SKILL_DIR/scripts/l.py" -> f"python3 -I {root}/a-skill/scripts/l.py"; "SKILLS/a-skill/scripts/x.py" -> f"{root}/a-skill/scripts/x.py"; "`SKILLS` stands for" unchanged
def test_notes_appended_once_with_exact_heading()
def test_notes_refuse_double_append()
def test_load_notes_prefers_local_then_named_then_default(tmp_path)
def test_transform_tree_touches_all_markdown(tmp_path)   # references/x.md sibling ref rewritten, scripts/x.py untouched, tokens only when entry.path_tokens
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tools/tests/test_codex_port_transform.py -v`
Expected: FAIL with `ImportError` for the new names

- [ ] **Step 3: Implement the four functions and `transform_tree`** in `tools/codex_port/transform.py`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tools/tests/test_codex_port_transform.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/codex_port/transform.py tools/tests/test_codex_port_transform.py
git commit -m "Add Codex port body rewrites and runtime notes"
```

---

### Task 5: Picker file and validation

**Files:**
- Create: `tools/codex_port/validate.py`, `tools/tests/test_codex_port_validate.py`
- Modify: `tools/codex_port/transform.py` (add `write_picker`)

**Interfaces:**
- Produces in `transform.py`: `write_picker(skill_dir: Path, entry: SkillEntry) -> Path` writing `agents/openai.yaml` with exactly the three `interface` keys `display_name`, `short_description`, `default_prompt`, double-quoted values, in that order (matches the September files byte for byte when values match).
- Produces in `validate.py`: `builtin_validate(skill_dir: Path) -> list[str]` (empty list means valid), `find_codex_validator(codex_home: Path) -> Path | None` returning `<codex_home>/skills/.system/skill-creator/scripts/quick_validate.py` when it exists, `run_codex_validator(validator: Path, skill_dir: Path) -> tuple[bool, str]` using `subprocess.run([sys.executable, str(validator), str(skill_dir)], capture_output=True, text=True)`, `ToolchainError(str)` raised when the validator's return code is non-zero and its stderr contains `ModuleNotFoundError` or `ImportError`, and `validate_skill(skill_dir: Path, codex_home: Path) -> list[str]` that runs built-in rules first and the Codex validator second when present.
- Built-in rules: top-level keys subset of `ALLOWED_TOP_LEVEL`, `name` matches `^[a-z0-9-]+$` and `len <= 64` and equals `skill_dir.name`, `description` is a `str` with `len <= 1024` and no `<` or `>`, `agents/openai.yaml` exists and its `short_description` is 25 to 64 chars.

- [ ] **Step 1: Write the failing tests**

```python
def test_write_picker_matches_expected_bytes(tmp_path)
def test_builtin_accepts_valid_skill(tmp_path)
def test_builtin_rejects_each_rule(tmp_path):   # parametrize: extra top key, bad name, name != dir, 1025-char description, "<" in description, short_description 24 and 65
def test_description_exactly_1024_passes(tmp_path)
def test_find_codex_validator_none_when_absent(tmp_path)
def test_run_codex_validator_uses_sys_executable(tmp_path, monkeypatch):   # fake validator script that prints sys.executable, assert equal
def test_import_error_raises_toolchain_error(tmp_path):   # fake validator that exits 1 with "ModuleNotFoundError: No module named 'yaml'" on stderr
def test_validate_skill_runs_codex_validator_when_present(tmp_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tools/tests/test_codex_port_validate.py -v`
Expected: FAIL with `ModuleNotFoundError: tools.codex_port.validate`

- [ ] **Step 3: Implement `write_picker` and `tools/codex_port/validate.py`.**

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tools/tests/test_codex_port_validate.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/codex_port/transform.py tools/codex_port/validate.py tools/tests/test_codex_port_validate.py
git commit -m "Add Codex port picker writer and validation"
```

---

### Task 6: Patching

**Files:**
- Create: `tools/codex_port/patching.py`, `tools/tests/test_codex_port_patching.py`

**Interfaces:**
- Produces: `find_patch(name: str, data_dirs: tuple[Path, ...]) -> Path | None` (first `patches/<name>.patch` across `data_dirs`), `check_patch(tree: Path, patch: Path) -> PatchResult`, `apply_patch(tree: Path, patch: Path) -> PatchResult`, `capture_patch(generated: Path, installed: Path, out: Path) -> int` (returns number of changed files, writes nothing when zero), `PatchResult(ok: bool, output: str)`.
- `check_patch` runs `["git", "apply", "--check", str(patch)]` with `cwd=tree`. `apply_patch` runs the same without `--check`. Patches use `a/<rel>` and `b/<rel>` prefixes relative to the skill directory. `capture_patch` runs `["git", "diff", "--no-index", "--no-color", "s", "t"]` from a temporary parent holding copies named `s` (generated) and `t` (installed), then rewrites header paths `a/s/` to `a/` and `b/t/` to `b/`. Excluded from capture and from the copies: `.rcs-port.json`, `agents/openai.yaml`, `__pycache__`, dotfiles.

- [ ] **Step 1: Write the failing tests**

```python
def test_apply_patch_changes_file(tmp_path)
def test_check_patch_reports_rejected_hunk_without_writing(tmp_path)   # context changed, ok False, output names SKILL.md, file bytes unchanged
def test_patch_applies_with_line_offset(tmp_path)                       # lines inserted above the hunk, still applies
def test_capture_patch_roundtrips(tmp_path)                             # capture s->t, apply to fresh copy of s, tree equals t
def test_capture_excludes_generated_files(tmp_path)                     # differing agents/openai.yaml and .rcs-port.json produce no hunks
def test_capture_returns_zero_and_writes_nothing_when_identical(tmp_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tools/tests/test_codex_port_patching.py -v`
Expected: FAIL with `ModuleNotFoundError: tools.codex_port.patching`

- [ ] **Step 3: Implement `tools/codex_port/patching.py`.** All subprocess calls take argument lists, never a shell string.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tools/tests/test_codex_port_patching.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/codex_port/patching.py tools/tests/test_codex_port_patching.py
git commit -m "Add Codex port patch apply and capture"
```

---

### Task 7: Install, sidecar, gate, and check

**Files:**
- Create: `tools/codex_port/install.py`, `tools/tests/test_codex_port_install.py`
- Modify: `docs/superpowers/specs/2026-11-06-codex-skill-port-design.md` D5 (one sentence, see Step 3)

**Interfaces:**
- Produces: `SIDECAR = ".rcs-port.json"`, `Sidecar` dataclass with the six fields from the shared types, `read_sidecar(skill_dir) -> Sidecar | None`, `write_sidecar(skill_dir, sidecar) -> None`, `installed_sha256(skill_dir) -> str` (= `tree_sha256` with the sidecar excluded), `Gate` enum `ABSENT | PORTED_LEGACY | PORTED_CLEAN | PORTED_EDITED | FOREIGN | SYMLINK | SYSTEM`, `gate(target: Path) -> Gate`, `install(stage: Path, target: Path, force: bool) -> Gate` (raises `InstallError(str)` for `FOREIGN`, `SYMLINK`, `SYSTEM`, and for `PORTED_EDITED` without `force`), `stage_root(codex_home) -> Path` = `<codex_home>/.rcs-port-stage`, `CheckStatus` enum `OK | NOT_INSTALLED | LEGACY | STALE_SOURCE | PATCH_FAILS | EDITED | MISSING_SOURCE | INVALID`, `CheckReport(name, status, details: str, info: list[str])`.
- `gate`: `SYSTEM` when `target.name == ".system"`, `SYMLINK` when `target.is_symlink()`, `ABSENT` when missing, `FOREIGN` when `SKILL.md` lacks `metadata.ported-from`, `PORTED_LEGACY` when ported-from present and no sidecar, `PORTED_CLEAN` when sidecar `output_sha256 == installed_sha256(target)`, else `PORTED_EDITED`.
- `install` swaps atomically: rename existing target to `<stage_root>/<name>.old`, rename stage to target, remove `.old`. If the second rename fails, rename `.old` back and re-raise.

- [ ] **Step 1: Write the failing tests**

```python
def test_sidecar_roundtrip(tmp_path)
def test_installed_sha256_ignores_sidecar(tmp_path)
def test_gate_absent_foreign_legacy_clean_edited(tmp_path)   # parametrize over five prepared targets
def test_gate_symlink_refused_and_link_target_intact(tmp_path)   # Review Focus 1
def test_gate_system_refused(tmp_path)
def test_install_replaces_legacy_copy(tmp_path)              # Review Focus 3
def test_install_refuses_edited_without_force_and_allows_with_force(tmp_path)
def test_install_rolls_back_when_swap_fails(tmp_path, monkeypatch)   # monkeypatch os.replace to fail on the second call, target bytes unchanged, no .old left behind
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tools/tests/test_codex_port_install.py -v`
Expected: FAIL with `ModuleNotFoundError: tools.codex_port.install`

- [ ] **Step 3: Implement `tools/codex_port/install.py`.** Then amend spec D5: replace "stages into a temporary directory under `~/.codex/skills/`" with "stages into `~/.codex/.rcs-port-stage/`, outside the skills root, because Codex globs every `~/.codex/skills/*/SKILL.md` and would load a half-built stage". Same volume, so the rename stays atomic.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tools/tests/test_codex_port_install.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/codex_port/install.py tools/tests/test_codex_port_install.py docs/superpowers/specs/2026-11-06-codex-skill-port-design.md
git commit -m "Add Codex port install gate, sidecar, and atomic swap"
```

---

### Task 8: Pipeline and CLI

**Files:**
- Create: `tools/codex_port/pipeline.py`, `tools/port_to_codex.py`, `tools/tests/test_codex_port_pipeline.py`, `tools/tests/test_port_to_codex_cli.py`
- Modify: `.gitignore` (append after line 40: `tools/codex_port/local/` under the "Private skills" comment)

**Interfaces:**
- Produces in `pipeline.py`: `BuildResult(name, ok: bool, gate: Gate | None, message: str)`, `build_skill(entry: SkillEntry, manifest: Manifest, force: bool, today: str) -> BuildResult`, `check_skill(entry, manifest, today) -> CheckReport`, `diff_skill(entry, manifest, today) -> str`.
- `build_skill` order: materialize into `stage_root/<name>` (clearing any leftover first), `source_sha = tree_sha256(stage)`, read the installed sidecar, `ported_on = sidecar.ported_on if sidecar and sidecar.source_sha256 == source_sha else today`, `transform_tree`, `write_picker`, apply patch if `find_patch` returns one (a failing patch is a `BuildResult(ok=False)` and the stage is removed), `validate_skill` (non-empty list is `ok=False`), write sidecar with `output_sha256 = installed_sha256(stage)`, `install`. A `ToolchainError` propagates out of `build_skill` so the CLI aborts the whole run.
- `check_skill` never writes under `skills/`: it materializes and transforms into `stage_root/<name>.check`, computes the would-be output hash, and reports `MISSING_SOURCE` (SourceError), `NOT_INSTALLED`, `LEGACY`, `EDITED` (installed hash differs from sidecar), `STALE_SOURCE` (sidecar source hash differs), `PATCH_FAILS` (`check_patch` not ok), `INVALID` (validate_skill non-empty), else `OK`. For `claude_ai` sources it appends an info line when another profile in `cache_roots` holds a copy whose `tree_sha256` differs.
- CLI (`tools/port_to_codex.py`, `click.group`): options on the group `--manifest` (default `tools/codex_port/manifest.toml`), `--local-manifest` (default `tools/codex_port/local/manifest.toml`, used only if it exists), `--codex-home` (overrides manifest). Commands: `build [--only NAME]... [--force]`, `check [--only NAME]...`, `diff NAME`, `capture NAME` (writes `patches/<NAME>.patch` into the first `data_dirs` entry that already holds that skill's notes, else the tracked dir). One line per skill on stdout: `<name>  <status>  <message>`. Exit 0 when every skill is `ok`, 1 when any is not, 2 for `ManifestError` or an unknown `--only` name.

- [ ] **Step 1: Write the failing pipeline tests** (end to end on a synthetic RCS skill and a synthetic zip skill under `tmp_path`)

```python
def test_build_installs_and_writes_sidecar(tmp_path)
def test_second_build_is_byte_identical(tmp_path)           # installed_sha256 equal, ported_on unchanged
def test_source_change_updates_ported_on(tmp_path)          # today="2026-12-01" on second call after editing the source body
def test_failing_patch_leaves_install_untouched(tmp_path)
def test_check_reports_each_status(tmp_path)                 # parametrize: not installed, legacy, stale source, edited, patch fails, missing source
def test_check_adds_profile_info_line(tmp_path)              # two cache roots, different content, info non-empty, status still OK
def test_toolchain_error_propagates(tmp_path)
```

- [ ] **Step 2: Write the failing CLI tests** with `click.testing.CliRunner`

```python
def test_build_exit_codes(tmp_path)              # all ok -> 0, one failing patch -> 1
def test_only_unknown_name_exits_2_and_writes_nothing(tmp_path)   # Review Focus 4
def test_check_exit_1_when_stale(tmp_path)
def test_capture_writes_patch_file(tmp_path)
def test_local_manifest_used_only_when_present(tmp_path)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run python -m pytest tools/tests/test_codex_port_pipeline.py tools/tests/test_port_to_codex_cli.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 4: Implement `tools/codex_port/pipeline.py` and `tools/port_to_codex.py`, append the `.gitignore` line.**

- [ ] **Step 5: Run the whole suite**

Run: `uv run python -m pytest tools/tests -q`
Expected: all tests pass, including the pre-existing lint tests

- [ ] **Step 6: Commit**

```bash
git add tools/codex_port/pipeline.py tools/port_to_codex.py tools/tests/test_codex_port_pipeline.py tools/tests/test_port_to_codex_cli.py .gitignore
git commit -m "Add Codex port pipeline and CLI"
```

---

### Task 9: Port data: manifest, notes, patches

**Files:**
- Create: `tools/codex_port/manifest.toml`, `tools/codex_port/notes/_default.md`, `tools/codex_port/notes/<name>.md` for the skills listed below, `tools/codex_port/patches/<name>.patch` as produced
- Create (gitignored): `tools/codex_port/local/manifest.toml`, `tools/codex_port/local/notes/brutal-grader.md`, `tools/codex_port/local/patches/brutal-grader.patch`

**Interfaces:**
- Consumes: the CLI from Task 8.

- [ ] **Step 1: Write `manifest.toml`** with the `[defaults]` block from the shared types and 13 entries. Sources: `rcs` with track `workflow` for `adversarial-premortem-complete`, `adversarial-premortem-single`, `writing-release-notes-as-postmortem`, `writing-repo-documentation`, `writing-successor-primers`; `rcs` track `teaching` for `writing-onboarding-guide`; `rcs` track `security` for `writing-vdp-and-coordinated-disclosure`; `rcs` track `claude-code-meta` for `authoring-skill`; `claude_ai` profile `Claude` for `adversarial-premortem`; `claude_ai` profile `Claude-Zenity` for `defensible-premortem` and `clean-user-facing-text`; `zip` for `coffee-peer-voice` and `anti-ai-slop` at the OneDrive `-portable.zip` paths. `path_tokens = true` for `coffee-peer-voice`, `anti-ai-slop`, `clean-user-facing-text`. Picker text for the eleven existing skills copied verbatim from their current `~/.codex/skills/<name>/agents/openai.yaml`. New picker text: `anti-ai-slop` ("Anti AI Slop", "Audit text for machine-writing tells and strip them", "Use $anti-ai-slop to audit this text for AI tells and strip them."), `clean-user-facing-text` ("Clean User-Facing Text", "Audit hidden Unicode and finalize prose for readers", "Use $clean-user-facing-text to audit and finalize this text before it ships."), `defensible-premortem` ("Defensible Premortem", "Verify claims against sources and stress-test the answer", "Use $defensible-premortem to verify this answer and tell me whether it can be defended.").

- [ ] **Step 2: Write `local/manifest.toml`** with only `[skills.brutal-grader]` (`rcs`, track `teaching`, picker text from the existing `openai.yaml`).

- [ ] **Step 3: Write the notes.** `_default.md` holds the sibling-skill sentence from the September writing-family block. `notes/adversarial-premortem.md`, `adversarial-premortem-single.md`, `adversarial-premortem-complete.md`, `defensible-premortem.md`, and `local/notes/brutal-grader.md` hold the September subagent-family block (five bullets). `notes/authoring-skill.md` and `notes/writing-repo-documentation.md` hold their September bespoke blocks. `notes/coffee-peer-voice.md`, `anti-ai-slop.md`, `clean-user-facing-text.md` hold a voice-family block with three bullets: scripts run with `python3 -I` at the absolute paths written in this file, which the port pinned at build time; where the source says Write or Edit tool, use `apply_patch`; where the source mentions Claude Code allow rules, Codex's approval policy applies and the single-command rule still holds. Drop the "Ported from the Claude Code version on <date>" intro line in every note, since `metadata.ported-to-codex` carries the date.

- [ ] **Step 4: Capture the September hand edits as patches.** For each of the eleven existing skills, run `uv run python -m tools.port_to_codex capture <name>`. It builds the mechanical plus notes output and diffs it against the installed copy.

- [ ] **Step 5: Prune each captured patch by hand.** Keep hunks that reword prose for Codex (host names, `AGENTS.md` for `CLAUDE.md`, validator rules, checklist items, inlined house style). Drop hunks that only differ in frontmatter layout, the old runtime-notes block, or `ported-to-codex` dates. Delete `coffee-peer-voice.patch` entirely: the installed 1.2 copy and the 1.18-portable source are different generations. Expected survivors with real content: `authoring-skill`, `writing-repo-documentation`, `adversarial-premortem-complete`, `brutal-grader` (local), and smaller ones for the premortem and writing families. Any patch that ends up empty is deleted.

- [ ] **Step 6: Author the three voice-family patches by hand** against the mechanical output (`uv run python -m tools.port_to_codex diff <name>` shows the current state). `clean-user-facing-text.patch`: replace the sentence that defines `SKILLS` via "the base directory the Skill tool printed" with one sentence saying the paths above are already absolute. `coffee-peer-voice.patch` and `anti-ai-slop.patch`: the sentence "Build every script path from the base directory the Skill tool printed when it loaded this file (SKILL_DIR)" and its counterpart become "The script paths below are absolute". Nothing else changes in those files.

- [ ] **Step 7: Verify every patch applies cleanly**

Run: `uv run python -m tools.port_to_codex check`
Expected: every skill reports `legacy` or `not-installed` (nothing built yet), none report `patch-fails`, `missing-source`, or `invalid`. Exit 1 is expected at this point.

- [ ] **Step 8: Commit the tracked data**

```bash
git add tools/codex_port/manifest.toml tools/codex_port/notes tools/codex_port/patches
git commit -m "Add Codex port manifest, runtime notes, and patches for 13 skills"
git status --porcelain tools/codex_port/local   # expected: empty, the overlay is ignored
```

---

### Task 10: Build, verify, hand off

**Files:**
- None created in the repo. Writes under `~/.codex/skills/` only.

- [ ] **Step 1: Build**

Run: `uv run python -m tools.port_to_codex build`
Expected: 14 lines ending in `ok`, exit 0. The eleven existing copies report gate `PORTED_LEGACY`, the three new ones `ABSENT`.

- [ ] **Step 2: Rebuild and confirm nothing changed**

Run: `uv run python -m tools.port_to_codex build && uv run python -m tools.port_to_codex check`
Expected: both exit 0, every `check` line `ok`.

- [ ] **Step 3: Codex's own validator on every installed skill**

Run: `for d in ~/.codex/skills/*/; do printf '%s ' "$(basename "$d")"; uv run python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d"; done`
Expected: 14 lines each ending `Skill is valid!`

- [ ] **Step 4: Codex sees all 14**

Run: `codex debug prompt-input hello | grep -oE '\(file: r0/[a-z0-9-]+/SKILL\.md\)' | sort -u | wc -l`
Expected: `14`

- [ ] **Step 5: Installed scripts run from their pinned paths**

Run: `uv run python -m pytest -q ~/.codex/skills/anti-ai-slop/tests -p no:cacheprovider`
Expected: pass. Then `grep -rlE 'SKILLS/|SKILL_DIR/|/root/\.claude/' ~/.codex/skills/*/SKILL.md`
Expected: no output.

- [ ] **Step 6: Record the outcome.** Update the work-state list and tell Rock the one remaining verification is his: open a Codex conversation in the ChatGPT app, invoke `$coffee-peer-voice` on a short draft, and confirm the `coffee-peer-voice v1.18-portable loaded` stamp prints.

---

## Self-review notes

Spec coverage: G1 Tasks 5 and 10. G2 Tasks 8 and 10. G3 Tasks 6 and 9. G4 Task 9 zip sources and token pinning in Task 4. G5 Task 7 gate. D1 Tasks 1 and 8 (`.gitignore`). D2 Tasks 3, 4, 6. D3 Task 5 and Task 9. D4 Tasks 7 and 8. D5 Task 7 with the staging-location amendment. D6 Task 5. D7 Task 9 (portable zips unchanged, stamps intact). D8 Tasks 2, 8, 9. D9 Task 2. D10 Task 9. Verification steps 1 to 6 and 8 in Task 10, step 7 handed to Rock. §8 security: argument-list subprocesses in Tasks 5 and 6, traversal guard in Task 2, no network anywhere.

Type consistency: `Gate`, `CheckStatus`, `CheckReport`, `Sidecar` defined in Task 7 and consumed by name in Task 8. `SkillEntry.path_tokens` defined in Task 1, read in Task 4. `tree_sha256` defined in Task 2, wrapped by `installed_sha256` in Task 7.

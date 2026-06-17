#!/usr/bin/env python3
"""
aibom_compliance.py — dynamic AIBOM completeness compliance against the
genai-security-project/aibom-generator evaluator.

The evaluator's required field set and scoring weights change as that repo
evolves, so this tool never hard-codes them. It clones the public repo at
runtime, reads the live field_registry.json, and scores a candidate AIBOM
with the repo's own scorer (calculate_completeness_score). That keeps the
"100%" target faithful to whatever the current evaluator measures.

Subcommands:
  requirements              Print the live field requirements (category, tier,
                            jsonpath) and scoring weights as JSON.
  scaffold OUT.json         Generate a maximal CycloneDX AIBOM populated at
                            every registry jsonpath with <FILL:...> placeholders,
                            then self-score to confirm the structure reaches 100.
  score AIBOM.json          Score a candidate AIBOM with the repo's own scorer.
                            Exit 0 only when total_score == 100.0 and no penalty.

Common flags:
  --repo-url URL   default https://github.com/genai-security-project/aibom-generator
  --ref REF        git ref to pin (branch, tag, or SHA). Default: the repo's
                   default branch HEAD. Pin a reviewed SHA for sensitive use.
  --keep-clone     do not delete the temporary clone (for inspection)

Security note: scoring runs the repo's scorer module (scoring.py + registry.py),
which are pure functions over local files. Review them, or pin --ref to a SHA you
trust, before running in a sensitive environment.
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types

DEFAULT_REPO = "https://github.com/genai-security-project/aibom-generator"
PLACEHOLDER = "<FILL: replace with real model content>"


def clone_repo(repo_url, ref, dest):
    """Shallow-clone the public repo. Pin to ref when given."""
    cmd = ["git", "clone", "--depth", "1"]
    if ref:
        cmd += ["--branch", ref]
    cmd += [repo_url, dest]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit("ERROR: git is not installed; cannot fetch the evaluator repo.")
    except subprocess.CalledProcessError as e:
        # --branch fails on a bare SHA; retry with a full clone + checkout.
        if ref:
            try:
                subprocess.run(["git", "clone", repo_url, dest], check=True,
                               capture_output=True, text=True)
                subprocess.run(["git", "-C", dest, "checkout", ref], check=True,
                               capture_output=True, text=True)
                return
            except subprocess.CalledProcessError as e2:
                sys.exit(f"ERROR: could not clone/checkout {repo_url}@{ref}: {e2.stderr}")
        sys.exit(f"ERROR: could not clone {repo_url}: {e.stderr}")


def load_scorer(src_dir):
    """Load registry.py + scoring.py under a synthetic package, skipping the
    heavy models/__init__.py so no extra dependencies are required for scoring
    with validate=False."""
    def _load(modname, relpath):
        spec = importlib.util.spec_from_file_location(modname, os.path.join(src_dir, relpath))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[modname] = mod
        spec.loader.exec_module(mod)
        return mod

    pkg = types.ModuleType("aibomtool")
    pkg.__path__ = [os.path.join(src_dir, "models")]
    sys.modules["aibomtool"] = pkg
    _load("aibomtool.registry", "models/registry.py")
    scoring = _load("aibomtool.scoring", "models/scoring.py")
    mgr = sys.modules["aibomtool.registry"].get_field_registry_manager()
    return scoring, mgr


def find_registry(src_dir):
    path = os.path.join(src_dir, "models", "field_registry.json")
    if not os.path.exists(path):
        sys.exit(f"ERROR: field_registry.json not found at {path}; repo layout may have changed.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --- AIBOM generation: follow each registry jsonpath and set a value ---------
_FILTER = re.compile(r"^(\w+)\[\?\(@\.(\w+)=='([^']+)'.*\)\](.*)$")
_INDEX = re.compile(r"^(\w+)\[(\d+)\]$")


def _tokenize(path):
    if path.startswith("$."):
        path = path[2:]
    toks, cur, depth = [], "", 0
    for ch in path:
        if ch == "[":
            depth += 1; cur += ch
        elif ch == "]":
            depth -= 1; cur += ch
        elif ch == "." and depth == 0:
            if cur:
                toks.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        toks.append(cur)
    return toks


def _ensure_item(lst, key, val):
    for it in lst:
        if isinstance(it, dict) and it.get(key) == val:
            return it
    it = {key: val}
    lst.append(it)
    return it


def set_path(doc, path, value):
    """Create nested structure for a registry jsonpath and set a leaf value."""
    toks = _tokenize(path)
    cur = doc
    for i, tok in enumerate(toks):
        last = i == len(toks) - 1
        mf, mi = _FILTER.match(tok), _INDEX.match(tok)
        if mf:
            key, fkey, fval, _suffix = mf.groups()
            lst = cur.setdefault(key, [])
            if not isinstance(lst, list):
                lst = cur[key] = []
            item = _ensure_item(lst, fkey, fval)
            if last:
                if fkey == "type":
                    item.setdefault("url", "https://example.com/ref")
                else:
                    item.setdefault("value", value)
            else:
                cur = item
        elif mi:
            key, idx = mi.group(1), int(mi.group(2))
            lst = cur.setdefault(key, [])
            if not isinstance(lst, list):
                lst = cur[key] = []
            while len(lst) <= idx:
                lst.append({})
            if last:
                lst[idx] = value
            else:
                if not isinstance(lst[idx], dict):
                    lst[idx] = {}
                cur = lst[idx]
        else:
            if last:
                cur[tok] = value
            else:
                nxt = cur.get(tok)
                if not isinstance(nxt, dict):
                    nxt = cur[tok] = {}
                cur = nxt


def build_maximal_aibom(registry):
    """Build a CycloneDX AIBOM populated at every registry jsonpath."""
    aibom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": "urn:uuid:00000000-0000-4000-8000-000000000000",
        "version": 1,
        "metadata": {"properties": [], "component": {"externalReferences": []}},
        "components": [{
            "type": "machine-learning-model",
            "name": PLACEHOLDER,
            "version": PLACEHOLDER,
            "purl": PLACEHOLDER,
            "description": PLACEHOLDER,
            "licenses": [{"license": {"id": "MIT"}}],
            "supplier": {"name": PLACEHOLDER},
            "externalReferences": [{"type": "distribution", "url": "https://example.com/dl"}],
            "modelCard": {"modelParameters": {}, "considerations": {}, "properties": []},
        }],
        "component": {
            "type": "machine-learning-model",
            "name": PLACEHOLDER,
            "supplier": {"name": PLACEHOLDER},
            "externalReferences": [{"type": "website", "url": "https://example.com"}],
            "modelCard": {"modelParameters": {}, "considerations": {}, "properties": []},
        },
    }
    aibom["component"]["modelCard"]["modelParameters"]["datasets"] = [
        {"name": PLACEHOLDER, "url": "https://example.com/ds"}
    ]
    for _name, cfg in registry.get("fields", {}).items():
        jp = cfg.get("jsonpath", "")
        if jp:
            set_path(aibom, jp, PLACEHOLDER)
    return aibom


def score(scoring, aibom):
    res = scoring.calculate_completeness_score(aibom, validate=False)
    return res


def cmd_requirements(args, src_dir):
    registry = find_registry(src_dir)
    fields = registry.get("fields", {})
    out = {"field_count": len(fields),
           "scoring_config": registry.get("scoring_config", {}).get("category_weights", {}),
           "fields": {}}
    for name, cfg in fields.items():
        out["fields"][name] = {"category": cfg.get("category"),
                               "tier": cfg.get("tier"),
                               "jsonpath": cfg.get("jsonpath")}
    print(json.dumps(out, indent=2))


def cmd_scaffold(args, src_dir):
    scoring, _mgr = load_scorer(src_dir)
    registry = find_registry(src_dir)
    aibom = build_maximal_aibom(registry)
    res = score(scoring, aibom)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(aibom, f, indent=2)
    print(f"Wrote scaffold to {args.out}")
    print(f"Self-score: {res['total_score']} (penalty_applied={res['penalty_applied']})")
    missing = {k: v for k, v in res["missing_fields"].items() if v}
    if res["total_score"] != 100.0 or missing:
        print("WARNING: scaffold did not reach 100; missing:", json.dumps(missing))
        return 1
    print("Scaffold structure scores 100. Replace every <FILL:...> with real model content.")
    return 0


def cmd_score(args, src_dir):
    scoring, _mgr = load_scorer(src_dir)
    with open(args.aibom, "r", encoding="utf-8") as f:
        aibom = json.load(f)
    res = score(scoring, aibom)
    print(f"total_score: {res['total_score']}")
    print("section_scores:", json.dumps(res["section_scores"]))
    missing = {k: v for k, v in res["missing_fields"].items() if v}
    if missing:
        print("missing_fields:", json.dumps(missing, indent=2))
    if res["penalty_applied"]:
        print("penalty_reason:", res["penalty_reason"])
    ok = res["total_score"] == 100.0 and not res["penalty_applied"]
    print("RESULT:", "PASS (100%)" if ok else "FAIL (<100%)")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo-url", default=DEFAULT_REPO)
    p.add_argument("--ref", default=None, help="git ref to pin (branch/tag/SHA)")
    p.add_argument("--keep-clone", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("requirements")
    sp = sub.add_parser("scaffold"); sp.add_argument("out")
    sp = sub.add_parser("score"); sp.add_argument("aibom")
    args = p.parse_args()

    tmp = tempfile.mkdtemp(prefix="aibom-eval-")
    clone_dir = os.path.join(tmp, "repo")
    rc = 1
    try:
        clone_repo(args.repo_url, args.ref, clone_dir)
        src_dir = os.path.join(clone_dir, "src")
        if not os.path.isdir(src_dir):
            sys.exit(f"ERROR: expected src/ in clone at {src_dir}; repo layout may have changed.")
        if args.command == "requirements":
            cmd_requirements(args, src_dir); rc = 0
        elif args.command == "scaffold":
            rc = cmd_scaffold(args, src_dir)
        elif args.command == "score":
            rc = cmd_score(args, src_dir)
    finally:
        if args.keep_clone:
            print(f"(clone kept at {clone_dir})")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())

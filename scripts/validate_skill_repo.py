#!/usr/bin/env python3
"""Validate the port-skill-collection repository package.

This is intentionally lightweight and dependency-minimal so GitHub Actions can
run it before invoking heavier security tooling.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover - exercised in CI failure mode
    print(f"PyYAML is required: {exc}", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "port-skill-collection"
SKILL_MD = SKILL_DIR / "SKILL.md"
README = ROOT / "README.md"
REQUIRED_FILES = [
    ROOT / "LICENSE",
    README,
    SKILL_MD,
    SKILL_DIR / "LICENSE",
    SKILL_DIR / "references" / "ports-ledger.md",
    SKILL_DIR / "references" / "refresh-mode.md",
    SKILL_DIR / "templates" / "ports.yaml",
]
EXPECTED_INSTALL = "hermes skills install vcolombo/port-skill-collection/skills/port-skill-collection --category migration"
GENERIC_FORBIDDEN_PUBLIC_PATTERNS = [
    r"ghp_[A-Za-z0-9_]+",
    r"sk-[A-Za-z0-9_-]{12,}",
    r"AKIA[0-9A-Z]{16}",
    r"ASIA[0-9A-Z]{16}",
    r"AIza[0-9A-Za-z_-]{35}",
]
PRIVATE_SCRUB_PATTERNS_ENV = "PRIVATE_SCRUB_PATTERNS"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path} must start with YAML frontmatter")
    match = re.search(r"\n---\s*\n", text[4:])
    if match is None:
        fail(f"{path} missing closing YAML frontmatter fence")
        raise AssertionError("unreachable")
    end = 4 + match.start()
    fm_text = text[4:end]
    body = text[4 + match.end() :]
    data = yaml.safe_load(fm_text)
    if not isinstance(data, dict):
        fail(f"{path} frontmatter must parse as a mapping")
    return data, body


def validate_structure() -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            fail(f"required file missing: {path.relative_to(ROOT)}")
    if (ROOT / "SKILL.md").exists():
        fail("root SKILL.md should not exist; use skills/port-skill-collection/SKILL.md")


def validate_skill() -> None:
    frontmatter, body = parse_frontmatter(SKILL_MD)
    if frontmatter.get("name") != "port-skill-collection":
        fail("SKILL.md name must be port-skill-collection")
    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        fail("SKILL.md description is required")
        raise AssertionError("unreachable")
    if len(description) > 1024:
        fail("SKILL.md description exceeds 1024 chars")
    version = frontmatter.get("version")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(version)):
        fail("SKILL.md version must be semver-like, e.g. 2.2.0")
    for phrase in ["ports.yaml", "## Refresh mode", "references/refresh-mode.md", "references/ports-ledger.md"]:
        if phrase not in body:
            fail(f"SKILL.md missing expected phrase: {phrase}")


def validate_readme() -> None:
    text = README.read_text(encoding="utf-8")
    if EXPECTED_INSTALL not in text:
        fail("README does not contain the full-directory install command")
    if "raw.githubusercontent.com/vcolombo/port-skill-collection/main/SKILL.md" in text:
        fail("README still advertises raw SKILL.md install path")
    for phrase in ["ports.yaml", "references/refresh-mode.md", "templates/ports.yaml"]:
        if phrase not in text:
            fail(f"README missing expected phrase: {phrase}")


def validate_ports_template() -> None:
    template_path = SKILL_DIR / "templates" / "ports.yaml"
    data = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("templates/ports.yaml must parse as a mapping")
    ports = data.get("ports")
    if not isinstance(ports, list) or not ports or not isinstance(ports[0], dict):
        fail("templates/ports.yaml must contain a non-empty ports list of mappings")
        raise AssertionError("unreachable")
    required = {"source_repo", "pinned_sha", "pinned_short_sha", "installed_at", "install_method", "adaptations", "skills"}
    missing = required - set(ports[0])
    if missing:
        fail(f"templates/ports.yaml first port missing keys: {sorted(missing)}")


def load_private_scrub_patterns() -> list[str]:
    raw = os.environ.get(PRIVATE_SCRUB_PATTERNS_ENV, "")
    return [line.strip() for line in raw.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def iter_scanned_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return [ROOT / line for line in result.stdout.splitlines() if line]
    except Exception:
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]


def scan_public_strings() -> None:
    files = [p for p in iter_scanned_files() if p.is_file()]
    pattern_sources: list[tuple[str, str]] = [(p, "generic") for p in GENERIC_FORBIDDEN_PUBLIC_PATTERNS]
    pattern_sources.extend((p, "private") for p in load_private_scrub_patterns())

    findings: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern, source in pattern_sources:
            if re.search(pattern, text):
                if source == "private":
                    findings.append(f"{path.relative_to(ROOT)} matched private scrub pattern [redacted]")
                else:
                    findings.append(f"{path.relative_to(ROOT)} matched {pattern!r}")
    if findings:
        fail("public scrub scan failed:\n" + "\n".join(findings))


def run_hermes_skill_guard_if_available() -> None:
    source = os.environ.get("HERMES_AGENT_SOURCE")
    if not source:
        print("HERMES_AGENT_SOURCE not set; skipping Hermes skills_guard integration")
        return
    source_path = Path(source)
    if not (source_path / "tools" / "skills_guard.py").is_file():
        fail(f"HERMES_AGENT_SOURCE does not look like a Hermes source checkout: {source}")
    code = f"""
import sys
from pathlib import Path
sys.path.insert(0, {str(source_path)!r})
from tools.skills_guard import scan_skill, should_allow_install, format_scan_report
result = scan_skill(Path({str(SKILL_DIR)!r}), source='vcolombo/port-skill-collection/skills/port-skill-collection')
print(format_scan_report(result))
allowed, reason = should_allow_install(result, force=False)
print(reason)
if not allowed:
    raise SystemExit(1)
"""
    subprocess.run([sys.executable, "-c", code], check=True)


def main() -> None:
    validate_structure()
    validate_skill()
    validate_readme()
    validate_ports_template()
    scan_public_strings()
    run_hermes_skill_guard_if_available()
    print(json.dumps({"status": "ok", "skill": "port-skill-collection", "path": str(SKILL_MD.relative_to(ROOT))}))


if __name__ == "__main__":
    main()

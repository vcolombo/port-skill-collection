# port-skill-collection

Hermes Agent skill for safely porting external `SKILL.md` collections into a Hermes active-profile skills tree.

## What it does

This skill provides a reusable workflow for importing Claude Code plugins, agentskills-style repositories, Codex/OpenCode/Cursor skill collections, or other GitHub repositories of `SKILL.md` directories into Hermes Agent.

Key safeguards:

- resolve the active Hermes profile skills root instead of assuming shell `~/.hermes/skills`;
- pin the source repository commit before copying;
- preserve upstream license/NOTICE files;
- preserve the original upstream `SKILL.md` as `references/original-SKILL.md`;
- hard-gate large collections: if a source has more than 3 skills, inventory first, estimate per-session index cost, and wait for user subset selection before installing;
- quote YAML date/timestamp-like generated metadata values so `skill_view` serialization does not break.

## Install into Hermes

Copy this directory into an active Hermes profile skills root, for example:

```bash
export HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
mkdir -p "$HERMES_HOME/skills/migration/port-skill-collection"
cp SKILL.md "$HERMES_HOME/skills/migration/port-skill-collection/SKILL.md"
```

Then verify in a fresh Hermes process/session:

```bash
hermes --skills port-skill-collection chat -q 'Return exactly: loaded' --toolsets safe -Q
```

Installed skills appear in new sessions after prompt/cache refresh.

## Repository contents

- `SKILL.md` — the Hermes skill.
- `README.md` — this public installation note.

## Public-release hygiene

This repository intentionally avoids environment-specific paths, user names, tokens, deployment hostnames, private project names, and private operational notes. Keep examples generic so the repo can remain safe to publish.

# port-skill-collection

Hermes Agent skill for safely porting external `SKILL.md` collections into a Hermes active-profile skills tree.

## What it does

This skill provides a reusable workflow for importing Claude Code plugins, agentskills-style repositories, Codex/OpenCode/Cursor skill collections, or other GitHub repositories of `SKILL.md` directories into Hermes Agent.

Key safeguards:

- resolve the active Hermes profile skills root instead of assuming shell `~/.hermes/skills`;
- pin the source repository commit before copying;
- preserve upstream license/NOTICE files;
- preserve the original upstream `SKILL.md` as `references/original-SKILL.md`;
- refresh mode: pull upstream updates via SHA-to-SHA diff and three-way reconcile, preserving local Hermes adaptations instead of clobbering them;
- hard-gate large collections: if a source has more than 3 skills, inventory first, estimate per-session index cost, and wait for user subset selection before installing;
- quote YAML date/timestamp-like generated metadata values so `skill_view` serialization does not break.

## Install into Hermes

Install directly from GitHub:

```bash
hermes skills install https://raw.githubusercontent.com/vcolombo/port-skill-collection/main/SKILL.md
```

### Offline fallback: manual copy for offline/air-gapped installs

If the machine cannot reach GitHub, derive the skills root from the Hermes runtime instead of guessing from `$HOME`:

```bash
# Offline fallback: derive the skills root from the runtime, not from $HOME
hermes profile show default   # note the "Path:" line — skills live at <Path>/skills
mkdir -p "<Path>/skills/migration/port-skill-collection"
cp SKILL.md LICENSE "<Path>/skills/migration/port-skill-collection/"
```

Then verify in a fresh Hermes process/session:

```bash
hermes --skills port-skill-collection chat -q 'Return exactly: loaded' --toolsets safe -Q
```

Installed skills appear in new sessions after prompt/cache refresh.

## Repository contents

- `SKILL.md` — the Hermes skill.
- `README.md` — this public installation note.
- `LICENSE` — MIT license.

## Public-release hygiene

This repository intentionally avoids environment-specific paths, user names, tokens, deployment hostnames, private project names, and private operational notes. Keep examples generic so the repo can remain safe to publish.

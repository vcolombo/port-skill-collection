# port-skill-collection

Hermes Agent skill for safely porting and refreshing external `SKILL.md` collections into a Hermes active-profile skills tree.

## What it does

This skill provides a reusable workflow for importing Claude Code plugins, agentskills-style repositories, Codex/OpenCode/Cursor skill collections, or other GitHub repositories of `SKILL.md` directories into Hermes Agent.

Key safeguards:

- resolve the active Hermes profile skills root instead of assuming shell `~/.hermes/skills`;
- pin the source repository commit before copying;
- preserve upstream license/NOTICE files;
- preserve the original upstream `SKILL.md` as `references/original-SKILL.md`;
- maintain a `ports.yaml` ledger at the active skills root so manual-copy ports have update metadata;
- refresh mode: pull upstream updates via SHA-to-SHA diff and three-way reconcile, preserving local Hermes adaptations instead of clobbering them;
- hard-gate large collections: if a source has more than 3 skills, inventory first, estimate per-session index cost, and wait for user subset selection before installing;
- quote YAML date/timestamp-like generated metadata values so `skill_view` serialization does not break.

## Install into Hermes

Install the full skill directory from GitHub:

```bash
hermes skills install vcolombo/port-skill-collection/skills/port-skill-collection --category migration
```

Why not a raw `SKILL.md` URL? This skill now ships support files under `references/` and `templates/`. Hermes can install those support files from a GitHub skill-directory identifier, but a raw `SKILL.md` URL installs only that single file.

### Offline fallback: manual copy for offline/air-gapped installs

If the machine cannot reach GitHub, derive the skills root from the Hermes runtime instead of guessing from `$HOME`:

```bash
# From a clone of this repository:
hermes profile show default   # note the "Path:" line — skills live at <Path>/skills
mkdir -p "<Path>/skills/migration/port-skill-collection"
cp -R skills/port-skill-collection/. "<Path>/skills/migration/port-skill-collection/"
```

Then verify in a fresh Hermes process/session:

```bash
hermes --skills port-skill-collection chat -q 'Return exactly: loaded' --toolsets safe -Q
```

Installed skills appear in new sessions after prompt/cache refresh.

## Repository contents

- `skills/port-skill-collection/SKILL.md` — the Hermes skill.
- `skills/port-skill-collection/references/refresh-mode.md` — refresh workflow details.
- `skills/port-skill-collection/references/ports-ledger.md` — `ports.yaml` schema and update rules.
- `skills/port-skill-collection/templates/ports.yaml` — starter ledger template.
- `skills/port-skill-collection/LICENSE` — license copy included with full-directory installs.
- `README.md` — this public installation note.
- `LICENSE` — repository MIT license.

## Public-release hygiene

This repository intentionally avoids environment-specific paths, user names, tokens, deployment hostnames, private project names, and private operational notes. Keep examples generic so the repo can remain safe to publish.

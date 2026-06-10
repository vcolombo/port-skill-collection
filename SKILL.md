---
name: port-skill-collection
description: Port a Claude Code plugin or external skill collection (a GitHub repo of SKILL.md directories) into Hermes Agent. Use when installing, importing, adapting, or "porting" existing skills from Claude Code, Codex, Cursor, OpenCode, or any agentskills-style repo — e.g. "port this skill repo into Hermes", "add the skills from github.com/x/y". For authoring new skills from scratch, use skill-creator instead; this skill is only for migrating existing ones.
version: 2.0.0
metadata:
  hermes:
    tags: [skills, migration, claude-code, setup]
    category: migration
---

# Port a Skill Collection into Hermes

Adapt an external skill repo (Claude Code plugin, agentskills.io-style collection) for use in Hermes. Skills port; plugin infrastructure such as hooks, slash commands, and named agents does not port directly and must be replaced with Hermes-native equivalents.

## Workflow

### 1. Locate and pin the source
- Get the repo URL from the user. Clone or pull it into a persistent external checkout such as `$HERMES_HOME/external-skill-repos/<repo-name>` or another user-approved persistent path. In containerized runtimes, do not put the only checkout in `/tmp` or another ephemeral image-layer path.
- Record the exact source identity before copying anything:
  ```bash
  git -C <repo> remote get-url origin
  git -C <repo> rev-parse HEAD
  git -C <repo> status --short
  ```
- Pin all provenance to that commit SHA. If refreshing an existing port, compare the previous recorded SHA to the new one before overwriting files.
- Find where skills live by searching for `SKILL.md` files, not by assuming layout. Common layouts include `skills/`, `optional-skills/`, nested `skills/skills/...`, or top-level directories each containing `SKILL.md`. Some projects split plugin and skills into two repos — clone the skills repo, not the plugin shim.

### 2. Resolve the active Hermes skill destination
- Do **not** assume shell `~/.hermes/skills`. Resolve the active profile or Hermes home first. Default single-profile installs often use `$HERMES_HOME/skills`; named profiles commonly have separate homes and skill roots.
- Prefer Hermes-native writes when creating local/runtime skills: `skill_manage(action='create')`, `skill_manage(action='patch')`, and `skill_manage(action='write_file')` automatically target the active profile and avoid accidentally writing to another profile.
- If you must copy files manually, derive the destination from the active runtime, not shell `~`:
  ```bash
  hermes profile show default  # or the explicit target profile
  hermes skills list
  ```
  Then verify the resulting installed path with `skill_view(<name>)` or `hermes --skills <name> chat -q 'Return exactly: loaded' --toolsets safe -Q`.

### 3. Inventory and prune (HARD GATE before installing)
- List every skill found: name + one-line description.
- Estimate rough per-session index cost before installation. Use a coarse but explicit estimate: every installed skill contributes its `name` + `description` to the `<available_skills>` index of new sessions, so count skills and approximate description text size/tokens rather than pretending unused skills are free.
- **Hard gate:** if the source contains more than 3 skills, you MUST present the full inventory with one-line descriptions and the rough per-session index cost, then WAIT for the user to choose the subset before installing anything.
- A broad request such as "install the repo," "add the skills," or "install all of them" is not consent to index the full set when the repo contains more than 3 skills. Treat it as a request to inventory and recommend a subset unless the user explicitly confirms after seeing the inventory/cost.
- Default recommendation: only skills matching the user's actual workflows. Never install a large collection silently.

### 4. Install the chosen subset
Pick ONE method and tell the user the tradeoff:
- **Copy (default):** copy each chosen skill directory into the active profile's resolved skills directory, e.g. `<active-skills-dir>/<category>/<skill-name>/`. Pro: fully owned, prunable, survives environment rebuilds. Con: no automatic updates; re-run this skill to refresh.
- **Symlink (whole collection):** symlink a small, intentionally chosen collection into the active profile's resolved skills directory only after confirming Hermes indexes symlinked directories in this deployment. Pro: `git pull` updates the collection. Con: all linked skills get indexed every session — only appropriate for small collections the user wants in full.

Standard install preservation steps for each copied skill:
- Preserve upstream license files (`LICENSE`, `LICENSE.txt`, `NOTICE`, or equivalent) inside the installed skill directory when the source provides them.
- Preserve the unmodified upstream `SKILL.md` as `references/original-SKILL.md` before rewriting for Hermes. If `references/` does not exist, create it.
- Add provenance to the adapted `SKILL.md` frontmatter or body: source repo URL, source relative path, pinned commit SHA, port date, and a short note that the installed body was adapted for Hermes.
- If the source has support files, copy them deliberately into Hermes-supported support directories (`references/`, `templates/`, `scripts/`, `assets/`) and document any files omitted.
- If refreshing a previously ported skill, never overwrite `references/original-SKILL.md` without first comparing the old pinned SHA, new pinned SHA, and local changes.

### 5. Compatibility pass (every installed skill)
- Frontmatter must have `name` and `description`; add minimal valid frontmatter if missing or malformed.
- Flag Claude Code–specific references the agent should mentally translate: tool names (`Read`, `Grep`, `Glob`, `Task`, `Skill` tool), `CLAUDE.md`, Claude config paths, and subagent dispatch. Do not rewrite the skill bodies unless the user asks — note the mappings to Hermes equivalents such as `read_file`, `search_files`, `delegate_task`, and `skill_view` in your summary instead.
- Note anything that simply will not work in the current environment, such as unavailable MCP servers, missing CLIs, missing credentials, OS-specific scripts, or paid external APIs, so the user can decide.

### 6. Bootstrap / discipline wiring (if applicable)
If the source plugin used a session-start hook to inject a meta-skill, Hermes has no hook equivalent. Offer the user one of:
- **Topic/platform binding:** create a trimmed bootstrap skill containing only the load-bearing rules, then bind it to a specific messaging topic/profile/platform via Hermes configuration. Back up configuration first and show a focused diff before applying.
- **Global persona note:** add a concise instruction to the agent persona asking it to check relevant installed skills before acting.
- **Neither:** skills still trigger from their descriptions, just not mandatorily.

### 7. Activate and verify
- Installed skills take effect in new sessions. Tell the user to start a new session or otherwise invalidate prompt caching after installation.
- Verify with `skill_view(<name>)` on multiple representative installed skills, including one with multiline YAML frontmatter. If `skill_view` fails with serialization errors, inspect generated frontmatter for unquoted YAML typed scalars such as dates and quote them before retrying.
- Give the user one natural test phrase per installed skill that should trigger it.

## Pitfalls
- GitHub API rate limits can break repository discovery or hub installs. Authenticate GitHub requests when doing repeated repository operations.
- GitHub `tree/` URLs can block automated fetching; clone repositories instead of scraping web pages.
- Nested skill layouts (`skills/skills/...`) exist in some repos — locate by searching for `SKILL.md` files, not by assuming structure.
- Do not enable optional shell-execution features just because a ported skill contains shell snippets; surface that to the user as a trust decision.
- In containerized runtimes, confirm the resolved active-profile skills directory is on persistent storage so installs survive container rebuilds.
- Do not use shell `~` as a proxy for Hermes home. `HOME`, `HERMES_HOME`, active profile home, and persisted volume paths may differ.
- Do not skip commit pinning because the source repo is "latest" or small. Without a SHA, future refreshes cannot distinguish upstream drift from local adaptation.
- Do not drop license/NOTICE files or original upstream `SKILL.md` when rewriting; provenance is part of the install, not optional documentation.
- Quote YAML metadata values that look like dates or other typed scalars, especially generated fields such as `ported_at: "YYYY-MM-DD"`. Unquoted dates can parse into native date objects and break `skill_view`/JSON serialization even though the Markdown file looks valid.

## Done means
The user has: the chosen skills installed under the resolved active-profile skills directory, source repo/relative path/pinned commit SHA recorded, upstream license/NOTICE files preserved when present, unmodified upstream `SKILL.md` saved as `references/original-SKILL.md`, compatibility summary delivered, any bootstrap wiring applied with a config backup, and a verified test trigger.

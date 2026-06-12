# Private custom skill repositories

Use this when the user wants locally maintained Hermes skills committed to private GitHub repositories without duplicating hub-installed or externally sourced skills.

## Classification workflow

1. Inventory installed skills from the resolved active skills root (derive it from the active profile/runtime; never hardcode a deployment path). For each `SKILL.md`, capture relative path, `name`, `description`, `version`, `author`, file count, and bytes.
2. Exclude skills that already have a source repo or are known external installs:
   - Hermes Hub lock metadata under `.hub/lock.json` marks hub-installed skills.
   - Existing checked-out source repos/remotes should be treated as already-covered.
   - Known external collections such as `claude-superpowers` and `hashicorp/terraform` should not be re-published as “ours”.
3. Include only skills with local/custom operational signals: private project names, user/operator procedures, deployment-specific knowledge (profiles, gateways, schedulers, task boards, memory/MCP wiring), or locally adapted runbooks not represented by another repo.
4. Keep classification evidence in a JSON report. Do not rely on the final repo list alone; future cleanup depends on knowing why a skill was included or excluded.

## Repository shape

For each selected skill, create one private repo using a predictable name such as:

```text
hermes-skill-<skill-name>
```

Local working copies can live under a persistent directory such as:

```text
<persistent-home>/skill-repos/<repo-name>
```

Each repo should contain the skill directory contents at repository root, plus:

- `README.md` if absent, pointing to `SKILL.md` and recording the runtime export path.
- `.gitignore` for caches, bytecode, logs, `.env*`, `node_modules`, build outputs.

Use GitHub private repos by default for user/project-specific skill material.

## Safety checks before push

Before `gh repo create --private --source ... --push`, run staged/working-tree checks:

- No files over 1 MB unless explicitly intended.
- No obvious private key or live-token patterns.
- Treat placeholder examples (`<personal-access-token>`, `sk-...`, `REDACTED`, `xxx`) as examples, not blockers, but strict-match real-looking tokens must block publication.
- Preserve runtime skills in place; only copy to the repo work area.

After push, verify each repo:

```bash
gh repo view <owner>/<repo> --json visibility,defaultBranchRef,pushedAt

git -C <persistent-home>/skill-repos/<repo> status --short --branch
```

Expected: `PRIVATE`, `main`, clean branch tracking `origin/main`.

## Updating the config repo

After publishing skill repos, update the Hermes config backup repo with inventories only, not skill source copies:

- `inventories/custom-skill-repos.json` — machine-readable mapping from skill path/name to repo URL.
- `docs/custom-skill-repos.md` — human-readable mapping and classification policy.

This keeps the config backup boundary clean: configuration and restore metadata live in the config repo, while maintainable skill source lives in dedicated repos.

## Pitfalls

- Do not create public repos for user/project/operator-specific skill material unless the user explicitly requests a public release and privacy scrub.
- Do not publish hub-installed or external collection skills as if they were locally authored.
- Do not rewrite the active runtime skill tree during publication; copy to a separate repo work area.
- If a repository was created too broadly, archive/delete/reclassify only with explicit approval because GitHub repo deletion is destructive.
- Removing skill source from the tip of a config repo does not purge earlier Git history. History purge is a separate force-push operation and needs explicit approval.

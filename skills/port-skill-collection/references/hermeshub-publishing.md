# HermesHub publication target discipline

Use this when the user asks to publish a skill to the Hermes Skill Hub / HermesHub.

## Correct target

- "Hermes Skill Hub", "Skills Hub", or "HermesHub" means the hub/listing repository and flow, not bundled inclusion in `NousResearch/hermes-agent`.
- The Hub PR shape is a complete directory under:
  ```text
  skills/<skill-name>/
  ```
- The CLI flow is:
  ```bash
  hermes skills publish <skill-dir> --to github --repo amanning3390/hermeshub
  ```
- A manual fork/branch/PR is acceptable when it produces the same shape, but say explicitly that it is equivalent to the publish command and avoid creating duplicate PRs.

## Not the same thing

Do **not** submit to these targets unless the user explicitly asks for official bundled/optional inclusion:

```text
NousResearch/hermes-agent/skills/
NousResearch/hermes-agent/optional-skills/
```

Bundled/optional inclusion is a different distribution decision with a different review bar. It is not implied by "publish to the skill hub."

## Verification checklist

1. Confirm the PR target repo is the Hub repo, not `NousResearch/hermes-agent`.
2. Confirm changed files live under `skills/<skill-name>/`.
3. Confirm the submitted directory contains every support file users need (`SKILL.md`, license, `references/`, `templates/`, `scripts/`, `assets/` as applicable).
4. Run the Hub scanner or local equivalent against the submitted `SKILL.md` and report its status/findings.
5. Clean-install the source distribution with the advertised install identifier and verify support files load via `skill_view`.
6. Tell the user the skill is **submitted** until the Hub PR is merged and indexed; do not call it published/listed prematurely.

## If the wrong PR was opened

1. Close the wrong PR with a concise comment explaining it was the wrong distribution target.
2. Delete the source branch in the fork to reduce clutter.
3. Do not claim the PR can be fully removed from GitHub history; normal users can close PRs and delete branches, but GitHub generally keeps PR records unless Support removes them for sensitive-data/legal reasons.
4. Submit the correct Hub PR and link it in the final report.

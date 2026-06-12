# Changelog

Skill package history for `skills/port-skill-collection`. The in-package
`## Change ledger` keeps only the current release; full history lives here
(outside the installable directory, so history edits do not force version bumps).

- **2.3.0** — Added publishing trigger phrases to the description; condensed the publishing section and pitfalls to reference pointers to cut per-session context cost; genericized `references/private-custom-skill-repos.md`.
- **2.2.9** — Added `metadata.hermes.repository` pointing to `https://github.com/vcolombo/port-skill-collection` so Hermes config backup can classify the skill as source-backed instead of at-risk.
- **2.2.8** — Added private custom skill repository workflow and `references/private-custom-skill-repos.md`: classify hub/external vs locally maintained skills, publish one private repo per selected skill, verify privacy/branch/secret/size checks, and update the config backup repo with an inventory instead of duplicating skill source.
- **2.2.1–2.2.7** — Consolidated previously published local maintenance history into the source repo: trigger-anchor preservation, safety CI/release gates, Gitleaks/CodeQL/Dependabot updates, public privacy-scrub safeguards, and version-bump enforcement for package changes.

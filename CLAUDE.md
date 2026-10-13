# claude-plugins-official

Curated Claude Code plugin marketplace. Content is Markdown (skills, agents,
commands), JSON manifests, and a few shell hooks. No root build or package.

## Layout
- `.claude-plugin/marketplace.json` — the catalog (every plugin entry + `renames` map)
- `plugins/<name>/` — internal plugins. Reference shape: `plugins/example-plugin`
  (`.claude-plugin/plugin.json`, `skills/*/SKILL.md`, `commands/`, `agents/`,
  `hooks/`, `.mcp.json`, `README.md`, `LICENSE`)
- `.github/workflows/` + `.github/scripts/` — CI validation, scanning, SHA bumps

## Never
- **Never rename a plugin.** A marketplace `name` is an immutable slug; changing it
  breaks installs. Change `displayName` instead. If a rename is ever approved by a
  human, it also needs a `renames` entry.
- **Never touch `external_plugins/`** — third-party code, not ours to edit.
- Never hand-edit `source.sha` values in `marketplace.json`; the
  `bump-plugin-shas` workflow owns them.
- Never edit `.github/workflows/` unless explicitly asked.

## Code rules
- Every `plugins/<name>/` must ship a `LICENSE` containing Apache License 2.0
  text (only `plugins/claude-security` is exempt).
- Skill = `skills/<skill-name>/SKILL.md`; frontmatter `name` must match the folder.
- Quote frontmatter values containing any of `` {}[]*&#!|>%@` ``.
- Keep SKILL.md lean; move long sections into `references/` files next to it.
- New plugin → copy `plugins/example-plugin`, then add its marketplace entry.

## Commands
- Validate a plugin: `claude plugin validate plugins/<name>`
- Validate the catalog: `claude plugin validate .claude-plugin/marketplace.json`
- Frontmatter (CI parity): `cd .github/scripts && bun install yaml && cd -` once, then
  `bun .github/scripts/validate-frontmatter.ts <changed .md files>`
- JSON syntax: `jq empty <file.json>`
- Hook tests: `bash .claude/hooks/tests/run.sh`

## Definition of done
A change is done only when all of these pass on the files you touched:
1. `claude plugin validate` on each changed plugin dir (and on
   `marketplace.json` if it changed) — "Validation passed" (warnings OK if pre-existing).
2. `bun .github/scripts/validate-frontmatter.ts` on every changed
   SKILL.md / agent / command file — exit 0.
3. `jq empty` on every changed JSON file — exit 0.
4. New plugin dir has an Apache-2.0 `LICENSE`.
Report the exact commands you ran and their output. Never say "should work".
(No UI in this repo, so no screenshot step.)

## Mistakes Claude made before
- Skill frontmatter `name` didn't match its folder (hookify) — check it.
- Command `allowed-tools` was wrong (example-command) — list only tools the
  command actually uses.
- SKILL.md files grew too long (plugin-dev) — split into `references/`.

## For the human
- `/clear` between unrelated tasks.
- `/compact` when one task runs long.
- Esc Esc to rewind when Claude takes a wrong turn (file edits only; bash changes need git).

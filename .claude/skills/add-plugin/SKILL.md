---
name: add-plugin
description: Scaffold a new internal plugin under plugins/ and register it in .claude-plugin/marketplace.json. Use when asked to add, create, or scaffold a new plugin in this repo.
---

# Add an internal plugin

1. Confirm the slug with the user. It is permanent — plugin names are never renamed.
   Check it is not already in `.claude-plugin/marketplace.json` or `renames`.
2. Copy the shape of `plugins/example-plugin`:
   - `plugins/<slug>/.claude-plugin/plugin.json` with `name`, `description`,
     `author: {"name": "Anthropic", "email": "support@anthropic.com"}`
   - `plugins/<slug>/LICENSE` — copy `plugins/example-plugin/LICENSE` (Apache 2.0)
   - `plugins/<slug>/README.md`
   - only the parts it needs: `skills/<skill>/SKILL.md` (frontmatter `name` = folder),
     `commands/`, `agents/`, `hooks/`, `.mcp.json`
3. Add a marketplace entry (append to `plugins`, do not edit others):
   `{"name", "description", "author", "source": "./plugins/<slug>",
     "category", "homepage": "https://github.com/anthropics/claude-plugins-official/tree/main/plugins/<slug>"}`
4. Run the definition of done from CLAUDE.md and paste the output:
   `claude plugin validate plugins/<slug>`,
   `claude plugin validate .claude-plugin/marketplace.json`,
   `bun .github/scripts/validate-frontmatter.ts <new .md files>`.
5. Never touch `external_plugins/` — third-party plugins come via the submission form.

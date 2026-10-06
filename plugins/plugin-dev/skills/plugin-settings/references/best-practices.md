# Plugin Settings Best Practices and Security

Best practices and security considerations for `.claude/*.local.md` plugin settings files. Moved from SKILL.md to keep it concise.

## Best Practices

### File Naming

✅ **DO:**
- Use `.claude/plugin-name.local.md` format
- Match plugin name exactly
- Use `.local.md` suffix for user-local files

❌ **DON'T:**
- Use different directory (not `.claude/`)
- Use inconsistent naming
- Use `.md` without `.local` (might be committed)

### Gitignore

Always add to `.gitignore`:

```gitignore
.claude/*.local.md
.claude/*.local.json
```

Document this in plugin README.

### Defaults

Provide sensible defaults when settings file doesn't exist:

```bash
if [[ ! -f "$STATE_FILE" ]]; then
  # Use defaults
  ENABLED=true
  MODE=standard
else
  # Read from file
  # ...
fi
```

### Validation

Validate settings values:

```bash
MAX=$(echo "$FRONTMATTER" | grep '^max_value:' | sed 's/max_value: *//')

# Validate numeric range
if ! [[ "$MAX" =~ ^[0-9]+$ ]] || [[ $MAX -lt 1 ]] || [[ $MAX -gt 100 ]]; then
  echo "⚠️  Invalid max_value in settings (must be 1-100)" >&2
  MAX=10  # Use default
fi
```

### Restart Requirement

**Important:** Settings changes require Claude Code restart.

Document in your README:

```markdown
## Changing Settings

After editing `.claude/my-plugin.local.md`:
1. Save the file
2. Exit Claude Code
3. Restart: `claude` or `cc`
4. New settings will be loaded
```

Hooks cannot be hot-swapped within a session.

## Security Considerations

### Sanitize User Input

When writing settings files from user input:

```bash
# Escape quotes in user input
SAFE_VALUE=$(echo "$USER_INPUT" | sed 's/"/\\"/g')

# Write to file
cat > "$STATE_FILE" <<EOF
---
user_setting: "$SAFE_VALUE"
---
EOF
```

### Validate File Paths

If settings contain file paths:

```bash
FILE_PATH=$(echo "$FRONTMATTER" | grep '^data_file:' | sed 's/data_file: *//')

# Check for path traversal
if [[ "$FILE_PATH" == *".."* ]]; then
  echo "⚠️  Invalid path in settings (path traversal)" >&2
  exit 2
fi
```

### Permissions

Settings files should be:
- Readable by user only (`chmod 600`)
- Not committed to git
- Not shared between users

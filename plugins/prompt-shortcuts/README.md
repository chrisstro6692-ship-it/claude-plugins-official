# prompt-shortcuts

Thirty popular "prompt shortcuts" packaged as Claude Code skills. Each one is a
slash command that applies a well-defined transformation to the text you pass
it — or, with no argument, to Claude's last answer.

## Install

```
/plugin install prompt-shortcuts@claude-plugins-official
```

## Usage

```
/prompt-shortcuts:eli5 how do vaccines work
/prompt-shortcuts:human <paste AI-sounding text>
/prompt-shortcuts:critic          # critiques Claude's previous answer
```

The skills are user-invoked only (`disable-model-invocation: true`), so they
never trigger on their own — they run only when you type them.

## Skills

| Writing & tone | Thinking & roles | Format | Code | Career & life |
|---|---|---|---|---|
| `human` | `expert` | `brief` | `code` | `email` |
| `copywriter` | `ceo` | `summarize` | `debug` | `coverletter` |
| `viral` | `critic` | `list` | `explain-code` | `interview` |
| `seo` | `teacher` | `table` | | `motivate` |
| `improve` | `eli5` | `outline` | | |
| `simplify` | `strategy` | `compare` | | |
| `expand` | `research` | | | |
| `translate` | `brainstorm` | | | |
| | `promptengineer` | | | |

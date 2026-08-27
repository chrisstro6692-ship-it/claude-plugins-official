# Graphify

A Claude Code plugin that generates clear, accurate diagrams and graphs from code, architecture, data flows, and relationships.

## Features

- **Automatic diagram generation** — Claude reads your code and produces diagrams without manual markup
- **Multiple formats** — Mermaid (GitHub/GitLab-rendered), Graphviz DOT, and ASCII art
- **Multiple diagram types** — flowcharts, sequence diagrams, class diagrams, ER diagrams, state machines, and more
- **Smart type inference** — Claude picks the most appropriate diagram type based on what you're graphing

## Usage

### Slash command

```
/graphify [target] [--format mermaid|dot|ascii] [--type flowchart|sequence|class|er|state]
```

**Examples:**

```
/graphify src/auth
/graphify UserService.ts --type class
/graphify --format dot src/
/graphify "order processing flow" --type sequence
/graphify --format ascii database schema
```

### Contextual (model-invoked)

The `graphify` skill activates automatically when you ask Claude to visualize, diagram, graph, draw, or map code structure, architecture, data flows, dependencies, class hierarchies, sequences, entity relationships, or state machines.

**Examples:**

- "Diagram the authentication flow"
- "Can you graph the dependencies in src/?"
- "Visualize the database schema"
- "Draw a sequence diagram for the checkout process"
- "Show me the class hierarchy for the payment module"

## Supported diagram types

| Type | Best for |
|---|---|
| Flowchart | Logic flows, decision trees, pipelines, module dependencies |
| Sequence | API calls, HTTP flows, message passing between services |
| Class | OOP hierarchies, interfaces, relationships |
| ER | Database schemas, data models |
| State | FSMs, lifecycle diagrams, workflow states |

## Supported output formats

| Format | Use when |
|---|---|
| Mermaid (default) | Output will be rendered in GitHub, GitLab, Notion, or Markdown tools |
| Graphviz DOT | Complex graphs needing fine-grained layout control |
| ASCII | Terminal output, plain text, no rendering support |

## Installation

```
/plugin install graphify@claude-plugins-official
```

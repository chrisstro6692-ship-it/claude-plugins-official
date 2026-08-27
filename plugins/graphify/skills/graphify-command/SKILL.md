---
name: graphify
description: Generate a diagram or graph from code, architecture, or data. Supports Mermaid, Graphviz DOT, and ASCII formats.
argument-hint: [target] [--format mermaid|dot|ascii] [--type flowchart|sequence|class|er|state]
allowed-tools: [Read, Glob, Grep, Bash]
---

# Graphify Command

Generate a diagram or graph from code, architecture, or data relationships.

## Arguments

The user invoked this with: $ARGUMENTS

Parse arguments as follows:
- **target** (optional): A file path, directory, function name, module name, or description of what to graph. If omitted, graph the current project's top-level structure.
- **--format** (optional): Output format — `mermaid` (default), `dot`, or `ascii`
- **--type** (optional): Diagram type — `flowchart`, `sequence`, `class`, `er`, `state`. If omitted, infer the best type from the target.

## Instructions

1. **Parse the arguments** to identify the target and any format/type overrides.

2. **Explore the target** using Read, Glob, and Grep tools:
   - If a file or directory: read relevant source files to understand structure, imports, classes, and functions
   - If a description or concept: interpret it directly and graph it as described
   - If no target given: use Glob to discover top-level structure of the current project

3. **Select the diagram type** (unless specified by `--type`):

   | Target | Best type |
   |---|---|
   | Function / logic flow | flowchart |
   | API / HTTP / messaging | sequence |
   | Classes / interfaces | class |
   | Database / schema | er |
   | State machine / lifecycle | state |
   | Module / file dependencies | flowchart |
   | System / service overview | flowchart |

4. **Generate the diagram** in the requested format:

   - **mermaid** (default): Wrap in a ` ```mermaid ` fenced code block. Ensure valid Mermaid syntax — node IDs cannot have spaces, labels with special characters must be quoted.
   - **dot**: Wrap in a ` ```dot ` fenced code block. Use Graphviz DOT syntax.
   - **ascii**: Produce a plain-text box-and-arrow diagram suitable for terminals and plain text environments.

5. **Present the diagram** with:
   - A one-line title or caption
   - The fenced code block containing the diagram
   - A brief explanation of what the diagram shows (2–4 sentences)
   - An offer to zoom in on a specific area, adjust the format, or add more detail

## Examples

```
/graphify src/auth
/graphify UserService.ts --type class
/graphify --format dot src/
/graphify "order processing flow" --type sequence
/graphify --format ascii database schema
```

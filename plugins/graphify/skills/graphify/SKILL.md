---
name: graphify
description: This skill should be used when the user asks to "visualize", "diagram", "graph", "chart", "draw", or "map" code structure, architecture, data flows, dependencies, class hierarchies, sequences, entity relationships, or state machines. Automatically generates clear, accurate diagrams from code and context.
version: 1.0.0
---

# Graphify

Graphify generates accurate, readable diagrams from code, architecture descriptions, and data relationships. Choose the best format based on what is being visualized and what the user's environment supports.

## Format Selection Guide

### Mermaid (preferred for most cases)
Use Mermaid when the output will be rendered in GitHub, GitLab, Notion, or any Markdown-aware tool. Mermaid supports:

- **Flowchart** (`graph TD` / `graph LR`) — logic flows, decision trees, pipelines
- **Sequence diagram** (`sequenceDiagram`) — API calls, message passing, HTTP flows
- **Class diagram** (`classDiagram`) — OOP hierarchies, interfaces, relationships
- **Entity Relationship** (`erDiagram`) — database schemas, data models
- **State diagram** (`stateDiagram-v2`) — FSMs, lifecycle diagrams
- **Gantt** (`gantt`) — timelines, project schedules
- **C4 diagram** (`C4Context`, `C4Container`) — system architecture

Always wrap Mermaid in a fenced code block:
````
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[End]
```
````

### Graphviz DOT
Use DOT format when the user requests it explicitly, or for complex directed/undirected graphs where fine-grained layout control is needed. Wrap in a `dot` code block:
````
```dot
digraph G {
    rankdir=LR;
    A -> B -> C;
    A -> C;
}
```
````

### ASCII Art
Use ASCII when the user needs a plain-text diagram (terminal output, email, no rendering support). Keep it simple and readable:

```
┌────────────┐     ┌────────────┐
│   Client   │────▶│   Server   │
└────────────┘     └────────────┘
```

## Workflow

### 1. Understand what to graph
- Read referenced files using Read, Glob, and Grep tools to understand structure
- Identify key nodes: classes, functions, modules, services, tables, states
- Identify edges: calls, imports, inheritance, foreign keys, transitions

### 2. Choose the right diagram type

| Subject | Recommended type |
|---|---|
| Function call chains / logic flow | Flowchart |
| API / service communication | Sequence diagram |
| Class / interface relationships | Class diagram |
| Database schema | ER diagram |
| State machine / lifecycle | State diagram |
| Module / package dependencies | Flowchart or DOT |
| System architecture overview | C4 or Flowchart |
| Data transformation pipeline | Flowchart |

### 3. Keep diagrams readable
- Limit to the most important nodes — omit trivial details unless asked
- Use meaningful, short labels (abbreviate long names if needed)
- Add a brief title or caption above the diagram
- Group related nodes using subgraphs where it improves clarity

### 4. Validate syntax
Before presenting a Mermaid diagram, verify the syntax is correct:
- Node IDs must not contain spaces — use underscores or camelCase
- String labels with special characters must be quoted: `A["label (1)"]`
- Arrows must use valid syntax: `-->`, `---`, `-.->`, `==>`, `--text-->`
- `classDiagram` uses `<|--` for inheritance and `..>` for dependency

## Examples

### Flowchart (code logic)
```mermaid
graph TD
    req[HTTP Request] --> auth{Authenticated?}
    auth -->|No| reject[401 Unauthorized]
    auth -->|Yes| handler[Route Handler]
    handler --> db[(Database)]
    db --> resp[HTTP Response]
```

### Sequence diagram (API interaction)
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant DB

    Client->>API: POST /login
    API->>DB: SELECT user WHERE email=?
    DB-->>API: User record
    API-->>Client: 200 OK + JWT
```

### Class diagram (OOP structure)
```mermaid
classDiagram
    class Animal {
        +String name
        +speak() String
    }
    class Dog {
        +fetch() void
    }
    class Cat {
        +purr() void
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

### ER diagram (database schema)
```mermaid
erDiagram
    USER {
        int id PK
        string email
        string name
    }
    ORDER {
        int id PK
        int user_id FK
        float total
    }
    USER ||--o{ ORDER : places
```

### State diagram (lifecycle)
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running : start()
    Running --> Paused : pause()
    Paused --> Running : resume()
    Running --> [*] : stop()
```

## Tips
- When graphing an entire codebase, focus on the top-level modules or entry points, then offer to zoom in on specific areas
- For large schemas, show only the core tables and their foreign-key relationships
- Always offer to refine or expand the diagram after presenting it

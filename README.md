# Isagawa Kernel

**A self-building, self-improving enforcement layer for Claude Code agents.**

The Isagawa Kernel governs how an AI agent works inside any Claude Code project. It enforces a structured loop — anchor, work, learn, complete — through hook-based gates that the agent cannot bypass. When the agent makes a mistake, it learns. When it drifts, it re-anchors. Every session, every project.

---

## What It Does

| Mechanism | Effect |
|-----------|--------|
| **Session gate** | Agent must invoke `/kernel/session-start` before any work |
| **Action counter** | Every Write, Edit, Bash increments a counter — blocks at 10 |
| **Anchor gate** | Forces agent to re-read protocol and review its own work every 10 actions |
| **Learn gate** | Blocks agent after any failure until it records a lesson |
| **HITL protocol** | Agent stops, reports, and waits for approval before fixing anything |
| **Self-build** | `/kernel/domain-setup` discovers your project and builds a custom protocol |

The hooks run as Claude Code PreToolUse/PostToolUse hooks. They are enforced at the infrastructure level — the agent sees `BLOCKED:` and the exact command to run. It cannot write its way around them.

---

## The Loop

```
session-start → anchor → WORK ──────────────────→ complete
                   ↑         ↓                        ↑
                   └─ every 10 actions ←──────────────┘
                             ↓
                   failure? → fix → learn (MANDATORY)
```

---

## Quick Start

### 1. Add the kernel to your project

```bash
# Copy .claude/ into your project root
cp -r /path/to/isagawa-kernel/.claude /path/to/your-project/

# Update settings.json with absolute paths for your machine
# (see INSTALL.md for the exact snippet)
```

### 2. Initialize for your project

Open Claude Code in your project and run:
```
/kernel/domain-setup
```

The kernel discovers your project, reads your code, builds a custom protocol, and initializes state. Restart Claude Code when prompted.

### 3. Start working

Every session begins the same way:
```
/kernel/session-start
```

The kernel resumes context, checks state, and anchors before any work begins.

---

## Commands

| Command | Purpose |
|---------|---------|
| `/kernel/session-start` | Start or resume a session |
| `/kernel/domain-setup` | Initialize kernel for a new project (run once) |
| `/kernel/anchor` | Re-read protocol, review work, reset counter |
| `/kernel/learn` | Record a lesson after fixing a failure |
| `/kernel/fix` | Impact assessment before applying any fix |
| `/kernel/complete` | Final gate — confirms task is done |
| `/kernel/autonomous-cycle` | Cycle through a task queue autonomously |
| `/kernel/validate` | Validate current state |
| `/kernel/reset` | Dev tool: wipe state for testing |

---

## File Structure

```
.claude/
├── commands/kernel/        ← All kernel slash commands
├── hooks/
│   ├── universal-gate-enforcer.py   ← PreToolUse: gates all Write/Edit/Bash
│   └── test-failure-detector.py     ← PostToolUse: detects failures, sets learn flag
├── skills/
│   ├── kernel-domain-setup/         ← 11-step skill for initializing a new domain
│   └── autonomous-cycling/          ← Skill for cycling through task queues
├── state/                  ← Runtime state (populated by kernel, gitignored)
├── lessons/                ← Lessons learned log (grows over time)
├── protocols/              ← Domain protocols (created by domain-setup)
└── settings.json           ← Hook registration (update paths for your machine)
```

---

## How the Hooks Work

Both hooks use `Path(__file__).resolve()` to locate state files — they work from any working directory, regardless of how Claude Code invokes them.

`settings.json` registers them as PreToolUse/PostToolUse hooks. After copying the kernel, update the hook command paths to absolute paths for your machine:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write|Bash",
      "hooks": [{"type": "command", "command": "python /absolute/path/to/.claude/hooks/universal-gate-enforcer.py"}]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "python /absolute/path/to/.claude/hooks/test-failure-detector.py"}]
    }]
  }
}
```

See `INSTALL.md` for the full setup walkthrough.

---

## For AI Agents

See `AGENT.md` — a structured guide for agents operating in a kernel-governed project.

---

## Origin

The Isagawa Kernel was developed as the enforcement layer inside the [Isagawa QA Platform](https://github.com/isagawa-qa) — a family of AI-powered test automation frameworks. It was extracted as a standalone component so it can govern any Claude Code project, not just QA workflows.

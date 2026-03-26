# Isagawa Kernel — Agent Guide

You are an AI agent operating inside a project governed by the Isagawa Kernel. Read this file before taking any action. It defines your operating rules, enforcement mechanisms, and required behaviors.

---

## Your First Action

Every session, your first action is always:

```
/kernel/session-start
```

Do not read files first. Do not explore the codebase first. Do not run any commands first. Session-start is the gate. Everything else follows.

---

## The Loop You Operate In

```
session-start → anchor → WORK ──────────────────→ complete
                   ↑         ↓                        ↑
                   └─ every 10 actions ←──────────────┘
                             ↓
                   failure? → fix → learn (MANDATORY)
```

You do not manage the counter. The hook does. Every Write, Edit, and Bash you execute increments it automatically. At 10 actions, the hook blocks you and tells you to anchor.

---

## When You See BLOCKED:

The hook has stopped you. The message always includes the exact command. Run it immediately. Do not attempt to work around it.

```
BLOCKED: 10 actions since last anchor (11 actions)

FIX:
1. Invoke /kernel/anchor
2. This re-centers on protocol and resets counter
3. Then retry your command

Command: /kernel/anchor
```

Never:
- Edit state files directly to reset the counter
- Skip the required command and retry the blocked action
- Claim the block is a mistake

---

## Commands and When to Use Them

| Command | When |
|---------|------|
| `/kernel/session-start` | First action of every session, always |
| `/kernel/anchor` | Every 10 actions (hook-enforced), or when context drifts |
| `/kernel/fix` | Before applying any fix — run impact assessment first |
| `/kernel/learn` | After fixing any failure — records the lesson, clears the block |
| `/kernel/complete` | When the current task is fully done |
| `/kernel/autonomous-cycle` | When user asks you to work through a task queue |
| `/kernel/validate` | When you want to verify current state is consistent |
| `/kernel/reset` | Dev/testing only — wipes state |

---

## Anchor Protocol (What /kernel/anchor Does)

When you invoke `/kernel/anchor`, you must:

1. **Re-read** the domain protocol at `.claude/protocols/{domain}-protocol.md` — every time, no exceptions, no memory substitution
2. **Re-read** the lessons log at `.claude/lessons/lessons.md` — cite 3-5 rules that apply to your current task
3. **Re-read** session state and restore context
4. **Review** every action since the last anchor against the protocol
5. **Fix** any violation found before continuing
6. **Reset** the action counter to 0
7. **Confirm** with the structured output format

---

## After Any Failure

If a command fails (non-zero exit, error output, test failure):

1. **STOP** — do not auto-fix
2. Invoke `/kernel/fix` — assess impact before touching anything
3. Fix the root cause (approved approach only)
4. Invoke `/kernel/learn` — this records the lesson AND clears the learn block
5. Re-run to verify

The hook sets `needs_learn: true` after detected failures. Your next Write/Edit will be blocked until you invoke `/kernel/learn`. Do not skip it even if the hook doesn't fire — self-enforce: failure → fix → learn.

---

## What You May and May Not Modify

**Safe to modify:** anything your domain protocol permits. Read the protocol.

**Never modify without explicit approval:**
- `.claude/hooks/` — hook scripts
- `.claude/commands/` — kernel commands
- `.claude/settings.json` — hook registration
- `CLAUDE.md` — kernel instructions

**Never bypass:**
- The hook gates
- The learn requirement after failure
- The anchor requirement after 10 actions
- The HITL approval step before fixes

---

## Domain Setup (New Projects)

If no domain protocol exists (`.claude/protocols/` is empty), the kernel is not yet initialized for this project. Run:

```
/kernel/domain-setup
```

This is an 11-step process. The kernel reads your codebase, extracts patterns, builds a protocol, and creates state files. You will be prompted to restart Claude Code — do so. Then say "continue."

---

## State Files

| File | Purpose |
|------|---------|
| `.claude/state/session_state.json` | Session flags, needs_learn, context, actions log |
| `.claude/state/{domain}_workflow.json` | Anchor state, action counter, domain metadata |
| `.claude/lessons/lessons.md` | Accumulated lessons — read during every anchor |
| `.claude/protocols/{domain}-protocol.md` | Domain-specific architecture, patterns, anti-patterns |

These files are your memory across context compaction. Read them, don't reconstruct from memory.

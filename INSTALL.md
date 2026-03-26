# Install Guide — Isagawa Kernel

Add the Isagawa Kernel to any Claude Code project in three steps.

---

## Prerequisites

- Python 3.8+
- Claude Code (CLI or VS Code extension)
- Git

---

## Step 1: Copy the Kernel

```bash
# From your project root
cp -r /path/to/isagawa-kernel/.claude /path/to/your-project/.claude
```

If your project already has a `.claude/` directory (e.g., from Claude Code settings), merge carefully — do not overwrite existing `settings.json`. Instead, add the hook entries manually (see Step 2).

---

## Step 2: Register the Hooks

Edit `.claude/settings.json` in your project. Add the hook entries with **absolute paths** to the hook scripts:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python /absolute/path/to/your-project/.claude/hooks/universal-gate-enforcer.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python /absolute/path/to/your-project/.claude/hooks/test-failure-detector.py"
          }
        ]
      }
    ]
  }
}
```

> **Why absolute paths?** Claude Code runs hooks from its own working directory, which may differ from your project root if a Bash command uses `cd`. Absolute paths guarantee the hooks are always found.

---

## Step 3: Initialize the Domain

Restart Claude Code (hooks only load at startup), then run:

```
/kernel/domain-setup
```

The kernel will:
1. Discover your project structure
2. Read your existing code to understand patterns
3. Build a custom protocol at `.claude/protocols/{domain}-protocol.md`
4. Create initial state files
5. Prompt you to restart Claude Code

After restarting, say "continue" — the kernel resumes from `/kernel/anchor`.

---

## Verifying the Install

After domain-setup and restart, try making any edit. If the kernel is working, you will see this if you haven't started a session:

```
BLOCKED: Session not started

FIX:
1. Invoke /kernel/session-start
...
```

That's the gate enforcer working. Run `/kernel/session-start` to begin.

---

## Updating Hook Paths

If you move your project directory, update the absolute paths in `settings.json`. The hook scripts themselves use `Path(__file__).resolve()` to locate state files, so they are portable — only the settings.json command strings need updating.

---

## Uninstalling

To remove the kernel from a project:

1. Delete `.claude/hooks/`, `.claude/commands/kernel/`, `.claude/skills/`, `.claude/state/`, `.claude/lessons/`, `.claude/protocols/`
2. Remove the hook entries from `.claude/settings.json`
3. Restart Claude Code

Your project's existing `.claude/settings.json` permissions and other settings are unaffected.

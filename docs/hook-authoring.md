# Hook authoring

Hooks are Python scripts Cursor invokes at lifecycle events. Configuration is in `.cursor/hooks.json`; scripts live in `.cursor/hooks/`.

## Configuration schema

`hooks.json` version must be `1`:

```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "command": ".cursor/hooks/pre_task.py",
        "matcher": "Shell|Task",
        "timeout": 15
      }
    ],
    "postToolUse": [ ... ],
    "postToolUseFailure": [ ... ],
    "stop": [ ... ],
    "subagentStop": [ ... ],
    "beforeSubmitPrompt": [ ... ]
  }
}
```

| Field | Purpose |
|-------|---------|
| `command` | Path relative to project root |
| `matcher` | Optional tool or prompt filter |
| `timeout` | Seconds before Cursor aborts the hook |
| `loop_limit` | Max invocations per session (stop hooks) |

## Hook script contract

1. Read JSON from **stdin** (may be empty).
2. Write JSON to **stdout**.
3. Exit `0` on success.
4. Finish within the configured **timeout**.
5. Be **executable** (`chmod +x`).

Minimal example:

```python
#!/usr/bin/env python3
import json
import sys

def main() -> int:
    raw = sys.stdin.read() or "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}
    print(json.dumps({
        "permission": "allow",
        "agent_message": "Hook acknowledged."
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

## Bundled hooks

| Script | Event | Role |
|--------|-------|------|
| `pre_task.py` | `preToolUse` | Pre-shell/task guidance |
| `post_task.py` | `postToolUse` | Post-task reminders |
| `failure.py` | `postToolUseFailure` | Record failure context |
| `stop.py` | `stop` | Session stop handling |
| `loop_continue.py` | `subagentStop` | Continue loop after subagent |
| `research.py` | `beforeSubmitPrompt` | Research policy hint |
| `validation.py` | `beforeSubmitPrompt` | Validation policy hint |

## Performance

Follow `performance-policy.mdc`:

- Keep hooks fast; avoid heavy scans on every keystroke.
- Record expensive work in `.cursor-loop/performance.json` via CLI controllers, not inside hooks.
- Prefer O(1) checks in prompt hooks (10s timeout).

## Safety

Follow `safety-policy.mdc`:

- Do not shell out with unsanitized user content.
- Never print secrets.
- Prefer `"permission": "deny"` only when a rule truly requires blocking (use sparingly).

## Installing and repairing

Install marks hooks executable:

```bash
python3 -m cursor_loop install .
```

Repair fixes permissions and re-runs verify:

```bash
python3 -m cursor_loop repair
```

Doctor reports non-executable scripts:

```bash
python3 -m cursor_loop doctor
```

## Adding a hook

1. Create `.cursor/hooks/my_hook.py` (executable).
2. Register in `hooks.json` under the appropriate event array.
3. Run verify:

   ```bash
   python3 -m cursor_loop verify
   ```

4. Test in Cursor by triggering the matched event.

## Regression

`hooks.json` and rule hashes feed L1/L2 regression. Changing hooks changes baseline hashes — document in CHANGELOG.

## Related

- [Architecture](architecture.md) — Hook lifecycle diagram
- [Subagent authoring](subagent-authoring.md)
- [Security policy](../SECURITY.md)

# Claude Mission Space UI probe — pre-build gate

Purpose: verify the installed Claude Code surface before making OSER correctness
depend on any mod UI.

## Evidence needed

1. plugin-authoring can create a disposable live pane;
2. a top/above-prompt band can show Mission stage + Health;
3. toast/status API exists and updates without model turns;
4. hooks still fire in the user's actual Claude Code surface;
5. uninstall/reload leaves no project state mutation;
6. fallback chat/Skill flow still works when the UI is absent.

## Important current caution

Claude Code's stable plugin structure documents Skills, agents, hooks and MCP/LSP
components. Mod UI surfaces are evolving separately. Keep any pane/band/toast
implementation in a Claude-specific adapter and capability-probe it by version.

The Decision Guard does not depend on mod UI.

## Proposed visual hierarchy

Band:
Mission | Formation/Delivery stage | verified progress | Health | pending decisions

Pane:
- Mission / current stage
- Decision Queue
- Active Truth
- Deliverables / Evidence
- Health / blockers

Do not expose chain-of-thought or raw agent conversations.

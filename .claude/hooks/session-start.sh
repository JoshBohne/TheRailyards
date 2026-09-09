#!/bin/zsh
# Tell the agent which Blender instances are live, which one the MCP session
# talks to, and where the dashboard is. Read-only except for copying the
# example MCP config into place when none exists.
cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}" || exit 0
echo "## Blender / dashboard status"
[ -f .mcp.json ] || { [ -f .mcp.json.example ] && cp .mcp.json.example .mcp.json && echo "- created .mcp.json from .mcp.json.example"; }
port=$(python3 -c "import json;d=json.load(open('.mcp.json'));print(d['mcpServers']['blender'].get('env',{}).get('BLENDER_PORT','9876'))" 2>/dev/null || echo 9876)
echo "- mcp__blender__* talks to port $port (BLENDER_PORT in .mcp.json)"
for p in 9876 9877 9878; do
  info=$(BMCP_PORT=$p timeout 4 python3 railyards-v4/tools/blender_mcp_client.py execute_code '{"code":"import bpy,os;print(bpy.context.scene.name,\"|\",os.path.basename(bpy.data.filepath) or \"unsaved\",\"|\",len(bpy.data.objects),\"objects\")"}' 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('result',{}).get('result','').strip())" 2>/dev/null)
  [ -n "$info" ] && echo "- Blender on :$p → $info" || echo "- Blender on :$p → not listening"
done
echo "- confirm the scene name with get_scene_info before any live edit; Blender CLI path: /Applications/Blender.app/Contents/MacOS/Blender"
if lsof -nP -iTCP:8863 -sTCP:LISTEN >/dev/null 2>&1; then echo "- dashboard already up: http://127.0.0.1:8863/ (state: work/live/state.json)"
else echo "- dashboard not running: start it with preview_start name=live-dashboard (or python3 tools/live-review/serve.py)"; fi
echo "- tool routing and dash.py publish steps: .claude/skills/blender-workflow/SKILL.md"
exit 0

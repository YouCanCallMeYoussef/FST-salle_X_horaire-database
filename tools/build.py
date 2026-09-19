"""Build index.html from tools/template.html + data/sessions-*.json.
Usage: python3 tools/build.py [data/sessions-S1-2026-2027.json]
"""
import json, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else root / "data" / "sessions-S1-2026-2027.json"
sessions = json.loads(src.read_text(encoding="utf-8"))
rooms = {r.strip() for s in sessions for r in s["room"].split(",") if r.strip()}
groups = {s["group"] for s in sessions}
body = (root / "tools" / "template.html").read_text(encoding="utf-8")
body = (body.replace("__SESSIONS_JSON__", json.dumps(sessions, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
            .replace("__SESSION_COUNT__", str(len(sessions)))
            .replace("__ROOM_COUNT__", str(len(rooms)))
            .replace("__GROUP_COUNT__", str(len(groups))))
i = body.index('<div class="wrap">')
head, body = body[:i], body[i:]
page = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Salles libres et emplois du temps des groupes de la Faculté des Sciences de Tunis — SecuriNets FST">
<style>[hidden]{{display:none!important}} img{{max-width:100%}}</style>
{head}</head>
<body>
{body}
</body>
</html>
"""
(root / "index.html").write_text(page, encoding="utf-8")
print(f"index.html: {len(sessions)} séances, {len(groups)} groupes, {len(rooms)} salles")

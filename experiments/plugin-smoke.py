#!/usr/bin/env python3
"""Load the ported v2 plugin and verify its before-tool hook persisted."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
cli = root / "versions/v2/node_modules/.bin/opencode"
plugin = root / "experiments/v2-port-plugin"
model = os.environ.get("OPENCODE_MODEL", "opencode/beam-free")
for attempt in range(1, 4):
    with tempfile.TemporaryDirectory(prefix="task2-plugin-") as temporary:
        folder = Path(temporary)
        (folder / "sample.txt").write_text("PORT-HOOK-OK\n")
        (folder / "opencode.json").write_text(json.dumps({"plugins": [str(plugin)]}))
        env = os.environ.copy()
        env["PWD"] = str(folder)
        for name, suffix in (("XDG_CONFIG_HOME", "config"), ("XDG_DATA_HOME", "data"), ("XDG_STATE_HOME", "state")):
            env[name] = str(folder / suffix)
        try:
            run = subprocess.run(
                [str(cli), "--standalone", "run", "--format", "json", "--model", model,
                 "Use the read tool to read sample.txt, then report its contents."],
                cwd=folder, env=env, capture_output=True, text=True, timeout=60,
            )
        except subprocess.TimeoutExpired:
            continue
        db = folder / "data/opencode/opencode.db"
        rows = []
        if db.exists():
            with sqlite3.connect(db) as connection:
                rows = connection.execute("select key, value from kv where key like '%:last-tool:%'").fetchall()
        records = [json.loads(row[1]) for row in rows]
        if run.returncode == 0 and records:
            print(json.dumps({"exit_code": run.returncode, "attempt": attempt, "hook_records": len(records),
                              "last_record": records[-1]}, ensure_ascii=False))
            break
else:
    raise SystemExit("Plugin hook did not persist an audit record in three attempts")

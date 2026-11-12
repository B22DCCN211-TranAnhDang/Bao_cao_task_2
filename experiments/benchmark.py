#!/usr/bin/env python3
"""Reproducible CLI benchmark. See BENCHMARK.md before interpreting metrics."""
import argparse
import csv
import json
import os
from pathlib import Path
import random
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "versions/v1/node_modules/.bin/opencode"
V2 = ROOT / "versions/v2/node_modules/.bin/opencode"
PI = ROOT / "versions/pi/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js"
CODEX = os.environ.get("CODEX_BIN", "codex")

TASKS = {
    "read": {
        "files": {"README.txt": "Project memo. Verification marker: THETA-731.\n"},
        "prompt": "Read README.txt and reply exactly: MARKER: <marker>. Do not modify files.",
    },
    "bug": {
        "files": {"mathlib.py": "def triangular(n):\n    if n < 0: raise ValueError('negative')\n    return n * (n - 1) // 2\n"},
        "prompt": "Fix triangular(n) in mathlib.py so it returns 0 for n=0, 1 for n=1, 6 for n=3, and rejects negative values. Edit only mathlib.py.",
    },
    "feature": {
        "files": {"textlib.py": "def slug(text):\n    raise NotImplementedError\n"},
        "prompt": "Implement slug(text) in textlib.py: trim outer whitespace, lowercase ASCII, replace each run of spaces with one hyphen. Example: '  Hello   World ' -> 'hello-world'. Edit only textlib.py.",
    },
}


def check(task, folder, stdout):
    if task == "read":
        return "MARKER: THETA-731" in stdout and (folder / "README.txt").read_text() == TASKS[task]["files"]["README.txt"]
    script = (
        "from mathlib import triangular\n"
        "assert [triangular(n) for n in (0,1,3,10)] == [0,1,6,55]\n"
        "try: triangular(-1)\n"
        "except ValueError: pass\n"
        "else: raise AssertionError('negative input')\n"
        if task == "bug" else
        "from textlib import slug\n"
        "assert slug('  Hello   World ') == 'hello-world'\n"
        "assert slug('A B') == 'a-b'\n"
        "assert slug('') == ''\n"
    )
    result = subprocess.run(["python3", "-c", script], cwd=folder, capture_output=True, text=True, timeout=10)
    return result.returncode == 0


def command(tool, model, prompt, folder):
    if tool == "v1":
        return [str(V1), "run", "--format", "json", "--auto", "--model", model, prompt]
    if tool == "v2":
        return [str(V2), "--standalone", "run", "--format", "json", "--auto", "--model", model, prompt]
    if tool == "pi":
        return ["bun", str(PI), "--mode", "json", "--print", "--no-session", "--model", model, prompt]
    return [CODEX, "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--sandbox", "workspace-write", "-C", str(folder), "--model", model, prompt]


def usage(tool, stdout):
    """Read native JSON events; null means a comparable value was not exposed."""
    values = []
    final_text = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            final_text.append(line)
            continue
        kind = event.get("type", "")
        if tool == "codex" and kind == "turn.completed":
            u = event.get("usage", {})
            values.append((u.get("input_tokens"), u.get("output_tokens"), u.get("cached_input_tokens")))
        elif tool == "v2" and kind == "step_finish":
            u = event.get("part", {}).get("tokens", {})
            values.append((u.get("input"), u.get("output"), u.get("cache", {}).get("read")))
        elif tool == "pi" and kind == "message_end":
            u = event.get("message", {}).get("usage", {})
            values.append((u.get("input"), u.get("output"), u.get("cacheRead")))
        elif tool == "v1" and kind == "step_finish":
            u = event.get("part", {}).get("tokens", {})
            values.append((u.get("input"), u.get("output"), u.get("cache", {}).get("read")))
        if kind == "text":
            final_text.append(event.get("part", {}).get("text", ""))
        elif tool == "codex" and kind == "item.completed" and event.get("item", {}).get("type") == "agent_message":
            final_text.append(event["item"].get("text", ""))
        elif tool == "pi" and kind == "message_end" and event.get("message", {}).get("role") == "assistant":
            final_text.extend(block.get("text", "") for block in event["message"].get("content", []) if block.get("type") == "text")
    def total(index):
        items = [v[index] for v in values if isinstance(v[index], (float, int))]
        return sum(items) if items else None
    return total(0), total(1), total(2), "\n".join(final_text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "experiments/benchmark.config.json"))
    parser.add_argument("--output", default=str(ROOT / "experiments/results"))
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for repeat in range(config["repeats"]):
        cases = [(task, tool, model) for task in TASKS for tool, model in config["models"].items()]
        random.Random(20261112 + repeat).shuffle(cases)
        for task, tool, model in cases:
                spec = TASKS[task]
                with tempfile.TemporaryDirectory(prefix=f"bench-{task}-{tool}-") as tmp:
                    folder = Path(tmp) / "fixture"
                    folder.mkdir()
                    for name, content in spec["files"].items():
                        (folder / name).write_text(content)
                    env = os.environ.copy()
                    env["PWD"] = str(folder)
                    env["XDG_DATA_HOME"] = str(Path(tmp) / "data")
                    env["XDG_CACHE_HOME"] = str(Path(tmp) / "cache")
                    started = time.perf_counter()
                    try:
                        run = subprocess.run(command(tool, model, spec["prompt"], folder), cwd=folder, env=env,
                                             capture_output=True, text=True, timeout=config["timeout_seconds"])
                        stdout, stderr, code, timeout = run.stdout, run.stderr, run.returncode, False
                    except subprocess.TimeoutExpired as exc:
                        stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout or ""
                        stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr or ""
                        code, timeout = None, True
                    elapsed = round(time.perf_counter() - started, 3)
                    input_tokens, output_tokens, cache_tokens, text = usage(tool, stdout)
                    passed = not timeout and code == 0 and check(task, folder, text)
                    key = f"{repeat+1}-{task}-{tool}"
                    (out / f"{key}.jsonl").write_text(stdout)
                    (out / f"{key}.stderr.txt").write_text(stderr)
                    row = dict(repeat=repeat+1, task=task, tool=tool, model=model, passed=passed,
                               timeout=timeout, exit_code=code, seconds=elapsed, input_tokens=input_tokens,
                               output_tokens=output_tokens, cache_read_tokens=cache_tokens)
                    rows.append(row)
                    print(json.dumps(row, ensure_ascii=False), flush=True)
    with (out / "runs.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()

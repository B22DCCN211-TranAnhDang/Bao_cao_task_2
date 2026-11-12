#!/usr/bin/env python3
"""Summarize benchmark CSV without hiding failed or missing-usage runs."""
import csv
from collections import defaultdict
from pathlib import Path
import statistics
import sys

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/runs.csv")
groups = defaultdict(list)
with path.open(newline="") as handle:
    for row in csv.DictReader(handle):
        groups[(row["task"], row["tool"])].append(row)

print("task,tool,passed,total,completion_rate,median_seconds,median_input_tokens,median_output_tokens,median_cache_read_tokens")
for (task, tool), rows in sorted(groups.items()):
    passed = sum(row["passed"] == "True" for row in rows)
    def median(field):
        values = [float(row[field]) for row in rows if row[field] != ""]
        return round(statistics.median(values), 3) if values else "unavailable"
    print(f"{task},{tool},{passed},{len(rows)},{passed/len(rows):.3f},{median('seconds')},{median('input_tokens')},{median('output_tokens')},{median('cache_read_tokens')}")

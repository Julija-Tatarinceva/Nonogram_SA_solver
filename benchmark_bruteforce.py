"""Measure complete-board enumeration; extrapolations are not full-search timings.

Rows always satisfy their clues. Each complete board is checked against column
clues, stopping that check at the first invalid column. No partial-board pruning
is used, and finding a solution does not stop the benchmark. Large spaces are
sampled in reproducible contiguous windows starting at random positions.
"""

import argparse
import csv
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import sys
import time

from nonogram_solver.puzzle import line_clues, make_clues, patterns, read_matrix


def combinations_from(options, start, count):
    """Enumerate a window of the Cartesian product without skipping its prefix."""
    total = math.prod(map(len, options))
    if start < 0 or count < 0 or start + count > total:
        raise ValueError("Window is outside the combination space.")
    indices = [0] * len(options)
    for row in range(len(options) - 1, -1, -1):
        start, indices[row] = divmod(start, len(options[row]))
    masks = [line[index] for line, index in zip(options, indices)]
    for _ in range(count):
        yield tuple(masks)
        for row in range(len(options) - 1, -1, -1):
            indices[row] += 1
            if indices[row] < len(options[row]):
                masks[row] = options[row][indices[row]]
                break
            indices[row] = 0
            masks[row] = options[row][0]


def valid_columns(masks, clues):
    return all(line_clues((mask >> column) & 1 for mask in masks) == clue
               for column, clue in enumerate(clues))


def processor_name():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
            return winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    except (ImportError, OSError):
        return platform.processor()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--samples", type=int, default=100_000, help="Complete boards per run; capped at the whole space")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-patterns", type=int, default=100_000)
    parser.add_argument("--csv", type=Path, default=Path("bruteforce_results/benchmark.csv"))
    args = parser.parse_args()
    if min(args.samples, args.runs, args.max_patterns) < 1:
        parser.error("samples, runs, and max-patterns must be positive")
    summary_path = args.csv.with_suffix(".json")
    if args.csv.exists() or summary_path.exists():
        parser.error("Output already exists; choose a new --csv filename.")
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    fields = ("input", "height", "width", "run", "seed", "combinations", "sample_start", "checked",
              "full_scan", "solutions_in_sample", "preparation_seconds_shared", "scan_seconds", "checks_per_second")
    metadata = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(), python=sys.version,
                    executable=sys.executable, platform=platform.platform(), processor=processor_name(),
                    logical_processors=os.cpu_count(), samples=args.samples, runs=args.runs, seed=args.seed,
                    max_patterns=args.max_patterns, results=[],
                    method="Full-board checks; no prefix pruning; never stops at the first solution. "
                           "Partial scans use random contiguous windows. Full-space times for partial scans are extrapolations.")
    rng = random.Random(args.seed)
    try:
        with args.csv.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for path in args.inputs:
                matrix = read_matrix(path)
                rows, columns = make_clues(matrix)
                started = time.perf_counter()
                options = [patterns(len(columns), clue, args.max_patterns) for clue in rows]
                total = math.prod(map(len, options))
                prepared = time.perf_counter() - started
                count = min(args.samples, total)
                scans, rates, solutions = [], [], []
                for run in range(args.runs):
                    start = 0 if count == total else rng.randrange(total - count + 1)
                    found = checked = 0
                    started = time.perf_counter()
                    for masks in combinations_from(options, start, count):
                        found += valid_columns(masks, columns)
                        checked += 1
                    elapsed = time.perf_counter() - started
                    assert checked == count
                    rate = checked / elapsed
                    writer.writerow(dict(input=str(path), height=len(rows), width=len(columns), run=run+1,
                                         seed=args.seed, combinations=str(total), sample_start=str(start),
                                         checked=checked, full_scan=int(count == total), solutions_in_sample=found,
                                         preparation_seconds_shared=prepared, scan_seconds=elapsed, checks_per_second=rate))
                    stream.flush()
                    scans.append(elapsed)
                    rates.append(rate)
                    solutions.append(found)
                    print(f"{path.name}: run {run+1}/{args.runs}; checked={checked}; "
                          f"time={elapsed:.6f}s; rate={rate:.0f}/s; solutions={found}; full={count == total}", flush=True)
                rate = count * args.runs / sum(scans)
                metadata["results"].append(dict(input=str(path), combinations=str(total), checked_per_run=count,
                    full_scan=count == total, preparation_seconds=prepared, scan_seconds_mean=statistics.mean(scans),
                    scan_seconds_sd=statistics.stdev(scans) if args.runs > 1 else None, checks_per_second=rate,
                    rate_min=min(rates), rate_max=max(rates), solutions_per_run=solutions,
                    full_scan_seconds_measured=statistics.mean(scans) if count == total else None,
                    full_scan_seconds_estimate_log10=None if count == total else math.log10(total)-math.log10(rate)))
                summary_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"CSV: {args.csv}; summary and machine metadata: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Console commands, benchmark CSV output, and optional animation.
# Keep the module docstring empty so argparse help remains unchanged.

import argparse
import csv
import math
import sys
import time
from pathlib import Path

from .puzzle import make_clues, read_matrix
from .solver import solve


def show_matrix(matrix):
    return "\n".join("".join("##" if cell else ".." for cell in row) for row in matrix)


def show_clues(rows, columns):
    print("Row clues:")
    for i, clue in enumerate(rows, 1):
        print(f"  {i:2}: {' '.join(map(str, clue)) or '0'}")
    print("Column clues:")
    for i, clue in enumerate(columns, 1):
        print(f"  {i:2}: {' '.join(map(str, clue)) or '0'}")


def animation(matrix, moves, temperature, score, best, *, delay=0.1):
    # ANSI output works in modern terminals; no terminal library is needed.
    print("\033[H\033[J" + show_matrix(matrix))
    print(f"Iteration: {moves}  T: {temperature:.4f}  Penalty: {score}  Best: {best}", flush=True)
    time.sleep(delay)


def add_search_options(parser):
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--iterations", type=int, default=100_000)
    parser.add_argument("--time-limit", type=float,
                        help="Search seconds per run; overrides iteration budget and disables restarts; cools by elapsed time")
    parser.add_argument("--restart-every", type=int, default=10_000)
    parser.add_argument("--start-temp", type=float, default=2.5)
    parser.add_argument("--end-temp", type=float, default=0.05)
    parser.add_argument("--max-patterns", type=int, default=100_000)
    parser.add_argument("--move", choices=("row", "mixed"), default="row",
                        help="Move operator (default: original row replacement)")
    parser.add_argument("--shift-probability", type=float, default=0.8,
                        help="Probability of a block-shift proposal in mixed mode, 0..1 (default: 0.8)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    single = commands.add_parser("solve", help="Solve clues derived from a binary matrix")
    single.add_argument("input", type=Path)
    single.add_argument("--animate", action="store_true")
    single.add_argument("--delay", type=float, default=0.1,
                        help="Pause in seconds after each animation frame (default: 0.1)")
    single.add_argument("--output", type=Path, help="Save best matrix as 0/1 text")
    add_search_options(single)
    bench = commands.add_parser("benchmark", help="Repeated runs; write detailed CSV")
    bench.add_argument("inputs", nargs="+", type=Path)
    bench.add_argument("--runs", type=int, default=20)
    bench.add_argument("--csv", type=Path, default=Path("results.csv"))
    add_search_options(bench)
    args = parser.parse_args()
    options = {name: getattr(args, name) for name in
               ("iterations", "restart_every", "start_temp", "end_temp", "max_patterns",
                "move", "shift_probability", "time_limit")}
    try:
        if args.command == "solve":
            if not math.isfinite(args.delay) or args.delay < 0:
                raise ValueError("--delay must be finite and nonnegative.")
            matrix = read_matrix(args.input)
            rows, columns = make_clues(matrix)
            show_clues(rows, columns)
            result = solve(rows, columns, seed=args.seed,
                           progress=(lambda *frame: animation(*frame, delay=args.delay))
                           if args.animate else None, **options)
            valid = make_clues(result.matrix) == (rows, columns)
            print("\nBest field:\n" + show_matrix(result.matrix))
            print(f"\nStatus: {'SOLVED' if valid else 'BUDGET EXHAUSTED'}")
            print(f"Penalty: {result.penalty}; known optimum: 0")
            print(f"Move: {args.move}; shift probability: {args.shift_probability if args.move == 'mixed' else 0}")
            print(f"Iterations: {result.iterations}; restarts: {result.restarts}")
            print(f"Stop reason: {result.stop_reason}")
            print(f"Preparation: {result.preparation_seconds:.6f} s; "
                  f"search: {result.search_seconds:.6f} s; total: {result.total_seconds:.6f} s")
            if args.output:
                if args.output.resolve() == args.input.resolve():
                    raise ValueError("Output must differ from the input file.")
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text("\n".join("".join(map(str, row)) for row in result.matrix)
                                       + "\n", encoding="utf-8")
            return 0 if valid else 2
        if args.runs < 1:
            raise ValueError("--runs must be positive.")
        if args.csv.resolve() in {path.resolve() for path in args.inputs}:
            raise ValueError("CSV output must differ from input files.")
        puzzles = [(path, make_clues(read_matrix(path))) for path in args.inputs]
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        fields = ["input", "height", "width", "seed", "solved", "penalty", "optimum",
                  "iterations", "restarts", "preparation_seconds", "search_seconds",
                  "total_seconds", "budget", "restart_every", "start_temp", "end_temp",
                  "max_patterns", "move", "shift_probability", "time_limit", "cooling", "stop_reason"]
        with args.csv.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for path, (rows, columns) in puzzles:
                successes, elapsed, penalties = 0, [], []
                for run in range(args.runs):
                    seed = args.seed + run
                    result = solve(rows, columns, seed=seed, **options)
                    valid = make_clues(result.matrix) == (rows, columns)
                    record = {"input": str(path), "height": len(rows), "width": len(columns),
                              "seed": seed, "solved": int(valid), "optimum": 0,
                              "budget": args.iterations if args.time_limit is None else "",
                              "cooling": "time" if args.time_limit is not None else "iterations",
                              **{key: options[key] for key in options if key != "iterations"},
                              **{key: getattr(result, key) for key in fields if hasattr(result, key)}}
                    if args.time_limit is not None:
                        record["restart_every"] = ""
                    writer.writerow(record)
                    stream.flush()
                    successes += valid
                    elapsed.append(result.total_seconds)
                    penalties.append(result.penalty)
                    print(f"{path.name}: run {run + 1}/{args.runs}, "
                          f"penalty={result.penalty}, time={result.total_seconds:.4f}s", flush=True)
                print(f"Summary: {successes}/{args.runs} solved; "
                      f"mean penalty={sum(penalties)/args.runs:.2f}; "
                      f"mean total time={sum(elapsed)/args.runs:.4f}s")
        print(f"CSV saved: {args.csv}")
        return 0
    except (OSError, ValueError, RecursionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

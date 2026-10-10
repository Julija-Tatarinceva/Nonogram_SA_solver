"""Simulated annealing: initialization, proposals, cooling, and acceptance."""

import itertools
import math
import random
import time
from dataclasses import dataclass

from .evaluation import LineDistance
from .moves import shift_block
from .puzzle import patterns


@dataclass
class Result:
    matrix: list
    penalty: int
    iterations: int
    restarts: int
    preparation_seconds: float
    search_seconds: float
    total_seconds: float
    stop_reason: str


def solve(row_clues, column_clues, *, seed=0, iterations=100_000,
          restart_every=10_000, start_temp=2.5, end_temp=0.05,
          max_patterns=200_000, progress=None, move="row", shift_probability=0.8,
          time_limit=None):
    """Minimize column distances while keeping every row valid.

    Row mode replaces a row; mixed mode also proposes one-cell block shifts.
    delta <= 0: accept; otherwise accept with probability exp(-delta / T).
    T cools geometrically within each restart. The global best is retained.
    """
    if iterations < 1 or restart_every < 1 or max_patterns < 1:
        raise ValueError("Iteration counts and max_patterns must be positive.")
    if time_limit is not None and (not math.isfinite(time_limit) or time_limit <= 0):
        raise ValueError("time_limit must be finite and positive.")
    if move not in ("row", "mixed"):
        raise ValueError("Move must be row or mixed.")
    if not math.isfinite(shift_probability) or not 0 <= shift_probability <= 1:
        raise ValueError("shift_probability must be between 0 and 1.")
    if not (math.isfinite(start_temp) and math.isfinite(end_temp) and 0 < end_temp <= start_temp):
        raise ValueError("Temperatures must be finite and 0 < end <= start.")
    height, width = len(row_clues), len(column_clues)
    if not height or not width:
        raise ValueError("The puzzle must have rows and columns.")
    started = time.perf_counter()
    row_options = [patterns(width, clue, max_patterns) for clue in row_clues]
    row_indices = ([{mask: i for i, mask in enumerate(options)} for options in row_options]
                   if move == "mixed" and shift_probability > 0 else None)
    column_options = [patterns(height, clue, max_patterns) for clue in column_clues]
    mutable = [r for r in range(height) if len(row_options[r]) > 1]
    # Call the cached wrappers directly in the hot loop.
    distances = [LineDistance(options, black_count=sum(clue)).cache
                 for options, clue in zip(column_options, column_clues)]

    def distance(c, mask):
        return distances[c](mask)

    def unpack(masks):
        return [[(mask >> c) & 1 for c in range(width)] for mask in masks]

    prepared = time.perf_counter()
    rng = random.Random(seed)
    best_score, best_rows = math.inf, None
    moves, restarts = 0, -1
    timed_out = False
    while (time_limit is not None or moves < iterations) and best_score != 0:
        restarts += 1
        indices = [rng.randrange(len(options)) for options in row_options]
        rows = [options[i] for options, i in zip(row_options, indices)]
        columns = [sum(((rows[r] >> c) & 1) << r for r in range(height))
                   for c in range(width)]
        penalties = [distance(c, column) for c, column in enumerate(columns)]
        score = sum(penalties)
        if score < best_score:
            best_score, best_rows = score, rows[:]
        if progress:
            progress(unpack(rows), moves, start_temp, score, best_score)
        steps = min(restart_every, iterations - moves)
        for step in (itertools.count() if time_limit is not None else range(steps)):
            if best_score == 0 or not mutable:
                break
            if time_limit is not None:
                elapsed = time.perf_counter() - prepared
                if elapsed >= time_limit:
                    timed_out = True
                    break
                fraction = elapsed / time_limit
            else:
                fraction = step / max(1, steps - 1)
            temperature = start_temp * (end_temp / start_temp) ** fraction
            r = rng.choice(mutable)
            if move == "mixed" and shift_probability > 0 and rng.random() < shift_probability:
                block_index = rng.randrange(len(row_clues[r]))
                direction = rng.choice((-1, 1))
                candidate = shift_block(rows[r], width, block_index, direction)
                if candidate == rows[r]:
                    # Blocked proposals consume one iteration, without an animation frame.
                    moves += 1
                    continue
                candidate_index = row_indices[r][candidate]
            else:
                # Uniformly select any pattern except the current one.
                candidate_index = rng.randrange(len(row_options[r]) - 1)
                if candidate_index >= indices[r]:
                    candidate_index += 1
                candidate = row_options[r][candidate_index]
            changes = rows[r] ^ candidate
            updates = []
            delta = 0
            while changes:
                bit = changes & -changes
                c = bit.bit_length() - 1
                column = columns[c] ^ (1 << r)
                penalty = 1 if penalties[c] == 0 else distance(c, column)
                updates.append((c, column, penalty))
                delta += penalty - penalties[c]
                changes ^= bit
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                rows[r], indices[r] = candidate, candidate_index
                for c, column, penalty in updates:
                    columns[c], penalties[c] = column, penalty
                score += delta
                if score < best_score:
                    best_score, best_rows = score, rows[:]
                if progress:
                    progress(unpack(rows), moves + 1, temperature, score, best_score)
            moves += 1
        if not mutable or timed_out:
            break
    finished = time.perf_counter()
    reason = ("solved" if best_score == 0 else "time_limit" if timed_out
              else "no_moves" if not mutable else "iteration_limit")
    return Result(unpack(best_rows), int(best_score), moves, restarts,
                  prepared - started, finished - prepared, finished - started, reason)

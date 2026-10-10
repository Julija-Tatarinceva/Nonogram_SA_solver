"""Read binary matrices, derive clues, and generate valid line patterns."""

import math
from pathlib import Path


def read_matrix(path):
    """Read 0101 or space-separated 0 1 0 1; allow blank lines and # comments."""
    matrix = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.split("#", 1)[0]
        cells = "".join(line.split())
        if not cells:
            continue
        if set(cells) - {"0", "1"}:
            raise ValueError(f"Line {number}: only 0 and 1 are allowed.")
        if matrix and len(cells) != len(matrix[0]):
            raise ValueError(f"Line {number}: inconsistent row length.")
        matrix.append([int(cell) for cell in cells])
    if not matrix:
        raise ValueError("The input matrix is empty.")
    return matrix


def line_clues(cells):
    blocks, length = [], 0
    for cell in cells:
        if cell:
            length += 1
        elif length:
            blocks.append(length)
            length = 0
    if length:
        blocks.append(length)
    return tuple(blocks)


def make_clues(matrix):
    return (tuple(line_clues(row) for row in matrix),
            tuple(line_clues(column) for column in zip(*matrix)))


def patterns(length, clues, limit=100_000):
    """Generate all valid line masks by placing blocks, not by enumerating 2^n.

    There are C(length - sum(clues) + 1, len(clues)) placements.
    Refuse excessive lists before allocating them.
    """
    if any(block <= 0 for block in clues):
        raise ValueError("Clue lengths must be positive.")
    required = sum(clues) + max(0, len(clues) - 1)
    if required > length:
        raise ValueError("Clues do not fit the line.")
    count = math.comb(length - sum(clues) + 1, len(clues))
    if count > limit:
        raise ValueError(f"A line requires {count} patterns (limit {limit}). "
                         "Use a smaller puzzle or increase --max-patterns.")
    result = []

    def place(index, start, mask):
        if index == len(clues):
            result.append(mask)
            return
        remaining = sum(clues[index:]) + len(clues) - index - 1
        block_mask = (1 << clues[index]) - 1
        for position in range(start, length - remaining + 1):
            place(index + 1, position + clues[index] + 1,
                  mask | (block_mask << position))

    place(0, 0, 0)
    return tuple(result)

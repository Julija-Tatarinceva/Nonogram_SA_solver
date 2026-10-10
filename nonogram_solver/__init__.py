"""Public API for the nonogram model and simulated annealing solver."""

from .evaluation import LineDistance
from .moves import shift_block
from .puzzle import line_clues, make_clues, patterns, read_matrix
from .solver import Result, solve

__all__ = [
    "LineDistance",
    "Result",
    "line_clues",
    "make_clues",
    "patterns",
    "read_matrix",
    "shift_block",
    "solve",
]

# Entry point and compatible imports for existing scripts.
import time  # Existing timer patches through nonogram.time still work.

from nonogram_solver import (
    LineDistance,
    Result,
    line_clues,
    make_clues,
    patterns,
    read_matrix,
    shift_block,
    solve,
)
from nonogram_solver.cli import add_search_options, animation, main, show_clues, show_matrix


if __name__ == "__main__":
    raise SystemExit(main())

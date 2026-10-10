"""Exact column penalties with a separate bounded cache per column."""

import math
from functools import lru_cache


class LineDistance:
    """Exact Hamming distance with a bounded least-recently-used cache."""

    def __init__(self, options, cache_limit=4096, *, black_count=None):
        if cache_limit < 1:
            raise ValueError("Cache limit must be positive.")
        self.options = options
        self.cache_limit = cache_limit

        # A separate wrapper per column keeps its own bounded cache.
        # Capture options directly, avoiding a reference cycle through self.
        @lru_cache(maxsize=cache_limit)
        def cached_distance(mask):
            lower_bound = abs(mask.bit_count() - black_count) if black_count is not None else 0
            best = math.inf
            for option in options:
                distance = (mask ^ option).bit_count()
                if distance < best:
                    best = distance
                    if best == lower_bound:
                        break
            return best

        self.cache = cached_distance

    def __call__(self, mask):
        return self.cache(mask)

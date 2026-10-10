"""Moves that preserve the row clues."""


def shift_block(mask, width, block_index, direction):
    """Shift a block one cell, returning the original mask if blocked."""
    if direction not in (-1, 1):
        raise ValueError("Direction must be -1 or 1.")
    blocks = []
    c = 0
    while c < width:
        if (mask >> c) & 1:
            start = c
            while c < width and (mask >> c) & 1:
                c += 1
            blocks.append((start, c))
        else:
            c += 1
    start, end = blocks[block_index]
    new_start, new_end = start + direction, end + direction
    if new_start < 0 or new_end > width:
        return mask
    if block_index > 0 and new_start <= blocks[block_index - 1][1]:
        return mask
    if block_index + 1 < len(blocks) and new_end >= blocks[block_index + 1][0]:
        return mask
    block = (1 << (end - start)) - 1
    return (mask ^ (block << start)) | (block << new_start)

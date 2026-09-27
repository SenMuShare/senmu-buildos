def total(subtotal: int, discount: int) -> int:
    result = subtotal - discount
    if result < 0:
        raise ValueError("negative total")
    return result

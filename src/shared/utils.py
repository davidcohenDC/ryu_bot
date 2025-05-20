def between(value: int, lower: int, upper: int, *, inclusive: bool = False) -> bool:
    """
    Return True if `value` is between `lower` and `upper`.

    Default: inclusive=False → checks lower ≤ value < upper
    """
    return lower <= value <= upper if inclusive else lower <= value < upper

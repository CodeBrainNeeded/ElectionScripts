from __future__ import annotations


def flexibleContains(contain1: object, contain2: object) -> bool:
    """Check whether one string contains another, ignoring case and whitespace."""
    if not isinstance(contain1, str) or not isinstance(contain2, str):
        return False

    short_contain = contain2 if len(contain1) > len(contain2) else contain1
    long_contain = contain1 if len(contain1) > len(contain2) else contain2
    return simplifyString(short_contain) in simplifyString(long_contain) and short_contain.strip() and long_contain.strip()


def simplifyString(value: object) -> str:
    """Normalize a string for comparison."""
    return str(value).strip().lower()

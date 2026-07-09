from __future__ import annotations

from VotingHelpers import flexibleContains


class Candidate:
    """Represents a single candidate running for a position."""

    def __init__(self, name: str):
        self.name: str = name.strip()
        self.borda: int = 0
        self.currentVotes: int = 0
        self.firstVotes: int = 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Candidate):
            return False
        return flexibleContains(self.name, other.name) or flexibleContains(other.name, self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

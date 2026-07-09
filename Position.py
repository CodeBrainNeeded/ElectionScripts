from __future__ import annotations

import copy
from typing import List, Optional

from Candidate import Candidate
from VotingHelpers import simplifyString


class Position:
    """Represents a single office and the ballots cast for it."""

    def __init__(self, name: str, numPossibleWinners: int, votes: Optional[List[List[str]]] = None):
        self.name: str = name.strip()
        self.numPossibleWinners: int = int(numPossibleWinners)
        self.indexInCSV: int = -1
        self.votes: List[List[str]] = []
        self.candidates: List[Candidate] = []
        self.winners: List[Candidate] = []
        self.originalVotes: List[List[str]] = []

        if votes:
            self.votes = [
                [entry.strip() for entry in vote if str(entry).strip()]
                for vote in votes
            ]
            self.originalVotes = copy.deepcopy(self.votes)

        self.findCandidates()
        self.calculateBorda()
        self.calculateFirstVotes()

    def __str__(self) -> str:
        return f"{self.name} ({self.numPossibleWinners} winner(s))"

    def __repr__(self) -> str:
        return self.__str__()

    def findCandidates(self) -> None:
        """Collect the distinct candidates from the ballot data."""
        seen: set[str] = set()
        self.candidates = []

        for vote in self.votes:
            for item in vote:
                normalized = simplifyString(item)
                if normalized and normalized not in seen:
                    self.candidates.append(Candidate(str(item).strip()))
                    seen.add(normalized)

        self.winners = list(self.candidates)

    def calculateBorda(self) -> None:
        """Assign each candidate a Borda score based on every ballot."""
        for candidate in self.candidates:
            candidate.borda = 0

        for candidate in self.candidates:
            for vote in self.votes:
                for index, ballot_name in enumerate(vote):
                    if simplifyString(str(ballot_name)) == simplifyString(candidate.name):
                        candidate.borda += len(vote) - index
                        break

    def calculateFirstVotes(self) -> None:
        """Count first-choice votes for the current ballot set."""
        for candidate in self.candidates:
            candidate.currentVotes = 0
            candidate.firstVotes = 0

        for vote in self.votes:
            if not vote:
                continue
            first_choice = vote[0]
            for candidate in self.candidates:
                if simplifyString(str(first_choice)) == simplifyString(candidate.name):
                    candidate.firstVotes += 1
                    candidate.currentVotes += 1
                    break

    def copyAndRemoveCandidate(self, candidate: Candidate) -> "Position":
        """Return a deep copy of the position with one candidate removed."""
        copied_position = copy.deepcopy(self)
        copied_position.votes = [
            [name for name in vote if simplifyString(str(name)) != simplifyString(candidate.name)]
            for vote in copied_position.votes
        ]
        copied_position.candidates = [
            active_candidate
            for active_candidate in copied_position.candidates
            if simplifyString(active_candidate.name) != simplifyString(candidate.name)
        ]
        copied_position.winners = [
            active_candidate
            for active_candidate in copied_position.winners
            if simplifyString(active_candidate.name) != simplifyString(candidate.name)
        ]
        copied_position.calculateBorda()
        copied_position.calculateFirstVotes()
        return copied_position

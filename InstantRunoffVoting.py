from __future__ import annotations

import random
from typing import List, Optional

from Candidate import Candidate
from Position import Position
from VotingHelpers import simplifyString

try:
    from Election import getAndCheckStringInput
except ImportError:  # pragma: no cover - allows tests to import this module directly
    def getAndCheckStringInput(valid_inputs: List[str]) -> str:
        response = input().strip()
        for valid_input in valid_inputs:
            if valid_input.lower() == response.lower():
                return response
        print("Invalid input. Please try again.")
        return getAndCheckStringInput(valid_inputs)


class InstantRunoffVoting:
    """Run single-winner or multi-winner elections through IRV."""

    def __init__(self, positions: Optional[List[Position]] = None):
        self.positions: List[Position] = positions or []

    def run(self, positions: Optional[List[Position]] = None) -> None:
        """Run the election and resolve any conflicts for multiple wins."""
        active_positions = positions or self.positions
        for position in active_positions:
            self.recurseCalculate(position)
        self.checkForMultiple(active_positions)

    def recurseCalculate(self, position: Position) -> List[Candidate]:
        """Eliminate the weakest candidate until the target number of winners remains."""
        if len(position.winners) <= position.numPossibleWinners:
            return position.winners

        position.calculateFirstVotes()
        candidateToRemove = self._selectCandidateToRemove(position)
        if candidateToRemove is None:
            return position.winners

        next_position = position.copyAndRemoveCandidate(candidateToRemove)
        return self.recurseCalculate(next_position)

    def _selectCandidateToRemove(self, position: Position) -> Optional[Candidate]:
        """Choose the candidate with the fewest first-choice votes, breaking ties with Borda and first-vote counts."""
        if not position.candidates:
            return None

        candidateToRemove = position.candidates[0]
        for candidate in position.candidates[1:]:
            if candidate.currentVotes < candidateToRemove.currentVotes:
                candidateToRemove = candidate
            elif candidate.currentVotes == candidateToRemove.currentVotes:
                if candidate.borda < candidateToRemove.borda:
                    candidateToRemove = candidate
                elif candidate.borda == candidateToRemove.borda:
                    if candidate.firstVotes < candidateToRemove.firstVotes:
                        candidateToRemove = candidate
                    elif candidate.firstVotes == candidateToRemove.firstVotes and random.random() < 0.5:
                        candidateToRemove = candidate
        return candidateToRemove

    def checkForMultiple(self, positions: List[Position]) -> None:
        """Prompt the user to resolve cases where one person wins multiple positions."""
        winnerToPosition: dict[str, List[Position]] = {}
        for position in positions:
            for winner in position.winners:
                winner_key = simplifyString(winner.name)
                winnerToPosition.setdefault(winner_key, []).append(position)

        for winner_key, involved_positions in winnerToPosition.items():
            if len(involved_positions) < 2:
                continue

            winner_name = involved_positions[0].winners[0].name if involved_positions else ""
            first_position = involved_positions[0]
            second_position = involved_positions[1]
            print(f"{winner_name} has won more than one position. Choose which position they should keep.")
            print(f"A: Keep {first_position.name} and recalculate {second_position.name}")
            print(f"B: Keep {second_position.name} and recalculate {first_position.name}")
            choice = getAndCheckStringInput(["A", "B"]).upper()

            if choice == "A":
                target_position = second_position
            else:
                target_position = first_position

            target_position_copy = target_position.copyAndRemoveCandidate(
                next(candidate for candidate in target_position.winners if simplifyString(candidate.name) == winner_key)
            )
            self.recurseCalculate(target_position_copy)
            return self.checkForMultiple(positions)

        return None

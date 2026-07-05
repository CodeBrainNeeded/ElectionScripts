from __future__ import annotations

import itertools
from typing import List, Optional

from Candidate import Candidate
from InstantRunoffVoting import InstantRunoffVoting
from Position import Position
from VotingHelpers import simplifyString


class CondorcetVoting(InstantRunoffVoting):
    """Run elections using a sequential Condorcet approach with pairwise majority comparisons."""

    def recurseCalculate(self, position: Position) -> List[Candidate]:
        """Select a winner from pairwise contests until the target number of winners remains."""
        if len(position.winners) <= position.numPossibleWinners:
            return position.winners

        winner = self._selectCondorcetWinner(position)
        if winner is None:
            return position.winners

        if position.numPossibleWinners == 1:
            position.winners = [winner]
            return position.winners

        next_position = position.copyAndRemoveCandidate(winner)
        return self.recurseCalculate(next_position)

    def _selectCondorcetWinner(self, position: Position) -> Optional[Candidate]:
        """Find a pairwise majority winner, or fall back to the strongest ranked-pairs outcome."""
        if not position.candidates:
            return None
        if len(position.candidates) == 1:
            return position.candidates[0]

        pairwise_scores = self._buildPairwiseScores(position)
        for candidate in position.candidates:
            if self._beatsAll(candidate, position.candidates, pairwise_scores):
                return candidate

        return self._rankedPairsWinner(position.candidates, pairwise_scores)

    def _buildPairwiseScores(self, position: Position) -> dict[str, dict[str, int]]:
        """Construct a pairwise comparison matrix for the active candidates."""
        scores: dict[str, dict[str, int]] = {}
        for candidate in position.candidates:
            scores[candidate.name] = {}
            for opponent in position.candidates:
                scores[candidate.name][opponent.name] = 0

        for left_candidate, right_candidate in itertools.combinations(position.candidates, 2):
            left_name = left_candidate.name
            right_name = right_candidate.name
            left_wins = 0
            right_wins = 0
            for ballot in position.votes:
                left_rank = self._rankForCandidate(ballot, left_candidate)
                right_rank = self._rankForCandidate(ballot, right_candidate)
                if left_rank < right_rank:
                    left_wins += 1
                elif right_rank < left_rank:
                    right_wins += 1

            scores[left_name][right_name] = left_wins
            scores[right_name][left_name] = right_wins

        return scores

    def _rankForCandidate(self, ballot: List[str], candidate: Candidate) -> int:
        """Return the rank of a candidate on a ballot, treating missing candidates as last."""
        for index, ballot_name in enumerate(ballot):
            if simplifyString(str(ballot_name)) == simplifyString(candidate.name):
                return index
        return len(ballot)

    def _beatsAll(self, candidate: Candidate, candidates: List[Candidate], scores: dict[str, dict[str, int]]) -> bool:
        """Return True when the candidate beats every other active candidate pairwise."""
        for opponent in candidates:
            if candidate.name == opponent.name:
                continue
            if scores[candidate.name][opponent.name] <= scores[opponent.name][candidate.name]:
                return False
        return True

    def _rankedPairsWinner(self, candidates: List[Candidate], scores: dict[str, dict[str, int]]) -> Optional[Candidate]:
        """Fall back to an approximate ranked-pairs winner when no Condorcet winner exists."""
        pairwise_edges: List[tuple[int, Candidate, Candidate]] = []
        for left, right in itertools.combinations(candidates, 2):
            margin = scores[left.name][right.name] - scores[right.name][left.name]
            pairwise_edges.append((margin, left, right))

        pairwise_edges.sort(key=lambda item: abs(item[0]), reverse=True)
        locked_edges: List[tuple[Candidate, Candidate]] = []
        for _, left, right in pairwise_edges:
            if not self._createsCycle(locked_edges, left, right):
                locked_edges.append((left, right))

        wins: dict[str, int] = {candidate.name: 0 for candidate in candidates}
        for left, right in locked_edges:
            if scores[left.name][right.name] > scores[right.name][left.name]:
                wins[left.name] += 1
            else:
                wins[right.name] += 1

        if not wins:
            return candidates[0]
        best_name = max(wins.items(), key=lambda item: (item[1], item[0]))[0]
        return next(candidate for candidate in candidates if candidate.name == best_name)

    def _createsCycle(self, edges: List[tuple[Candidate, Candidate]], left: Candidate, right: Candidate) -> bool:
        """Check whether adding an edge would create a cycle in the locked set."""
        if (left, right) in edges or (right, left) in edges:
            return True

        graph: dict[str, set[str]] = {left.name: set(), right.name: set()}
        for start, end in edges:
            graph[start.name].add(end.name)
            graph[end.name].add(start.name)
        graph[left.name].add(right.name)
        graph[right.name].add(left.name)

        visited: set[str] = set()
        stack: List[str] = [left.name]
        while stack:
            current = stack.pop()
            if current == right.name:
                return True
            if current in visited:
                continue
            visited.add(current)
            stack.extend(graph[current])
        return False

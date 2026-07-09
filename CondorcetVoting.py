from __future__ import annotations

import itertools
import random
from copy import deepcopy
from typing import List, Optional

from Candidate import Candidate
from InstantRunoffVoting import InstantRunoffVoting
from Position import Position
from VotingHelpers import simplifyString


class CondorcetVoting(InstantRunoffVoting):
    """Run elections using a sequential Condorcet approach with pairwise majority comparisons."""

    def recurseCalculate(self, position: Position) -> List[Candidate]:
        """Select a winner from pairwise contests until the target number of winners remains."""
        if position.numPossibleWinners <= 0:
            return []

        if len(position.candidates) <= position.numPossibleWinners:
            return list(position.candidates)

        winner = self._selectCondorcetWinner(position)
        if winner is None:
            return list(position.candidates[: position.numPossibleWinners])

        if position.numPossibleWinners == 1:
            position.winners = [winner]
            return position.winners

        next_position = self._copyAndRemoveCandidateWithoutScoreRecompute(position, winner)
        next_position.numPossibleWinners = position.numPossibleWinners - 1

        remaining_winners = self.recurseCalculate(next_position)
        selected_winners = [winner]
        selected_winners.extend(remaining_winners)
        return selected_winners

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

    def _copyAndRemoveCandidateWithoutScoreRecompute(self, position: Position, candidate: Candidate) -> Position:
        """Copy a position and remove one candidate while preserving existing Borda and first-vote values."""
        copied_position = deepcopy(position)
        candidate_key = simplifyString(candidate.name)
        copied_position.votes = [
            [name for name in vote if simplifyString(str(name)) != candidate_key]
            for vote in copied_position.votes
        ]
        copied_position.candidates = [
            active_candidate
            for active_candidate in copied_position.candidates
            if simplifyString(active_candidate.name) != candidate_key
        ]
        copied_position.winners = [
            active_candidate
            for active_candidate in copied_position.winners
            if simplifyString(active_candidate.name) != candidate_key
        ]
        return copied_position

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
            if self._compareHeadToHead(candidate, opponent, scores) <= 0:
                return False
        return True

    def _compareHeadToHead(
        self,
        left: Candidate,
        right: Candidate,
        scores: dict[str, dict[str, int]],
    ) -> int:
        """Compare two candidates head-to-head with Planning.md tie-breakers."""
        left_votes = scores[left.name][right.name]
        right_votes = scores[right.name][left.name]
        if left_votes != right_votes:
            return left_votes - right_votes

        if left.borda != right.borda:
            return left.borda - right.borda

        if left.firstVotes != right.firstVotes:
            return left.firstVotes - right.firstVotes

        return 1 if random.random() < 0.5 else -1

    def _rankedPairsWinner(self, candidates: List[Candidate], scores: dict[str, dict[str, int]]) -> Optional[Candidate]:
        """Fall back to an approximate ranked-pairs winner when no Condorcet winner exists."""
        pairwise_edges: List[tuple[int, int, int, str, str, Candidate, Candidate]] = []
        for left, right in itertools.combinations(candidates, 2):
            comparison = self._compareHeadToHead(left, right, scores)
            if comparison > 0:
                winner = left
                loser = right
            else:
                winner = right
                loser = left

            margin = abs(scores[left.name][right.name] - scores[right.name][left.name])
            borda_delta = winner.borda - loser.borda
            first_vote_delta = winner.firstVotes - loser.firstVotes
            pairwise_edges.append(
                (
                    margin,
                    borda_delta,
                    first_vote_delta,
                    simplifyString(winner.name),
                    simplifyString(loser.name),
                    winner,
                    loser,
                )
            )

        pairwise_edges.sort(key=lambda item: (item[0], item[1], item[2], item[3], item[4]), reverse=True)

        locked_graph: dict[str, set[str]] = {candidate.name: set() for candidate in candidates}
        for _, _, _, _, _, winner, loser in pairwise_edges:
            if not self._createsCycle(locked_graph, winner.name, loser.name):
                locked_graph[winner.name].add(loser.name)

        if not locked_graph:
            return candidates[0]

        incoming_counts: dict[str, int] = {candidate.name: 0 for candidate in candidates}
        for winners_over in locked_graph.values():
            for loser_name in winners_over:
                incoming_counts[loser_name] += 1

        best_name = min(incoming_counts.items(), key=lambda item: (item[1], simplifyString(item[0])))[0]
        return next(candidate for candidate in candidates if candidate.name == best_name)

    def _createsCycle(self, graph: dict[str, set[str]], winner: str, loser: str) -> bool:
        """Check whether locking winner -> loser would create a directed cycle."""
        visited: set[str] = set()
        stack: List[str] = [loser]
        while stack:
            current = stack.pop()
            if current == winner:
                return True
            if current in visited:
                continue
            visited.add(current)
            stack.extend(graph.get(current, set()))
        return False

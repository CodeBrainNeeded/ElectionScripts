import unittest

from Candidate import Candidate
from Position import Position
from InstantRunoffVoting import InstantRunoffVoting
from CondorcetVoting import CondorcetVoting


class PositionTests(unittest.TestCase):
    def test_position_collects_candidates_and_calculates_scores(self):
        position = Position(
            "President",
            1,
            [
                ["Alice", "Bob", "Carol"],
                ["Bob", "Alice", "Carol"],
                ["Carol", "Bob", "Alice"],
            ],
        )

        self.assertEqual([candidate.name for candidate in position.candidates], ["Alice", "Bob", "Carol"])
        self.assertEqual(position.candidates[0].firstVotes, 1)
        self.assertEqual(position.candidates[1].firstVotes, 1)
        self.assertEqual(position.candidates[2].firstVotes, 1)


class InstantRunoffVotingTests(unittest.TestCase):
    def test_irv_selects_the_candidate_with_the_majority_of_transferable_votes(self):
        position = Position(
            "President",
            1,
            [
                ["Alice", "Bob", "Carol"],
                ["Alice", "Bob", "Carol"],
                ["Bob", "Alice", "Carol"],
                ["Carol", "Bob", "Alice"],
            ],
        )

        engine = InstantRunoffVoting()
        winners = engine.recurseCalculate(position)

        self.assertEqual([candidate.name for candidate in winners], ["Alice"])


class CondorcetVotingTests(unittest.TestCase):
    def test_condorcet_selects_the_pairwise_majority_winner(self):
        position = Position(
            "President",
            1,
            [
                ["Alice", "Bob", "Carol"],
                ["Alice", "Carol", "Bob"],
                ["Bob", "Carol", "Alice"],
            ],
        )

        engine = CondorcetVoting()
        winners = engine.recurseCalculate(position)

        self.assertEqual([candidate.name for candidate in winners], ["Alice"])


if __name__ == "__main__":
    unittest.main()

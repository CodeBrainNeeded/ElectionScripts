import unittest
from unittest.mock import patch

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
                ["Alice", "Carol", "Bob"],
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

    def test_condorcet_multiwinner_keeps_selected_winners_across_recursion(self):
        position = Position(
            "Co-President",
            2,
            [
                ["Alice", "Bob", "Carol"],
                ["Alice", "Carol", "Bob"],
                ["Bob", "Carol", "Alice"],
            ],
        )

        engine = CondorcetVoting()
        winners = engine.recurseCalculate(position)

        self.assertEqual([candidate.name for candidate in winners], ["Alice", "Bob"])

    def test_condorcet_head_to_head_tie_breaks_by_borda_then_first_votes(self):
        position = Position(
            "President",
            1,
            [
                ["Alice", "Bob"],
                ["Bob", "Alice"],
            ],
        )
        alice = next(candidate for candidate in position.candidates if candidate.name == "Alice")
        bob = next(candidate for candidate in position.candidates if candidate.name == "Bob")

        # Pairwise votes are tied, so Borda decides this case.
        alice.borda = 10
        bob.borda = 11
        alice.firstVotes = 1
        bob.firstVotes = 1

        engine = CondorcetVoting()
        winner = engine._selectCondorcetWinner(position)
        self.assertIsNotNone(winner)
        if winner is None:
            self.fail("Expected a winner for tied head-to-head with Borda tie-break")
        self.assertEqual(winner.name, "Bob")

        # With Borda tied too, first-choice votes decide.
        alice.borda = 11
        bob.borda = 11
        alice.firstVotes = 2
        bob.firstVotes = 1
        winner = engine._selectCondorcetWinner(position)
        self.assertIsNotNone(winner)
        if winner is None:
            self.fail("Expected a winner for tied head-to-head with first-vote tie-break")
        self.assertEqual(winner.name, "Alice")

    def test_condorcet_head_to_head_random_tie_break_is_used_last(self):
        position = Position(
            "President",
            1,
            [
                ["Alice", "Bob"],
                ["Bob", "Alice"],
            ],
        )
        alice = next(candidate for candidate in position.candidates if candidate.name == "Alice")
        bob = next(candidate for candidate in position.candidates if candidate.name == "Bob")
        alice.borda = bob.borda = 10
        alice.firstVotes = bob.firstVotes = 1

        engine = CondorcetVoting()
        with patch("CondorcetVoting.random.random", return_value=0.25):
            winner = engine._selectCondorcetWinner(position)
            self.assertIsNotNone(winner)
            if winner is None:
                self.fail("Expected random tie-break to choose a winner")
            self.assertEqual(winner.name, "Alice")

        with patch("CondorcetVoting.random.random", return_value=0.75):
            winner = engine._selectCondorcetWinner(position)
            self.assertIsNotNone(winner)
            if winner is None:
                self.fail("Expected random tie-break to choose a winner")
            self.assertEqual(winner.name, "Bob")

    def test_condorcet_recursion_does_not_recompute_borda_between_rounds(self):
        position = Position(
            "Co-President",
            2,
            [
                ["Alice", "Bob", "Carol"],
                ["Alice", "Carol", "Bob"],
                ["Bob", "Alice", "Carol"],
                ["Carol", "Alice", "Bob"],
            ],
        )

        engine = CondorcetVoting()
        with patch.object(Position, "calculateBorda", side_effect=AssertionError("calculateBorda should not run in Condorcet recursion")):
            winners = engine.recurseCalculate(position)

        self.assertEqual(len(winners), 2)

    def test_condorcet_cycle_uses_ranked_pairs_fallback(self):
        # Classic cycle: A > B, B > C, C > A (no Condorcet winner).
        position = Position(
            "Cycle",
            1,
            [
                ["A", "B", "C"],
                ["B", "C", "A"],
                ["C", "A", "B"],
                ["A", "B", "C"],
                ["B", "C", "A"],
                ["C", "A", "B"],
            ],
        )

        engine = CondorcetVoting()
        with patch("CondorcetVoting.random.random", return_value=0.2):
            with patch.object(engine, "_rankedPairsWinner", wraps=engine._rankedPairsWinner) as ranked_pairs_spy:
                winners = engine.recurseCalculate(position)

        self.assertEqual(len(winners), 1)
        self.assertTrue(ranked_pairs_spy.called)


if __name__ == "__main__":
    unittest.main()

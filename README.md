# **Ranked-Choice Election Scripts**

This workspace now contains a modular election toolkit that can process ranked ballot data from a Microsoft Forms CSV using either Instant Runoff Voting (IRV) or a sequential Condorcet method.

## How to use it

* Create a Microsoft Form with ranking questions and export the results as a CSV.
* Install Python if you have not already done so.
* Run the main entrypoint:
  * python Election.py
* Follow the prompts to enter the CSV path, the positions and winner counts, and whether to use IRV or Condorcet.

## Files

* Election.py: CLI entrypoint and CSV/position setup logic.
* Position.py: ballot and candidate data for a single office.
* Candidate.py: storage for candidate-specific vote totals and tie-breaker values.
* InstantRunoffVoting.py: IRV election engine.
* CondorcetVoting.py: Condorcet election engine.
* tests/test_election.py: regression tests for the new voting engines.

## Election theory

IRV is a transferable-vote system that eliminates the weakest candidate until a winner remains. Condorcet compares candidates head-to-head and elects a candidate who beats every other candidate in pairwise majority contests when one exists.


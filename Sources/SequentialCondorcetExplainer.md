# Sequential Condorcet Method

## Definitions
- **Condorcet winner**: candidate who defeats every other candidate in pairwise majority comparisons.
- **Sequential Condorcet**: multi‑winner extension where winners are chosen one at a time using Condorcet comparisons, then removed from the candidate set.

## Inputs
- **Ballots**: list of voter rankings (ordered lists of candidates).
- **Seats**: integer number of winners to select.

## Algorithm
1. Initialize:
   - candidates = set of all candidates
   - winners = empty list
2. Repeat until winners.size == seats:
   a. Build pairwise preference matrix:
      - For each candidate X, Y in candidates:
        - count voters preferring X over Y
   b. Find Condorcet winner:
      - candidate who beats all others in pairwise matrix
   c. If Condorcet winner exists:
      - add to winners
      - remove from candidates
   d. If no Condorcet winner (cycle):
      - apply tie‑breaking rule (e.g., Minimax, Ranked Pairs, Schulze, random)
      - add chosen candidate to winners
      - remove from candidates
3. Return winners.

## Pseudocode

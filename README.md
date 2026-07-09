# Ranked-Choice Election Calculator

This repository helps you calculate election winners from a Microsoft Forms CSV file.

It supports two methods:

* IRV (Instant Runoff Voting)
* Condorcet (sequential Condorcet with ranked-pairs fallback)

You do not need to understand the code to use it.

## What You Need

Before you run the script, make sure you have:

* Python installed on your computer.
* A Microsoft Forms results file exported as `.csv`.
* This project folder downloaded

## Quick Start

1. Open a Terminal window.
2. Run:

   ```bash
   python Election.py
   ```

3. Answer the prompts shown in the terminal.

## What the Program Will Ask

### 1) CSV file path

Enter the full path to your election CSV file.

Example:

```text
C:\Users\YourName\Desktop\election_results.csv
```

### 2) Positions and number of winners

Enter positions in this format:

```text
PositionName,NumberOfWinners;PositionName,NumberOfWinners;
```

Example:

```text
Co-President,2;Treasurer,1;Secretary,1;Public Relations,1;
```

### 3) Voting method

* Enter `I` for IRV
* Enter `C` for Condorcet

### 4) Multi-position winner conflicts (only if needed)

If one candidate wins multiple positions, the script will ask which position they should keep.
It then recalculates the other position without that candidate.

## Output You Will Get

The script prints each position and its final winner(s).

Example:

```text
The winner(s) of Treasurer is/are: Charan Polisetty
```

## Choosing a Method

### IRV

Uses elimination rounds based on first-choice votes.

### Condorcet

Compares candidates head-to-head and prefers candidates who perform best in pairwise matchups.

### **Which one to use**

If you are unsure of which one to use, default to Condorcet. It is typically regarded as the best method for electing the socially optimal winner.

[here is a great article on why](https://effectivegov.uchicago.edu/primers/condorcet-voting) *(basically, it is kind of hard to complain about the winner of an election when they have beat every other candidate in a 1v1 matchup)*

The only reasons for using IRV over Condorcet are if you want to avoid the potential ambiguity of a Condorcet cycle (although the script handles those for you) or if you don't want to have to explain Condorcet to your constituents because you/they are more familiar with IRV. Or maybe you just don't want to use an election method named after an 18th century French dude.

## Common Input Mistakes

* Wrong CSV path: make sure the file exists and ends in `.csv`.
* Wrong position format: include commas and semicolons exactly.
* Position name mismatch: names should match CSV column headers.

## Project Files

* `Election.py`: main script you run
* `InstantRunoffVoting.py`: IRV logic
* `CondorcetVoting.py`: Condorcet logic
* `Position.py`, `Candidate.py`: election data models
* `tests/test_election.py`: automated tests

## Notes

* Blank ranking entries are ignored.
* Rankings in each CSV cell should be separated by semicolons.
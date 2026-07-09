from __future__ import annotations

import csv
from typing import List

from Candidate import Candidate
from Position import Position
from InstantRunoffVoting import InstantRunoffVoting
from CondorcetVoting import CondorcetVoting
from VotingHelpers import flexibleContains, simplifyString


def flexibleContains(contain1: str, contain2: str) -> bool:
    """Check whether one string contains another, ignoring case and whitespace."""
    if not isinstance(contain1, str) or not isinstance(contain2, str):
        return False

    short_contain = contain2 if len(contain1) > len(contain2) else contain1
    long_contain = contain1 if len(contain1) > len(contain2) else contain2
    return bool(
        short_contain.strip()
        and long_contain.strip()
        and simplifyString(short_contain) in simplifyString(long_contain)
    )


def simplifyString(value: str) -> str:
    """Normalize a string for comparison."""
    return str(value).strip().lower()


def getAndCheckStringInput(valid_inputs: List[str]) -> str:
    """Prompt the user until a valid answer is provided."""
    response = input().strip()
    for valid_input in valid_inputs:
        if flexibleContains(response, valid_input):
            return response
    print("Invalid input. Please try again.")
    return getAndCheckStringInput(valid_inputs)


def intro() -> None:
    """Print the introductory instructions for the election runner."""
    print("This is the rank-order election script.")
    print("It can process ranked ballot data from a CSV file using either IRV or Condorcet logic.")
    print()


def getCSV() -> List[List[str]]:
    """Ask the user for the election CSV and return its rows."""
    print("Input the address of the CSV file with the election data. Do not include any extra text.")
    path = getAndCheckStringInput([".csv"])
    try:
        with open(path, "r", newline="", encoding="utf-8-sig") as handle:
            return list(csv.reader(handle))
    except (FileNotFoundError, OSError):
        print("File not found. Please try again.")
        return getCSV()


def getPositions() -> List[Position]:
    """Ask the user for the positions and how many winners each can have."""
    print("Enter the positions in the format positionName,numberOfWinners;positionName,numberOfWinners;.")
    raw_input = getAndCheckStringInput([",", ";"])
    positions: List[Position] = []

    for item in raw_input.split(";"):
        if not item:
            continue
        name, winner_count = item.split(",")
        positions.append(Position(name.strip(), int(winner_count.strip()), []))

    return positions


def getVotingMethod() -> str:
    """Ask whether the user wants IRV or Condorcet."""
    print("Choose a voting method: enter 'I' for IRV or 'C' for Condorcet.")
    return getAndCheckStringInput(["I", "C"]).upper()


def setUpForVoting(csv_data: List[List[str]], positions: List[Position]) -> None:
    """Populate each position with the ranking data from the CSV file."""
    if not csv_data:
        raise ValueError("The CSV file is empty.")

    header = csv_data[0]
    ballots = csv_data[1:]
    for position in positions:
        position.indexInCSV = -1
        for index, column_name in enumerate(header):
            if simplifyString(column_name) == simplifyString(position.name):
                position.indexInCSV = index
                break

        if position.indexInCSV < 0:
            raise ValueError(f"Could not find a CSV column for {position.name}.")

        position.votes = []
        for ballot in ballots:
            if position.indexInCSV >= len(ballot):
                ranking = []
            else:
                ranking = [entry.strip() for entry in str(ballot[position.indexInCSV]).split(";") if entry.strip()]
            position.votes.append(ranking)

        position.originalVotes = [list(vote) for vote in position.votes]
        position.findCandidates()
        position.calculateBorda()
        position.calculateFirstVotes()


def main() -> None:
    """Run the end-to-end election workflow from the command line."""
    intro()
    csv_data = getCSV()
    positions = getPositions()
    setUpForVoting(csv_data, positions)

    method = getVotingMethod()
    if method == "I":
        engine = InstantRunoffVoting(positions)
    else:
        engine = CondorcetVoting(positions)

    engine.run(positions)

    for position in positions:
        winner_names = ", ".join(candidate.name for candidate in position.winners)
        print(f"The winner(s) of {position.name} is/are: {winner_names}")


if __name__ == "__main__":
    main()

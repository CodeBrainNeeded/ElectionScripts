# Planning for Election Script:



##### User Experience:

1. explaining the purpose of the script and what data the user needs in order to use it
2. receive a message asking them what the address of the CSV file with their election data is; respond with the file's address
3. ask what positions are being run for and how many winners are possible for each position; responds with which positions there are and how many winners each can have (similar to how it was done in the example file)
4. asking them whether they want to use IRV or Condorcet; respond with an "I" or a "C"
5. ask which of the positions a candidate who has won multiple positions wants to win, and which one they want recalculated without them; respond with the position's name (should only be asked if and when there is a candidate who has won multiple positions, and should be repeated until there are no candidates who are winning multiple positions)
6. list each of the positions and their winner(s)



Key: *message sent by script; how the user responds to the script if at all (specific details that need to be adhered to, if any)*

use the *OriginalScript.py* file for reference

have fail-safes for input that does not meet the input criteria, similar to the fail-safes implemented in the reference file



##### File Organization (all are Python files):

* Election: static file (don't really even need a class) that interacts with the user through input() and print()
* Position: a file containing a single class (called "Position) that represents a position that candidates are running for
* Candidate: a file containing a single class (called "Candidate") that represents a person running for a position
* InstantRunoffVoting: a file containing a single class (called "IRV") which functions as an Instant Runoff election calculator for several positions
* CondorcetVoting: a file containing a single class (called "Condorcet") which functions as a Condorcet election calculator for several positions



##### System Design:

The classes may or may not need to have the following functionality / methods / instance variables depending on how the system is designed (also use the *OriginalScript.py* file for reference).



###### Election.py:

**Functionality:**

* is run by the user
* interacts with the user as outlined in the *User Experience* section, or has its objects interact with the user
* processes the election data and stores it as a 2D list
* uses the election data to make a list of Positions
* creates and uses InstantRunoffVoting and/or CondorcetVoting objects

**Methods:**

* flexibleContains: same as in reference document
* simplifyString: same as in reference document
* getAndCheckStringInput: same as in reference document
* intro: similar to in reference document
* getCSV: similar to in reference document
* getPositions: similar to in reference document
* askWhichPosition: asks which Position a Candidate wants to win and which one should be reevaluated (it will be called if a Candidate has won multiple Positions)

**Instance Variables:** none, its a "static" class (although it will need objects that it feeds into methods, etc.)



###### Position.py:

**Functionality:**

* represents a position that people are running for
* has all the votes for the position (each vote is a ranking of the Candidates running for the Position from highest to lowest preference)
* contains all the Candidates for the position

**Methods:**

* \_\_init\_\_: initializes a Position object

  * takes in a 2D list of votes, and saving them to the *votes* instance variable
  * initializes all other instance variables and sets them to 0/""/False values.
  * runs findCandidates
  * runs calculateBorda
  * runs calculateFirstVotes
* findCandidates:  uses the *votes* list to sift through the first relevant ranking vote it to find and save the Candidates that are running for the Position
* \_\_str\_\_: similar to reference
* \_\_repr\_\_: similar to reference
* calculateBorda: uses the votes data and Candidates to find the Borda count for each Candidate and save it to the respective Candidate's instance variable
* calculateFirstVotes: uses the votes data and the Candidates to find the number of first-choice votes each Candidate received and save it to the respective Candidate's instance variable
* copyAndRemoveCandidate: takes in a Candidate as a parameter; makes a deep copy of the object that the object that the method is being called with, removes the Candidate's name from the voting data and also removes it from the *candidates* array; assigns the new object's winners to the "self" object's winners so that changing one changes the other; returns the aforementioned copied object

**Instance Variables:**

* name (str): the name of the position
* numPossibleWinners (int): the number of people who can be winners of the position
* votes (list\[list\[str]]): the votes that people have entered for who should win the position
* candidates (list\[Candidate]): all the Candidates running for the Position
* winners (List\[Candidate]): the Candidates who have won the Position



###### Candidate.py:

**Functionality:**

* represents a person running for a position
* contains data pertaining to the person

**Methods:**

* \_\_eq\_\_: returns flexibleContains(self, other)
* \_\_str\_\_:
* \_\_repr\_\_:
* \_\_init\_\_: takes in a name(str) and saves it to the respective instance variable; sets other instance variables to zero

**Instance Variables:**

* name (str): the name of the Candidate
* borda (int): the Borda count of the Candidate
* currentVotes (int): the number of votes the Candidate received (this is updated each calculation cycle for IRV)
* firstVotes (int): the number of 1st place votes the Candidate received



###### InstantRunoffVoting:

**Functionality:**

* calculate results for a list of Positions using Instant Runoff Voting (IRV) logic
* work with the user through print() and input() to resolve any conflicts, such as if the same candidate wins multiple positions
* assigns winners to the *positions*

**Methods:**

* run: calls recurseCalculate for each Position in *positions*, then calls checkForMultiple with the list of Positions as the parameter
* recurseCalculate: 

  * takes a Position as a parameter
  * if the length of *winners* is greater than or equal to *numPossibleWinners*, returns the Position's *winners***;** else ->
  * finds out how many 1-st choice votes each Candidate for the Position has using the *votes* list
  * finds which Candidate has the least votes; if there is a tie, use their *borda*, then their *firstVotes*, and finally random chance as tiebreakers
  * use copyAndRemoveCandidate to make a copy of the Position, remove the Candidate with the least votes, and make the copy's *winners* point to the same place in memory as the original's *winners*
* call recurseCalculate with the copy as the parameter
* checkForMultiple:

  * takes in a list of Positions as a parameter
  * checks if multiple Positions have the same winner; if not, return
  * prompt the user to choose which one the winner wants to win and which one should be recalculated; use Election.getAndCheckStringInput to check for valid input, and process it to determine which one the winner wants to win and which one they don't
  * for the position that the winner does not want to win, use copyAndRemoveCandidate to make a new Position object that removes the candidate from the running, run calculateBorda and calculateFirstVotes on the new object; and call recurseCalculate with the copy
  * call checkForMultiple again with the list of Positions

**Instance Variables:**

* *positions* (list\[Position]): contains all the positions that need to be evaluated



###### CondorcetVoting:

**Functionality:**

* calculate results for a list of Positions using Sequential Condorcet with Ranked Pairs (aka Tideman) logic
* the user experience should be the same as with InstantRunoffVoting and they should be able to be used as interchangeably as possible in code (with the minimum of change in the experience of doing external method calls, etc.)

**Methods:** whatever is necessary to meet the functionality criteria

**Instance Variables:** whatever is necessary to meet the functionality criteria



##### Other Key Details:

* Use the *OriginalScript.py* file as a reference as much as possible (because we know it works as an Instant Runoff Voting calculator).
* Write informative but concise Docstrings for all methods and instance variables
* Use camelCase for variable and method names and PascalCase for class names
* Use type hints for variables and objects whenever possible
* Use *CondorcetMethodWikipedia.txt*, *InstantRunoffVotingWikipedia.txt*, and *SequentialCondorcetExplainer.md* as references for designing the voting systems


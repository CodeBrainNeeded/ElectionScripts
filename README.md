# **Instant-Runoff Voting**

This script was created with the intent of simplifying the conduction of a Instant-Runoff election through a platform like Microsoft Forms.



**Here's how to use it:**

* Make a Microsoft Form for your election with "Ranking" questions and collect response, export the results as an Excel File. Then, convert or "Save As" the file as a CSV.
* Install Python if you haven't already. The steps to do so are here: https://www.python.org/downloads/
* Download the script
* Run the python file: open Command Line and type in "python" followed by a space and then the address of the script file

  * for example: "python C:\\Users\\CodeBrainNeeded\\Desktop\\RankChoiceVoting.py"
* Follow the instructions and answer the prompts as given by the script



You can trust that the script is not malware because I don't know enough about malware to explain to you why the script is not malware. You can also just read the code. There is no method in it called "hijackDevice()".



**Election Theory:**

The script uses an Instant Runoff Voting (IRV) system, which is unquestionably fairer than the "first-past-the-post" system that most organizations and governments use in the USA (many other countries use IRV). IRV is theoretically not as fair as the Condorcet method (this is a great article on why: https://effectivegov.uchicago.edu/primers/condorcet-voting), but the shortcomings of IRV compared to Condorcet usually only arise in elections that are highly partisan/polarized and/or involve a very small number of competitive candidates, so IRV is generally sufficient for elections in non-governmental organizations.


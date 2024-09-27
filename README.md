# Assignment # 1 : Game playing agent for Power Connect-4

**Name:** Muhammad Amir Hamza

**Roll #** 261210478 

**course:** ECSE-526 Artificial Intelligence

## Description
The objective of this assignment was to develop and evaluate the performance of a game-playing agent for the Power Connect-4 game. The instructor provided an initial heuristic function, which we used to assess the performance of both the Minimax and Minimax with $\alpha\beta$-pruning agents. In the second part of the assignment, we were tasked with creating our own heuristic function and analyzing its overall performance, as well as comparing it against the initial heuristic.

## File Description
- **GameBoard.py**: This class simulates the game environment for Power Connect-4. Key functions include:

    - Checking all possible valid moves.
    - Detecting terminal conditions (win, loss, or draw).
    - Calculating the overall game score.
    - Performing actions (e.g., placing a piece) on the game board.
    - Printing the game grid in a readable format for easy understanding.

- **agent_advance_moveordering.py**: In this file, we developed an advanced version of the agent using a modified heuristic function. The agent employs Minimax with $\alpha\beta$ pruning and move ordering to reduce the agent's reaction time. Additionally, the `test_play()` function simulates gameplay between the agent and a random opponent, which can be adjusted to allow for human interaction.

- **agent_initial_moveordering.py**: This is similar to `agent_advance_moveordering.py` but uses the initial heuristic function.

- **ConnectServer.py**: This contains a class to communicate with the server. 

- **agent_black.py & agent_white.py:** These files were executed concurrently on the TRLinux machines using the `ConnectServer.py` file for communication with the server, to play a match with eachother. The same files were used for in-class tournament. 

- **log_black_agent.txt & log_white_agent.txt**: These are the log file of match between agent using advance heuristic function (agent white) and agent using initial heuristic function (agent black).

- **Aux, test and result generator.zip:** This contains all the auxillary files for results generations, data storing and testing. 

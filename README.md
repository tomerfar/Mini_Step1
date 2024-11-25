Tomer Faran - 2085852650
Koral Shilon - 318762051

# backgammon
Python modules to play backgammon (human or computer)

## System Requirements

- Python 3 (you may need to change the commands below to `python3 ...` if that is how you run python 3 on your machine)

## How to run the game

* **Human vs Computer**: run `python single_player.py`, then choose the computer strategy to play against
* **Human vs Human**: run `python two_player.py`
<<<<<<< HEAD
* **Computer vs Computer**: run `python main.py` The two 'players' can have different strategies.
* **tournament**: run `python tournament.py`
=======
* **tournament**: run `python tournament.py`

>>>>>>> 1ca8bb65156c1c374ebbbaf5301539e02f4fa15c
This runs many games with a different 'player' starting each time and returns the probability of the strategies being equally good.

Backgammon Game Platform
Overview
This project is a Python-based platform for simulating and playing Backgammon games. It supports human vs. AI and AI vs. AI matches, as well as tournaments. Players can choose from various AI strategies or participate manually. The platform is designed for flexibility, allowing users to add new strategies or customize game rules.

Classes and Key Components
1. Game
Manages the flow of a single Backgammon game.
Features:
Tracks board state, dice rolls, and player turns.
Supports timed turns for players.
Validates moves and enforces game rules.
Determines game winners.
Core Method:
run_game(verbose=True): Starts the game loop, allowing players to make moves.
2. ReadOnlyBoard
Provides a read-only interface to the Board class for strategies.
Ensures that strategies cannot alter the board state directly.
3. Strategies
Purpose: Defines the logic for player decision-making.
Includes:
HumanStrategy: Interactive gameplay for human players.
MoveRandomPiece: AI that moves pieces randomly (Easy).
MoveFurthestBackStrategy: AI that prioritizes moving pieces furthest from their home (Medium).
Strategy Interface:
move(board, colour, dice_roll, make_move, opponents_activity): Executes moves during a player's turn.
4. Tournament
Manages multi-round tournaments between players.
Features:
Randomized matchups with support for "bye" rounds.
Configurable "best of" series for matches.
Automatically tracks winners and progress through the tournament tree.
5. Single Player Mode
Allows one human player to compete against an AI.
Features:
Interactive prompts for piece selection and moves.
Configurable time limits and AI difficulty.
Interface Functions
Game Setup and Play
run_game(verbose=True): Starts a single game between two players.
get_rolls_to_move(location, requested_move, available_rolls): Determines valid dice rolls to achieve a requested move.
Tournament Setup
run_tournament(player_names, player_strategies): Initiates a multi-round tournament with the given players and strategies.
Board Interaction
print_board(): Displays the current state of the board.
to_json(): Exports the board state for analysis or debugging.
How to Play
Single Player Mode
Run the single-player script.
Enter your name and choose an AI strategy.
Specify a time limit for turns.
Play interactively by choosing pieces to move based on dice rolls.
The game ends when one player wins.
Tournament Mode
Run the tournament script.
Enter the number of players and assign strategies.
Configure the "best of" series and time limits.
Watch the tournament progress as players compete.
Features and Customization
Flexible Strategies: Add new AI strategies by subclassing Strategy and implementing the move method.
Real-Time Interaction: Supports human input and timed turns.
Tournament Automation: Simulates tournaments with automatic progression.

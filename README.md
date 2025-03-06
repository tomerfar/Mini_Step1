# backgammon

Python modules to play backgammon (human or computer)

## System Requirements

- Python 3 (you may need to change the commands below to `python3 ...` if that is how you run python 3 on your machine)

## How to run the game

- **Human vs Computer**: run `python single_player.py`, then choose the computer strategy to play against
- **Human vs Human**: run `python two_player.py`

Report: Reinforcement Learning in AI Player
This report describes the main classes and methods involved in creating a reinforcement learning-based AI player. It explains how the neural network is built, how it is trained, and how the AI player uses the trained network to make informed game decisions.

Brain Class and Neural Network
Overview
The Brain class manages a neural network that evaluates board states. It includes functions for saving/loading the model, training, and evaluating game states. The neural network is a feedforward model that predicts heuristic values for given board configurations.
Neural Network Structure
The neural network is a simple, fully connected model with the following structure:
• Input Layer: 28 neurons (Board representation as a vector).
• Hidden Layers:
o 128 neurons, ReLU activation
o 64 neurons, ReLU activation
• Output Layer: 1 neuron (single-value prediction)
Key Functions
• save_brain: Saves the trained model.
• load_saved_brain: Loads a saved model.
• pre_train_brain: Collects initial heuristic values by observing a player’s moves.
• train_brain: Trains the network based on game outcomes.
• generate_to_fit_vector: Computes target values for training based on the winner.

Training Class
Overview
The Training class serves as the engine for training the neural network. It runs multiple simulated games, collects board states, and sends the gathered data to the Brain class for learning.
Key Responsibilities
• Running Games: Simulates matches between two players.
• Collecting Data: Extracts board states and game results.
• Training the Neural Network: Feeds the collected data to the Brain for updating the model.
• Saving Progress: Periodically saves the trained model.
Training Process

1. Initial Training (Pre-training Stage)
   o Collects board states and heuristic evaluations.
   o Sends this data to the Brain for initial learning.

2. Main Training (Learning from Wins & Losses)
   o Runs a series of games and records each move.
   o After each game, the winner is determined.
   o The Brain is updated with the new data after each game.
   o The trained model is saved at predefined checkpoints.
   This class ensures that the neural network continuously improves by learning from gameplay outcomes.

MLPlayer Class
Overview
The MLPlayer class represents the AI player that makes decisions based on the trained neural network. During its turn, the AI evaluates possible moves and selects the best one using the neural network's predictions. It integrates with the game by generating potential board states and evaluating them using the model to make the most informed move possible.
Key Responsibilities
• Evaluating Moves: The AI generates possible future board states based on available dice rolls and evaluates each using the neural network.
• Selecting the Best Move: Based on the evaluations, the AI selects the most optimal move for the current board state.
• Learning from Games: The AI uses the train method to improve the model based on past game data.
• Saving and Loading Models: The model can be saved after training and loaded for future use.
The MLPlayer class acts as the brain for the AI player, making real-time decisions based on neural network evaluations and past game history.

Not Relevant to the project from down here.
<<<<<<< HEAD

- **Computer vs Computer**: run `python main.py` The two 'players' can have different strategies.
- # **tournament**: run `python tournament.py`
- **tournament**: run `python tournament.py`

> > > > > > > 1ca8bb65156c1c374ebbbaf5301539e02f4fa15c
> > > > > > > This runs many games with a different 'player' starting each time and returns the probability of the strategies being equally good.

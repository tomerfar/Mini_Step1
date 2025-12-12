# Python-Backgammon

A small Python project containing modules to play Backgammon (human vs. human, human vs. computer, or computer vs. computer). It includes an AI player based on a feedforward neural network and training utilities to improve its heuristic over time with reinforcement learning.

## Table of contents
- About
- Key features
- System requirements
- Installation
- Running the game
  - Human vs Computer
  - Human vs Human
  - Computer vs Computer
  - Tournament mode
- AI architecture & training
  - Brain (neural network)
  - Training engine
  - MLPlayer (AI player)
- Project layout
- How to train a new model
- Saving & loading models
- Contributing
- License
- Contact

## About
This repository provides an extendable Backgammon implementation and an AI that learns to play via reinforcement learning. The AI uses a small feedforward neural network to estimate board-state heuristics and chooses moves by evaluating possible next states.

## Key features
- Play locally: human vs human, human vs computer, or computer vs computer.
- Reinforcement-learning pipeline to train an evaluation network from self-play.
- Simple, modular codebase for experimenting with different network architectures and training regimes.

## System requirements
- Python 3.8+ (If your system uses `python3` for Python 3, use that command.)
- Typical ML dependencies (if you use the included Brain implementation):
  - numpy
  - tensorflow or pytorch (depending on the Brain implementation in this repo)
  - (Optional) tqdm for progress bars

Install the Python dependencies using pip (adjust package names to match the repo's implementation):
pip install -r requirements.txt

## Installation
1. Clone the repository:
   git clone https://github.com/tomerfar/Python-Backgammon.git
2. Change into the project directory:
   cd Python-Backgammon
3. Install dependencies (recommended inside a virtual environment).

## Running the game
All commands assume you are in the project root. Replace `python` with `python3` if needed.

- Human vs Computer
  - Run:
    python single_player.py
  - Follow the prompts to select which computer strategy to play against (random, heuristic, ML player, etc).

- Human vs Human
  - Run:
    python two_player.py

- Computer vs Computer
  - Run:
    python main.py
  - Use this mode to run two AIs against each other for evaluation.

- Tournament
  - Run:
    python tournament.py
  - Runs a tournament of multiple games between configured strategies and reports results.

## AI architecture & training

### Brain (neural network)
The Brain class manages a feedforward neural network used to evaluate board states. Key points:
- Typical architecture used in this project:
  - Input: 28 neurons (board representation vector)
  - Hidden layers: 128 (ReLU) -> 64 (ReLU)
  - Output: 1 neuron (scalar heuristic)
- Primary methods:
  - save_brain: save model weights/checkpoints to disk
  - load_saved_brain: restore model from disk
  - pre_train_brain: collect initial heuristic labels from an existing heuristic or playstyle
  - train_brain: fit the network using collected training data
  - generate_to_fit_vector: generate target values after a game finishes (propagate winner signal)

Note: The concrete Brain backend may use TensorFlow or PyTorch depending on implementation; check the module for exact imports and file formats (.h5, .pt, etc).

### Training class
The Training class automates self-play to produce training examples and train the Brain:
- Runs simulated matches between two players (configurable strategies).
- Records board states and actions during games.
- After each game, computes target values (winner signals) and updates the Brain.
- Periodically saves model checkpoints.

Training flow:
1. (Optional) Pre-training: gather labeled heuristic values from a baseline heuristic or expert player.
2. Main training: perform many self-play games, update network after games, and save progress.

### MLPlayer
MLPlayer uses the trained Brain to make decisions:
- On a turn, generates legal moves and resulting board states.
- Uses the Brain to evaluate each candidate board state and selects the move with the highest heuristic.
- Can save its model after training and load an existing model for gameplay.

## Project layout (high level)
- single_player.py      — CLI for human vs computer
- two_player.py         — CLI for human vs human
- main.py               — Example computer vs computer runner
- tournament.py         — Tournament orchestrator
- brain.py              — Neural network wrapper (save/load/train/evaluate)
- training.py           — Training loop and self-play orchestration
- mlplayer.py           — AI player interface using Brain
- board.py / game.py    — Game state, rules, legal moves
- players/              — Other player implementations / heuristics

(Open the repository files to confirm exact filenames and adjust commands as needed.)

## How to train a new model
1. Ensure your Brain config points to a writable models directory.
2. (Optional) Run pre-training to bootstrap the network:
   - Use pre_train_brain to collect initial heuristics and produce a starting model.
3. Run the Training script to perform self-play:
   python -m training
   - The Training class will run a number of games, update the Brain, and save checkpoints.
4. Monitor progress by running evaluation matches (computer vs computer) against a baseline strategy.

Tip: Start with a limited number of games to ensure everything runs correctly, then scale up.

## Saving & loading models
- Models are saved via Brain.save_brain(). File format depends on the ML backend (e.g., TensorFlow .h5 or PyTorch .pt).
- Load models with Brain.load_saved_brain() to resume training or run inference during play.

## Contributing
Contributions are welcome. Suggested improvements:
- Add unit tests for rule enforcement and move generation.
- Add command-line flags to tune training parameters (learning rate, batch size, save frequency).
- Experiment with deeper networks, alternative board encodings, or reinforcement learning algorithms (policy/value networks, MCTS).

If you plan to submit changes:
1. Fork the repository.
2. Create a feature branch.
3. Open a PR with a description of your changes.

## License
Include license information here (e.g., MIT). If none exists, add one or clarify intended licensing.

## Contact
For questions or help, open an issue on the repository or contact the maintainer: tomerfar

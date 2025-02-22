import torch
from src.game import Game
from src.Brain import Brain
from src.strategies import MoveRandomTraining, TrainingPhase2
from src.MLplayer import MLPlayer
from src.colour import Colour
from random import randint

class Training:
    def __init__(self, brain=None):
        self.brain = Brain()
        self.game_turns = []
        self.start_board_estimation = []
        self.white_20_estimation = []
        self.black_100_estimation = []

        if brain is None:
            self.initialize_neural_network()
        else:
            self.brain = self.brain.load_saved_brain(brain)

    def initialize_neural_network(self):
        for i in range(5):  # Run 5 iterations
            game = Game(
                white_strategy=MoveRandomTraining(),
                black_strategy=MoveRandomTraining(),
                first_player=Colour(randint(0, 1)),
                time_limit=-1
            )
            print(f"Running pre-train iteration {i+1}")
            game.run_game(verbose=False)

            # Train the neural network initially on the starting board
            self.brain.pre_train_brain(game.strategies[Colour.WHITE].game_data)
            self.brain.save_brain(self.brain.name) # Overrides current save, changing Neural Network
        

    def train(self, iterations, names):
        name_index = 0

        for i in range(iterations[-1]):
            # Create a new game instance for each training iteration
            game = Game(
            white_strategy=TrainingPhase2(),
            black_strategy=TrainingPhase2(),
            first_player=Colour(randint(0, 1)),
            time_limit=-1
            )
            game.run_game(verbose=False)

            # Train the brain with the game boards and winner's color
            self.brain.train_brain(game.strategies[Colour.WHITE].game_data, game.who_won())
            self.brain.games_played += 1

            if i >= iterations[name_index] - 1:
                self.brain.save_brain(names[name_index])  # Save brain after a specified number of iterations
                name_index += 1

            # Estimation for the starting board and black/white scoring
            # start_board_estimation = self.brain.neural_network(torch.tensor([game.game_boards[0]], dtype=torch.float32)).item()
            # black, white = self.brain.black_white_scoring()
            # self.start_board_estimation.append(start_board_estimation)
            # self.white_20_estimation.append(white)
            # self.black_100_estimation.append(black)
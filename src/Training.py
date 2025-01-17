import torch
from game import Game
from Brain import Brain

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
        init_game = Game('COMPUTER', 'COMPUTER') # Need to change to other players
        init_game.run_game()
        # Train the neural network initially on the starting board
        self.brain.train_brain(init_game.game_boards, init_game.who_won_the_game().colour)

    def train(self, iterations, names):
        name_index = 0

        for i in range(iterations[-1]):
            # Create a new game instance for each training iteration
            game = Game('ML', 'ML') # 
            game.player1.brain = self.brain
            game.player2.brain = self.brain
            game.run_game()

            # Train the brain with the game boards and winner's color
            self.brain.train_brain(game.game_boards, game.who_won_the_game().colour)
            self.brain.games_played += 1

            if i >= iterations[name_index] - 1:
                self.brain.save_brain(names[name_index])  # Save brain after a specified number of iterations
                name_index += 1

            # Estimation for the starting board and black/white scoring
            start_board_estimation = self.brain.neural_network(torch.tensor([game.game_boards[0]], dtype=torch.float32)).item()
            black, white = self.brain.black_white_scoring()
            self.start_board_estimation.append(start_board_estimation)
            self.white_20_estimation.append(white)
            self.black_100_estimation.append(black)
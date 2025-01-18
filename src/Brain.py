import os
import pickle
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from board import Board

class NeuralNetwork(nn.Module):
    def __init__(self, input_size):
        super(NeuralNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)  # Output a single value
        )


    def forward(self, x):
        return self.network(x)
    

class Brain:
    def __init__(self):
        self.neural_network = NeuralNetwork(input_size=28)
        self.optimizer = optim.Adam(self.neural_network.parameters(), lr=1) # lr might be changed
        self.criterion = nn.MSELoss()
        self.games_played = 0
        self.name = None
        self.lambda_value = 0.7


    def save_brain(self, file_name=None):
        if file_name is None:
            file_name = input("Please give a name to the brain: ")
        self.name = file_name
        full_file_name = os.getcwd() + "\\" + file_name + ".pt"
        torch.save(self.neural_network.state_dict(), full_file_name)


    @staticmethod
    def load_saved_brain(file_name):
        path = os.getcwd() + "\\" + file_name + ".pt"
        neural_network = NeuralNetwork()
        neural_network.load_state_dict(torch.load(path))
        return neural_network
    

    def train_brain(self, game_boards, game_winner_colour):
        to_fit = self.generate_to_fit_vector(game_boards, game_winner_colour).ravel()
        game_boards_tensor = torch.tensor(game_boards, dtype=torch.float32)
        to_fit_tensor = torch.tensor(to_fit, dtype=torch.float32)

        self.optimizer.zero_grad()
        outputs = self.neural_network(game_boards_tensor)
        loss = self.criterion(outputs, to_fit_tensor)
        loss.backward()
        self.optimizer.step()


    def generate_to_fit_vector(self, game_boards, game_winner_colour):
        game_boards_tensor = torch.tensor(game_boards, dtype=torch.float32)
        with torch.no_grad():
            initial_probability_array = self.neural_network(game_boards_tensor).numpy()

        computed_probability_array = [0] * len(initial_probability_array)
        sum_distance = 0
        next_value = game_winner_colour

        for i in range(len(initial_probability_array)-1, -1, -1):
            current_value = initial_probability_array[i]
            sum_distance += (next_value - current_value)
            computed_probability_array[i] = current_value + 0.05 * sum_distance
            sum_distance *= self.lambda_value
            next_value = initial_probability_array[i]

        return np.array(computed_probability_array)

    def black_white_scoring(self):
        test_board = Board()
        test_board.board = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 0]]
        with torch.no_grad():
            return self.neural_network(torch.tensor([test_board.board_to_vector(0)], dtype=torch.float32)).numpy(), \
                   self.neural_network(torch.tensor([test_board.board_to_vector(1)], dtype=torch.float32)).numpy()
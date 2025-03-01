import os
import pickle
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from src.board import Board

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
        self.optimizer = optim.Adam(self.neural_network.parameters(), lr=0.001) # lr might be changed
        self.criterion = nn.MSELoss()
        self.games_played = 0 # need to increment it whenever we finish a game
        self.name = None
        self.lambda_value = 0.7


    def save_brain(self, file_name=None):
        if file_name is None:
            file_name = input("Please give a name to the brain: ")
        self.name = file_name
        full_file_name = os.getcwd() + "\\" + file_name + ".pt"
        torch.save(self.neural_network.state_dict(), full_file_name)


    # @staticmethod
    # def load_saved_brain(file_name):
    #     path = os.getcwd() + "\\" + file_name + ".pt"
    #     neural_network = NeuralNetwork(input_size=28)
    #     neural_network.load_state_dict(torch.load(path, weights_only=True))
    #     return neural_network
    
    @staticmethod
    def load_saved_brain(file_name):
        path = os.path.join(os.getcwd(), f"{file_name}.pt")
        brain_instance = Brain()  # Initialize an empty Brain instance
        brain_instance.neural_network.load_state_dict(torch.load(path, weights_only=True))
        return brain_instance  # Return the fully constructed Brain object
    
    def pre_train_brain(self, game_data):
        # Extract board states and heuristic values from game_data
        board_states = [data['board'] for data in game_data]
        heuristic_values = [data['heuristic'] for data in game_data]
        # print(f"boards:{board_states}")
        # print(f"values:{heuristic_values}")

        # Convert board states and heuristic values to tensors
        board_states_tensor = torch.tensor(board_states, dtype=torch.float32)
        heuristic_values_tensor = torch.tensor(heuristic_values, dtype=torch.float32).view(-1, 1)

        # Zero the gradients
        self.optimizer.zero_grad()

        # Forward pass: compute predicted outputs by passing inputs to the model
        outputs = self.neural_network(board_states_tensor)

        # Compute the loss
        loss = self.criterion(outputs, heuristic_values_tensor)

         # Compute differences
        differences = heuristic_values_tensor - outputs
        expected_value = differences.mean().item()
        variance = differences.var().item()

        # Prepare DataFrame
        df = pd.DataFrame({
            'Heuristic Value': heuristic_values,
            'NN Output': outputs.detach().numpy().flatten(),
            'Difference': differences.detach().numpy().flatten()
        })

         # Add statistics
        df['Mean'] = [expected_value] * len(df)
        df['Variance'] = [variance] * len(df)

        # Save to Excel
        df.to_excel("heuristic_network_dif.xlsx", index=False)

            # Backward pass: compute gradient of the loss with respect to model parameters
        loss.backward()

        # Perform a single optimization step (parameter update)
        print("Before update:", self.neural_network.network[0].weight.data[0][:5])  
        self.optimizer.step()  
        print("After update:", self.neural_network.network[0].weight.data[0][:5])

        print(f"Pre-train Loss: {loss.item()}")
        print(f"Expected Value of Difference: {expected_value}")
        print(f"Variance of Difference: {variance}")
        

    # def train_brain(self, game_boards, game_winner_colour):
    #     to_fit = self.generate_to_fit_vector(game_boards, game_winner_colour).ravel()
    #     game_boards_tensor = torch.tensor(game_boards, dtype=torch.float32)
    #     to_fit_tensor = torch.tensor(to_fit, dtype=torch.float32).view(-1, 1)

    #     self.optimizer.zero_grad()
    #     outputs = self.neural_network(game_boards_tensor)
    #     loss = self.criterion(outputs, to_fit_tensor)
    #     loss.backward()
    #     self.optimizer.step()

    def train_brain(self, game_data, game_winner_colour):
        # Extract board states from game_data
        board_states = [data['board'] for data in game_data]
        
        # Generate target values (0 or 1) based on the winner
        to_fit = self.generate_to_fit_vector(game_data, game_winner_colour).ravel()
        
        # Convert to tensors
        game_boards_tensor = torch.tensor(board_states, dtype=torch.float32)
        to_fit_tensor = torch.tensor(to_fit, dtype=torch.float32).view(-1, 1)

        # Train neural network
        self.optimizer.zero_grad()
        outputs = self.neural_network(game_boards_tensor)  # NN predictions
        loss = self.criterion(outputs, to_fit_tensor)  # Compute loss
        loss.backward()
        print("Before update:", self.neural_network.network[0].weight.data[0][:5])
        self.optimizer.step()
        print("After update:", self.neural_network.network[0].weight.data[0][:5])
        print(f"Pre-train Loss: {loss.item()}")



    # def generate_to_fit_vector(self, game_boards, game_winner_colour):
    #     game_boards_tensor = torch.tensor(game_boards, dtype=torch.float32)
    #     with torch.no_grad():
    #         initial_probability_array = self.neural_network(game_boards_tensor).numpy()

    #     computed_probability_array = [0] * len(initial_probability_array)
    #     sum_distance = 0
    #     next_value = game_winner_colour

    #     for i in range(len(initial_probability_array)-1, -1, -1):
    #         current_value = initial_probability_array[i]
    #         sum_distance += (next_value - current_value)
    #         computed_probability_array[i] = current_value + 0.05 * sum_distance
    #         sum_distance *= self.lambda_value
    #         next_value = initial_probability_array[i]

    #     return np.array(computed_probability_array)
    
    def generate_to_fit_vector(self, game_data, game_winner_colour):
        # Initialize the computed probability array
        win_lose_vector = np.zeros(len(game_data))
        last_board = game_data[-1]["board"]
        remaining_pieces = sum(abs(round(piece * 15)) for piece in last_board)
        if (remaining_pieces == 15):
            gain = 1.5
        elif (remaining_pieces > 3):
            gain = 1
        else:
            gain = 0.6

        # Assign 1 if the board belongs to the winner, otherwise 0
        for i in range(len(game_data)):
            color = game_data[i]['color']  # Get the color from the game_data entry
            win_lose_vector[i] = gain if color == game_winner_colour else 0

        return np.array(win_lose_vector)


    def black_white_scoring(self):
        test_board = Board()
        test_board.board = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 0]]
        with torch.no_grad():
            return self.neural_network(torch.tensor([test_board.board_to_vector(0)], dtype=torch.float32)).numpy(), \
                   self.neural_network(torch.tensor([test_board.board_to_vector(1)], dtype=torch.float32)).numpy()
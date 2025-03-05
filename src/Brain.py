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

    
    def generate_to_fit_vector(self, game_data, game_winner_colour):
        # Initialize the computed probability array
        win_lose_vector = np.zeros(len(game_data))
        last_board = game_data[-1]["board"]
        remaining_pieces = sum(abs(round(piece * 15)) for piece in last_board)
        if (remaining_pieces == 15):
            gain = 0.9
        elif (remaining_pieces > 3):
            gain = 1
        else:
            gain = 0.6

        # Assign 1 if the board belongs to the winner, otherwise 0
        for i in range(len(game_data)):
            color = game_data[i]['color']  # Get the color from the game_data entry
            win_lose_vector[i] = gain if color == game_winner_colour else 0

        return np.array(win_lose_vector)


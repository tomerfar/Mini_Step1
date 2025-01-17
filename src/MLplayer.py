import torch
from src.strategies import Strategy
from src.colour import Colour
from src.move_not_possible_exception import MoveNotPossibleException
from Brain import NeuralNetwork  # Assume this is your neural network class
from Brain import Brain
from itertools import permutations

class MLPlayer(Strategy):
    def __init__(self, colour: Colour, brain=None):
        self.colour = colour
        self.brain = brain if brain else NeuralNetwork(input_size=28)  # Assuming 28 is the input size
        self.game_history = []  # Store game history for training

    def move(self, board, colour: Colour, dice_roll, handle_move, game_context):
        """
        Decide on the best move using the neural network.
        """
        possible_moves = self.get_possible_moves(board)
        move_values = []

        for move in possible_moves:
            start_location, die_roll = move
            board_copy = board.create_copy()
            try:
                board_copy.move_piece(board_copy.get_piece_at(start_location), die_roll)
                board_state = board_copy.to_json()  # Get the board state as a JSON (or list, array, etc.)
                board_state_tensor = torch.tensor(board_state, dtype=torch.float32).unsqueeze(0)
                move_value = self.brain(board_state_tensor).item()  # Get the evaluation score from the network
                move_values.append((move, move_value))
            except MoveNotPossibleException:
                continue

        # Pick the move with the highest value
        best_move = max(move_values, key=lambda x: x[1])[0]
        start_location, die_roll = best_move
        handle_move(start_location, die_roll)  # Execute the move


    def generate_boards(self, board, colour, dice_rolls):
        """
         Generate all future possible boards the player is able to reach from a specific dice roll.
        Returns a dictionary where:
        - Key: Board state
        - Value: List of moves leading to that board
           """
        # Base case: If no dice rolls are left, return the current board as a single-item list
        if not dice_rolls: # Thats the place that will return the boards from the
            return {board: []}
        
        location_of_pieces = [x.location for x in board.get_pieces(colour)] # Gets a list of integers that says which locations on the board the player has pieces
        location_of_pieces = list(set(location_of_pieces)) # To avoid duplications, cause location might hold multiple pieces

        player_pieces = [board.get_piece_at(loc) for loc in location_of_pieces] # Retreives the actual pieces form each location on the board

        # die_roll = dice_rolls[0]
        # remaining_die_roll = dice_rolls[1:]

        resulting_boards = {} # Dictionary to store boards and their corresponding moves
        # Consider both orders of dice rolls
        for dice_order in (set(permutations(dice_rolls))):
            die_roll = dice_order[0]
            remaining_die_roll = dice_order[1:]


            for piece in player_pieces:
                if board.is_move_possible(piece, die_roll):
                    # valid_move_found = True  # At least one valid move was found
                    # Create a copy of the board and move the piece
                    board_copy = board.create_copy()
                    new_piece = board_copy.get_piece_at(piece.location)
                    board_copy.move_piece(new_piece, die_roll)

                    # Recursively generate boards for the remaining dice rolls after
                    subsequent_boards = self.generate_boards(board_copy, colour, remaining_die_roll)
                    if not subsequent_boards:
                        resulting_boards[board_copy] = [{'piece_at': piece.location, 'die_roll': die_roll}]
                    else:
                        for new_board, moves in subsequent_boards.items():
                            resulting_boards[new_board] = [{'piece_at': piece.location, 'die_roll':die_roll}] + moves

        return resulting_boards

    def train(self, game_boards, game_winner_colour):
        """
        Train the neural network on past game data.
        """
        self.brain.train_brain(game_boards, game_winner_colour)

    def save_brain(self, file_name):
        """
        Save the trained model to a file.
        """
        self.brain.save_brain(file_name)

    @staticmethod
    def load_brain(file_name):
        """
        Load a trained model from a file.
        """
        return NeuralNetwork.load_saved_brain(file_name)

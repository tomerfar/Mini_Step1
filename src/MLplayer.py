import torch
from src.strategies import Strategy
from src.colour import Colour
from src.move_not_possible_exception import MoveNotPossibleException
from src.Brain import NeuralNetwork  # Assume this is your neural network class
from src.Brain import Brain
from itertools import permutations

class MLPlayer(Strategy):
    def __init__(self, brain_file=None):
        self.brain = Brain()
        brain_file = input("Please enter the filename for the brain model: ")
        if brain_file:
            self.brain.load_saved_brain(brain_file)
        else:
            self.brain = NeuralNetwork(input_size=28)  # Assuming 28 is the input size
        self.game_history = []  # Store game history for training

    
    @staticmethod
    def get_difficulty():
        return "Machine Learning Player"


    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        """
        Decide on the best move using the neural network.
        """
        possible_moves = self.generate_boards(board, colour, dice_roll)
        optimal_move = [] # List that will hold tuples with 2 values : ((list of moves), move_value)
        if len(possible_moves) > 0:

            for gen_board, move in possible_moves.items():
                try:
                    board_vector = self.convert_board_to_vector(board=gen_board) # returns a vector representation of the board
                    board_state_tensor = torch.tensor(board_vector, dtype=torch.float32).unsqueeze(0)
                    move_value = self.brain.neural_network(board_state_tensor).item()  # Get the evaluation score from the network
                    optimal_move.append((move, move_value))
                except MoveNotPossibleException:
                    continue

            # Choose max/min value from the 2nd element in the tuple: x[1], extract the 1st value (the moves) :[0] 
            best_move = (max if colour == Colour.WHITE else min)(optimal_move, key=lambda x: x[1])[0]
            #best_move = (max)(optimal_move, key=lambda x: x[1])[0]
            

            for move in best_move:
                make_move(move['piece_at'], move['die_roll'])
    

    def convert_board_to_vector(self, board): # Convert board into a normalize vector
        board_vector = [0] * 28
        for location in range(1, 25):
            pieces = board.pieces_at(location)
            if len(pieces) > 0:
                board_vector[location - 1] = (len(pieces) if pieces[0].colour == Colour.WHITE else -len(pieces)) / 15 
        board_vector[24] = (len(board.pieces_at(0))) / 15  # White pieces blown 
        board_vector[25] = (len(board.pieces_at(25))) / 15  # Black pieces blown MIGHT NEED minus BEFORE THE len
        board_vector[26] = (len(board.get_taken_pieces(Colour.WHITE))) / 15  # White pieces eaten
        board_vector[27] = (len(board.get_taken_pieces(Colour.BLACK))) / 15  # Black pieces eaten MIGHT NEED minus BEFORE THE len
        return board_vector

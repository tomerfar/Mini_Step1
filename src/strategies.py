from asyncio import wait
import time
import math
import numpy as np
from random import shuffle
from src.piece import Piece
from src.move_not_possible_exception import MoveNotPossibleException
from src.colour import Colour
from itertools import permutations

import threading
import tkinter

#time test
#interface V
#im/ex mode
class Strategy:
    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        raise NotImplemented()
    

    def game_over(self, opponents_activity):
        pass


    def evaluate_board(self, myboard, colour):
        board_stats = self.assess_board(colour, myboard)

        board_value = board_stats['sum_distances'] - float(board_stats['sum_distances_opponent']) / 3 + \
                      float(board_stats['sum_single_distance_away_from_home']) / 6 - \
                      board_stats['number_occupied_spaces'] - board_stats['opponents_taken_pieces'] + \
                      3 * board_stats['pieces_on_board'] + float(board_stats['sum_distances_to_endzone']) / 6
        normalize_value = board_value / 310
        return normalize_value
    
    
    def assess_board(self, colour, myboard):
        pieces = myboard.get_pieces(colour)
        pieces_on_board = len(pieces)
        sum_distances = 0
        number_of_singles = 0
        number_occupied_spaces = 0
        sum_single_distance_away_from_home = 0
        sum_distances_to_endzone = 0
        for piece in pieces:
            sum_distances = sum_distances + piece.spaces_to_home()
            if piece.spaces_to_home() > 6:
                sum_distances_to_endzone += piece.spaces_to_home() - 6
        for location in range(1, 25):
            pieces = myboard.pieces_at(location)
            if len(pieces) != 0 and pieces[0].colour == colour:
                if len(pieces) == 1:
                    number_of_singles = number_of_singles + 1
                    sum_single_distance_away_from_home += 25 - pieces[0].spaces_to_home()
                elif len(pieces) > 1:
                    number_occupied_spaces = number_occupied_spaces + 1
        opponents_taken_pieces = len(myboard.get_taken_pieces(colour.other()))
        opponent_pieces = myboard.get_pieces(colour.other())
        sum_distances_opponent = 0
        for piece in opponent_pieces:
            sum_distances_opponent = sum_distances_opponent + piece.spaces_to_home()
        return {
            'number_occupied_spaces': number_occupied_spaces,
            'opponents_taken_pieces': opponents_taken_pieces,
            'sum_distances': sum_distances,
            'sum_distances_opponent': sum_distances_opponent,
            'number_of_singles': number_of_singles,
            'sum_single_distance_away_from_home': sum_single_distance_away_from_home,
            'pieces_on_board': pieces_on_board,
            'sum_distances_to_endzone': sum_distances_to_endzone,
        }
    
    def convert_board_to_vector(self, board): 
        # Convert board into a normalized vector
        board_vector = [0] * 28
        for location in range(1, 25):  # Locations 1 to 24
            pieces = board.pieces_at(location)
            if len(pieces) > 0:
                board_vector[location] = (len(pieces) if pieces[0].colour == Colour.WHITE else -len(pieces)) / 15
        
        # Blown pieces
        board_vector[0] = (len(board.pieces_at(0))) / 15  # White pieces blown
        board_vector[25] = -(len(board.pieces_at(25))) / 15  # Black pieces blown
    
        # Eaten pieces
        board_vector[26] = (len(board.get_taken_pieces(Colour.WHITE))) / 15  # White pieces eaten
        board_vector[27] = -(len(board.get_taken_pieces(Colour.BLACK))) / 15  # Black pieces eaten
    
        return board_vector
    

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
    

class MoveFurthestBackStrategy(Strategy):

    @staticmethod
    def get_difficulty():
        return "Medium"

    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        #wait 2 seconds before moving
        
        could_not_move_first_roll = False

        for i, die_roll in enumerate(dice_roll):
            moved = self.move_die_roll(board, colour, die_roll, make_move)
            if not moved and i == 0:
                could_not_move_first_roll = True

        if could_not_move_first_roll:
            self.move_die_roll(board, colour, dice_roll[0], make_move)

    @staticmethod
    def move_die_roll(board, colour, die_roll, make_move):
        valid_pieces = board.get_pieces(colour)
        valid_pieces.sort(key=Piece.spaces_to_home, reverse=True)
        for piece in valid_pieces:
            if board.is_move_possible(piece, die_roll):
                make_move(piece.location, die_roll)
                return True

        return False


class HumanStrategy(Strategy):
    def __init__(self, name):
        self.__name = name
        self.stop_input_event = threading.Event()  # Event to signal stopping input

    @staticmethod
    def get_difficulty():
        return "N/A"

    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        print("It is %s's turn, you are %s, your roll is %s" % (self.__name, colour, dice_roll))
        while len(dice_roll) > 0 and not board.has_game_ended():
            if self.stop_input_event.is_set():  # Check if input should stop
                print("Time limit reached, stopping input.")
                break
            board.print_board()
            if board.no_moves_possible(colour, dice_roll):
                print("There are no valid moves. Your turn has ended.")
                time.sleep(3)
                break
            print("You have %s left" % dice_roll)
            location = self.get_location(board, colour)
            piece = board.get_piece_at(location)
            while True:
                if self.stop_input_event.is_set():  # Check if input should stop
                    print("Time limit reached, stopping input.")
                    return
                try:
                    value = int(input("How far (or 0 to move another piece)?\n"))
                    if value == 0:
                        break                    
                    rolls_moved = make_move(piece.location, value)
                    for roll in rolls_moved:
                        dice_roll.remove(roll)
                    print("")
                    print("")
                    break
                except ValueError:
                    print("That's not a number! Try again")
                except MoveNotPossibleException as e:
                    print(str(e))

        print("Done!")

    def get_location(self, board, colour):
        value = None
        while value is None:
            if self.stop_input_event.is_set():  # Check if input should stop
                print("Time limit reached, stopping input.")
                return None
            try:
                location = int(input("Enter the location of the piece you want to move?\n"))
                piece_at_location = board.get_piece_at(location)
                if piece_at_location is None or piece_at_location.colour != colour:
                    print("You don't have a piece at location %s" % value)
                else:
                    value = location
            except ValueError:
                print("That's not a number! Try again")
        return value


class MoveRandomPiece(Strategy):

    @staticmethod
    def get_difficulty():
        return "Easy"

    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        for die_roll in dice_roll:
            valid_pieces = board.get_pieces(colour)
            shuffle(valid_pieces)
            for piece in valid_pieces:
                if board.is_move_possible(piece, die_roll):
                    make_move(piece.location, die_roll)
                    break



class MoveRandomTraining(Strategy):

    def __init__(self):
        self.game_data = []  # List to store board states and heuristic values


    @staticmethod
    def get_difficulty():
        return "Training stage 1"
    

    def move(self, board, colour, dice_roll, make_move, opponents_activity):

        for die_roll in dice_roll:
            valid_pieces = board.get_pieces(colour)
            shuffle(valid_pieces)
            for piece in valid_pieces:
                if board.is_move_possible(piece, die_roll):
                    # Capture board state and heuristic value before making the move
                    current_board_state = self.convert_board_to_vector(board=board) # Not sure we need it
                    heuristic_value = self.evaluate_board(myboard=board, colour=colour)

                    # Store the board state and heuristic in the game_data list
                    self.game_data.append({
                        "board": current_board_state,
                        "heuristic": heuristic_value
                    })

                    # Make the move
                    make_move(piece.location, die_roll)
                    break


class TrainingPhase2(Strategy):

    def __init__(self):
        self.game_data = []  # List of lists [{color: [board, value]}]


    @staticmethod
    def get_difficulty():
          return "Training stage 2"
    

    def move(self, board, colour, dice_rolls, make_move, opponents_activity):
        opponent_board = self.convert_board_to_vector(board.create_copy())
        self.game_data.append({
                "board": opponent_board,
                "color": colour.other(),
            })
        optimal_move = []
        boards_and_values = {}
        
         
        possible_boards_with_moves = self.generate_boards(board, colour, dice_rolls) # List of all possible boards for the player with the current dice rolls
        if len(possible_boards_with_moves) == 0:
            i = 0 # so we wont enter the else statement
            #print("Didn't generate any boards.\n")
        else: 
            for b in possible_boards_with_moves.keys():
                boards_and_values[b] = math.exp(self.evaluate_board(b,colour=colour)) # Value = e^(heuristic_value)

            # Sort the boards_and_values dictionary by its values (heuristic values) in descending order
            sorted_boards_and_values = dict(sorted(boards_and_values.items(), key=lambda item: item[1], reverse=True))

            # Take the top 4 entries from the sorted dictionary
            top_4_boards_and_values = dict(list(sorted_boards_and_values.items())[:min(4, len(sorted_boards_and_values))])

            # Extract boards and weights
            boards = list(top_4_boards_and_values.keys())
            weights = np.array(list(top_4_boards_and_values.values()), dtype=np.float64)

            # Normalize weights to convert them into probabilities
            probabilities = weights / np.sum(weights)

            # Randomly select a board state based on the probabilities
            selected_board = np.random.choice(boards, p=probabilities)
            optimal_move = possible_boards_with_moves[selected_board]

            self.game_data.append({
                    "board": self.convert_board_to_vector(selected_board),
                    "color": colour
                })

        if len(optimal_move) > 0:
            for move in optimal_move:
                make_move(move['piece_at'], move['die_roll'])
    


        




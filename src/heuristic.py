from src.piece import Piece

class Heuristic:

    def __init__(self):
        
        self.weights = {
            "distances_to_home": 1.5,   # Weight for distance from home
            "pieces in safe zones": 0.5,      # Weight for occupied spaces
            "number of safe zones": 1.5, # Number of houses we built on the board
            "number of opponents safe zones": -1.5, # Number of houses the opponent has on the board
            "number_of_singles": 1.0,    # Weight for single pieces
            "opponent_pieces": -1.0, # Weight for opponent's taken pieces
            "taken pieces": -1.0, # Number of opponent's pieces we take in captivity
            "opponents singles": 1.0, # Number of opponent's pieces that are single on the board
            "opponent distance to home": -1.0 # Weight for distance of opponent's pieces from home
        }

    def evaluate(self, board, colour):
        """
    This method evaluates the board for a given player (colour) and returns a score.
    The score should reflect how favorable the board state is for the given player.
    """
            

    def assess_board(self, colour, myboard):
        # Initialize variables
        pieces = myboard.get_pieces(colour)
        pieces_on_board = len(pieces)
        sum_distances_to_home = 0
        number_of_singles = 0
        pieces_in_safe_zones = 0
        number_of_safe_zones = 0
        opponents_taken_pieces = len(myboard.get_taken_pieces(colour.other()))
        opponent_pieces = myboard.get_pieces(colour.other())
        sum_opponent_distances_to_home = 0
        opponent_singles = 0
        opponent_safe_zones = 0

        # Calculate distances to home for player's pieces
        for piece in pieces:
            sum_distances_to_home += piece.spaces_to_home()
            if piece.is_in_safe_zone():  # Assuming a method for safe zones exists
                pieces_in_safe_zones += 1

        # Evaluate player's board spaces
        for location in range(1, 25):  # Assuming 24 positions on the board
            pieces_at_location = myboard.pieces_at(location)
            if len(pieces_at_location) != 0 and pieces_at_location[0].colour == colour:
                if len(pieces_at_location) == 1:
                    number_of_singles += 1
                elif len(pieces_at_location) > 1:
                    number_of_safe_zones += 1

        # Evaluate opponent's board spaces
        for piece in opponent_pieces:
            sum_opponent_distances_to_home += piece.spaces_to_home()
            if piece.is_in_safe_zone():  # Assuming the same safe zone check applies
                opponent_safe_zones += 1

        for location in range(1, 25):
            opponent_pieces_at_location = myboard.pieces_at(location)
            if len(opponent_pieces_at_location) != 0 and opponent_pieces_at_location[0].colour == colour.other():
                if len(opponent_pieces_at_location) == 1:
                    opponent_singles += 1

        # Return the values mapped to heuristic dictionary keys
        return {
            "distances_to_home": sum_distances_to_home,
            "pieces in safe zones": pieces_in_safe_zones,
            "number of safe zones": number_of_safe_zones,
            "number of opponents safe zones": opponent_safe_zones,
            "number_of_singles": number_of_singles,
            "opponent_pieces": len(opponent_pieces),
            "taken pieces": opponents_taken_pieces,
            "opponents singles": opponent_singles,
            "opponent distance to home": sum_opponent_distances_to_home,
        }

 
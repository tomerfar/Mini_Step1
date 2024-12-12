from src.piece import Piece

class Heuristic:

    def __init__(self):
        
        self.weights = {
             'pieces on board': 1.0,
             'sum distances': 1.5,
             'number of_safe_zones': 2.0,
             'number of singles': -1.0,
             'number of opponent safe zones': -1.0,
             'sum_single_distance_away_from_home': -0.5,
             'sum_distances_to_endzone': 1.0,
             'taken_pieces': -1.0,
             'sum distances opponent': -1.0,
             'number_of_opponent_safe_zones': -1.0,
             'number_of_opponent_singles': 1.0,
             'sum_opponent_single_distance_away_from_home': -0.5,
             'opponents_taken_pieces': 1.5,
             'opponent_pieces': -1.0
        }

    def evaluate(self, myboard, colour) -> float :
        """
    This method evaluates the board for a given player (colour) and returns a score.
    The score should reflect how favorable the board state is for the given player.
    """
        board_stats = self.assess_board(colour, myboard)
        board_result = 0

        for key in board_stats.keys():
           board_result +=  board_stats[key] * self.weights[key]
        
        return board_result
        
            

    def assess_board(self, colour, myboard):
        pieces = myboard.get_pieces(colour)
        pieces_on_board = len(pieces)

        sum_distances = 0
        number_of_safe_zones = 0
        number_of_singles = 0
        sum_single_distance_away_from_home = 0
        sum_distances_to_endzone = 0
        taken_pieces = len(myboard.get_taken_pieces(colour))
        
        
        sum_distances_opponent = 0
        number_of_opponent_safe_zones = 0
        number_of_opponent_singles = 0
        sum_opponent_single_distance_away_from_home = 0
                
        for piece in pieces:
            sum_distances += piece.spaces_to_home()
            if piece.spaces_to_home() > 6:
                sum_distances_to_endzone += piece.spaces_to_home() - 6

        for location in range(1, 25):
            pieces = myboard.pieces_at(location)
            if len(pieces) != 0:
                if pieces[0].colour == colour:
                    if len(pieces) == 1:
                        number_of_singles += 1
                        sum_single_distance_away_from_home += 25 - pieces[0].spaces_to_home()
                    elif len(pieces) > 1:
                        number_of_safe_zones += 1
                else:
                     if len(pieces) == 1:
                        number_of_opponent_singles += 1
                        sum_opponent_single_distance_away_from_home += 25 - pieces[0].spaces_to_home()
                     else: 
                        number_of_opponent_safe_zones += 1 
                    
        opponents_taken_pieces = len(myboard.get_taken_pieces(colour.other()))
        opponent_pieces = myboard.get_pieces(colour.other())

        for piece in opponent_pieces:
            sum_distances_opponent += piece.spaces_to_home()
        return {
            'pieces on board': pieces_on_board,
            'sum distances': sum_distances,
            'number of_safe_zones': number_of_safe_zones,
            'number of singles': number_of_singles,
            'number of opponent safe zones': number_of_opponent_safe_zones,
            'sum_single_distance_away_from_home': sum_single_distance_away_from_home,
            'sum_distances_to_endzone': sum_distances_to_endzone,
            'taken_pieces': taken_pieces,
            'sum distances opponent': sum_distances_opponent,
            'number_of_opponent_safe_zones': number_of_opponent_safe_zones,
            'number_of_opponent_singles': number_of_opponent_singles,
            'sum_opponent_single_distance_away_from_home': sum_opponent_single_distance_away_from_home,
            'opponents_taken_pieces': opponents_taken_pieces,
            'opponent_pieces': opponent_pieces
               }

 
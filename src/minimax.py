from src.compare_all_moves_strategy import CompareAllMoves
from src.piece import Piece


class CompareAllMovesMinMax(CompareAllMoves):

    @staticmethod
    def get_difficulty():
        return "MiniMax"

    def evaluate_board(self, myboard, colour):
        """
        Evaluate the board using all available stats for a comprehensive score.
        """
        board_stats = self.assess_board(colour, myboard)

        # Extract statistics from assess_board
        sum_distances = board_stats['sum_distances']
        sum_distances_opponent = board_stats['sum_distances_opponent']
        number_of_singles = board_stats['number_of_singles']
        sum_single_distance_away_from_home = board_stats['sum_single_distance_away_from_home']
        number_occupied_spaces = board_stats['number_occupied_spaces']
        opponents_taken_pieces = board_stats['opponents_taken_pieces']
        pieces_on_board = board_stats['pieces_on_board']
        sum_distances_to_endzone = board_stats['sum_distances_to_endzone']

        # Comprehensive scoring formula
        board_value = (
            -sum_distances  # Minimize the distance of own pieces
            + number_of_singles * 1.5  # Penalize having singles
            - number_occupied_spaces * 2  # Encourage occupying more spaces
            + opponents_taken_pieces * 2  # Reward capturing opponent pieces
            - sum_distances_opponent * 0.5  # Penalize if opponent pieces are closer
            + pieces_on_board * 3  # Reward having more pieces on the board
            + sum_distances_to_endzone * 0.2  # Reward progress towards the end zone
            - 3 * self.count_vulnerable_pieces(myboard, colour)  # Penalize vulnerable pieces
            + 2 * self.count_protected_pieces(myboard, colour)  # Reward protected pieces
            + sum_single_distance_away_from_home * 0.1  # Reward vulnerable pieces closer to home
        )

        return board_value

    def assess_board(self, colour, myboard):
        pieces = myboard.get_pieces(colour)
        pieces_on_board = len(pieces)
        sum_distances = 0
        number_of_singles = 0
        number_occupied_spaces = 0
        sum_single_distance_away_from_home = 0
        sum_distances_to_endzone = 0

        # Calculate board stats for own pieces
        for piece in pieces:
            sum_distances += piece.spaces_to_home()
            if piece.spaces_to_home() > 6:
                sum_distances_to_endzone += piece.spaces_to_home() - 6
            if piece.is_single():
                number_of_singles += 1
                sum_single_distance_away_from_home += 25 - piece.spaces_to_home()

        # Count number of occupied spaces by own pieces
        for location in range(1, 25):
            pieces_at_location = myboard.pieces_at(location)
            if pieces_at_location and pieces_at_location[0].colour == colour:
                if len(pieces_at_location) == 1:
                    number_of_singles += 1
                elif len(pieces_at_location) > 1:
                    number_occupied_spaces += 1

        # Calculate opponent stats
        opponent_pieces = myboard.get_pieces(colour.other())
        sum_distances_opponent = 0
        opponents_taken_pieces = len(myboard.get_taken_pieces(colour.other()))
        for piece in opponent_pieces:
            sum_distances_opponent += piece.spaces_to_home()

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

    # You will need to implement these helper functions
    def count_vulnerable_pieces(self, myboard, colour):
        # Example of how you might calculate vulnerable pieces
        # Return the number of pieces that are vulnerable (e.g., single pieces in open spaces)
        return sum(1 for piece in myboard.get_pieces(colour) if piece.is_vulnerable())

    def count_protected_pieces(self, myboard, colour):
        # Example of how you might calculate protected pieces
        # Return the number of pieces that are protected (e.g., pieces with other pieces around them)
        return sum(1 for piece in myboard.get_pieces(colour) if piece.is_protected())

    
    def generate_possible_dice_rolls_with_probabilities(self):
        """
        Generate all possible dice rolls for the opponent's next turn,
        along with their probabilities.
        Returns a list of tuples: (roll, probability).
        """
        possible_rolls_with_probs = []
        for die1 in range(1, 7):
            for die2 in range(1, 7):
                if die1 == die2:
                    # Double roll, probability is 1/36
                    possible_rolls_with_probs.append(([die1, die1, die1, die1], 1/36))
                else:
                    # Mixed roll, probability is 2/36
                    possible_rolls_with_probs.append(([die1, die2], 2/36))
        return possible_rolls_with_probs
        
    def generate_possible_dice_rolls(self):
        """
        Generate all possible dice rolls for the opponent's next turn.
        Returns a list of all possible combinations of dice rolls.
        """
        possible_rolls = []
        for die1 in range(1, 7):
            for die2 in range(1, 7):
                if die1 == die2:
                    # Double roll, four moves
                    possible_rolls.append([die1, die1, die1, die1])
                else:
                    # Two dice rolls
                    possible_rolls.append([die1, die2])
        return possible_rolls
    
    
    #tree
    def _init_(self, depth=2):
        super()._init_()
        self.depth = depth

    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        # Stage 1: Get the initial board states and moves leading to them
        result = self.move_recursively_first_stage(board, colour, dice_roll)
        
        best_values_for_boards = {}  # To store best move value for each board
        best_moves_for_boards = {}   # To store best move for each board
        all_combination_of_dice_rolls = self.generate_possible_dice_rolls()  # Possible dice rolls for stage 2

        # Stage 2: For each board, evaluate all dice rolls
        for copy_of_board in result['all boards'].keys():
            best_move_for_current_board = None
            best_move_value = float('inf')  # Start with an infinitely high value to minimize
            
            # Store the sequence of moves that led to this board
            move_sequence = result['all boards'][copy_of_board]
            
            # Evaluate the best move for the current board based on all dice rolls
            for dice_rolls in all_combination_of_dice_rolls:
                move_and_value = self.move_recursively_2nd_stage(copy_of_board, colour, dice_rolls)
                
                # Find the best move for this board
                if move_and_value['best_value'] < best_move_value:
                    best_move_value = move_and_value['best_value']
                    best_move_for_current_board = move_and_value['best_moves']

            # Store the best move and the corresponding board value
            best_moves_for_boards[copy_of_board] = {
                'best_move': best_move_for_current_board,
                'best_value': best_move_value,
                'move_sequence': move_sequence  # The moves that led to this board
            }

        # Stage 3: Select the best board across all possible boards
        final_best_move = None
        final_best_value = float('inf')
        final_move_sequence = []

        for board, data in best_moves_for_boards.items():
            # Compare the best values of all boards and pick the best one
            if data['best_value'] < final_best_value:
                final_best_value = data['best_value']
                final_best_move = data['best_move']
                final_move_sequence = data['move_sequence']  # Get the moves that led to this board

        # final_best_move is the move to play. Now we apply the moves from the best move sequence.
        if final_best_move:
            # Apply all moves that led to this optimal board state
            for move in final_move_sequence:
                make_move(move['piece_at'], move['die_roll'])  # Adjusted to match the original code format

        return {'best_value': final_best_value, 'best_moves': final_best_move}


        
                




    def move_recursively_first_stage(self, board, colour, dice_rolls):

        all_boards = {}
        moves_history = []

        best_board_value = float('inf')
        best_pieces_to_move = []

        pieces_to_try = [x.location for x in board.get_pieces(colour)]
        pieces_to_try = list(set(pieces_to_try))

        valid_pieces = []
        for piece_location in pieces_to_try:
            valid_pieces.append(board.get_piece_at(piece_location))
        valid_pieces.sort(key=Piece.spaces_to_home, reverse=True)

        dice_rolls_left = dice_rolls.copy()
        die_roll = dice_rolls_left.pop(0)

        for piece in valid_pieces:
            if board.is_move_possible(piece, die_roll):
                board_copy = board.create_copy()
                new_piece = board_copy.get_piece_at(piece.location)
                board_copy.move_piece(new_piece, die_roll)

                # Store the moves that led to this board
                new_moves_history = moves_history + [{'die_roll': die_roll, 'piece_at': piece.location}]
                all_boards[board_copy] = new_moves_history  # Store the sequence of moves leading to this board

                # If there are remaining dice rolls, recurse
                if len(dice_rolls_left) > 0:
                    result = self.move_recursively(board_copy, colour, dice_rolls_left)
                    if len(result['best_moves']) == 0:
                        # we've done the best we can do
                        board_value = self.evaluate_board(board_copy, colour)
                        if board_value < best_board_value and len(best_pieces_to_move) < 2:
                            best_board_value = board_value
                            best_pieces_to_move = [{'die_roll': die_roll, 'piece_at': piece.location}]
                    elif result['best_value'] < best_board_value:
                        new_best_moves_length = len(result['best_moves']) + 1
                        if new_best_moves_length >= len(best_pieces_to_move):
                            best_board_value = result['best_value']
                            move = {'die_roll': die_roll, 'piece_at': piece.location}
                            best_pieces_to_move = [move] + result['best_moves']
                else:
                    # If no more dice rolls, evaluate the final position
                    if len(new_moves_history) < len(best_pieces_to_move):
                        best_board_value = self.evaluate_board(board_copy, colour)
                        best_pieces_to_move = new_moves_history
                    # If move is not possible, store the sequence of moves
                    new_moves_history = moves_history + [{'die_roll': die_roll, 'piece_at': piece.location}]
                    all_boards[board_copy] = new_moves_history  # Store the sequence of moves leading to this board
                

        return {'best_value': best_board_value,
                'best_moves': best_pieces_to_move,
                'all_boards': all_boards}  # Return all boards with the move sequences leading to them


    def move_recursively_2nd_stage(self, board, colour, dice_rolls):
        best_board_value = float('inf')
        best_pieces_to_move = []

        pieces_to_try = [x.location for x in board.get_pieces(colour)]
        pieces_to_try = list(set(pieces_to_try))

        valid_pieces = []
        for piece_location in pieces_to_try:
            valid_pieces.append(board.get_piece_at(piece_location))
        valid_pieces.sort(key=Piece.spaces_to_home, reverse=True)

        dice_rolls_left = dice_rolls.copy()
        die_roll = dice_rolls_left.pop(0)

        for piece in valid_pieces:
            if board.is_move_possible(piece, die_roll):
                board_copy = board.create_copy()
                new_piece = board_copy.get_piece_at(piece.location)
                board_copy.move_piece(new_piece, die_roll)
                if len(dice_rolls_left) > 0:
                    result = self.move_recursively(board_copy, colour, dice_rolls_left)
                    if len(result['best_moves']) == 0:
                        # we have done the best we can do
                        board_value = self.evaluate_board(board_copy, colour)
                        if board_value < best_board_value and len(best_pieces_to_move) < 2:
                            best_board_value = board_value
                            best_pieces_to_move = [{'die_roll': die_roll, 'piece_at': piece.location}]
                    elif result['best_value'] < best_board_value:
                        new_best_moves_length = len(result['best_moves']) + 1
                        if new_best_moves_length >= len(best_pieces_to_move):
                            best_board_value = result['best_value']
                            move = {'die_roll': die_roll, 'piece_at': piece.location}
                            best_pieces_to_move = [move] + result['best_moves']
                else:
                    board_value = self.evaluate_board(board_copy, colour)
                    if board_value < best_board_value and len(best_pieces_to_move) < 2:
                        best_board_value = board_value
                        best_pieces_to_move = [{'die_roll': die_roll, 'piece_at': piece.location}]

        return {'best_value': best_board_value,
                'best_moves': best_pieces_to_move}

    
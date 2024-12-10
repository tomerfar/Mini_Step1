import time
from src.strategies import Strategy
from itertools import product
from src.piece import Piece
from src.heuristic import Heuristic
from src.board import Board

class MinimaxStrategy(Strategy):
    def __init__(self, max_depth=3, time_limit=-1):
        self.max_depth = max_depth
        self.time_limit = time_limit

    def move(self, board, colour, dice_roll, make_move, opponents_activity):
        start_time = time.time()
        best_move = None
        best_score = float('-inf')

        depth = 1
        while True:
            if self.time_limit != -1 and time.time() - start_time > self.time_limit:
                break  # Stop searching if time is up

            current_best_move, score = self.minimax(board, colour, depth, True, float('-inf'), float('inf'))
            if score > best_score:
                best_move = current_best_move
                best_score = score

            depth += 1

            if time.time() - start_time > self.time_limit:
                break  # Stop if time is up

        make_move(best_move[0], best_move[1])  # execute the best move

    def minimax(self, board, colour, depth, maximizing_player, current_dice_roll, alpha, beta):
        # Base case: If we've reached the maximum depth or the game is over
        if depth == 0 or board.has_game_ended(): # Tomer - Not sure that we need the condition of the depth.
            return None, self.evaluate_board(board, colour) 

        possible_moves = self.get_possible_moves(board, colour, current_dice_roll)
        best_move = None

        if maximizing_player:
            max_eval = float('-inf')
            for move in possible_moves:
                new_board = board.copy()  # Create a new board after making the move
                new_board.make_move(move[0], move[1])  # Apply move
                next_dice_rolls = self.generate_dice_rolls()

                for dice_roll in next_dice_rolls:
                    _, eval = self.minimax(new_board, colour, depth - 1, False, dice_roll, alpha, beta)
                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Prune the search tree
            return best_move, max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                new_board = board.copy()  # Create a new board after making the move
                new_board.make_move(move[0], move[1])  # Apply move
                next_dice_rolls = self.generate_dice_rolls()

                for dice_roll in next_dice_rolls:
                    _, eval = self.minimax(new_board, colour, depth - 1, True, dice_roll, alpha, beta)
                    if eval < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Prune the search tree
            return best_move, min_eval

    def evaluate_board(self, board, colour):
        # Implement your evaluation function here
        # For example, evaluate based on distance to home and piece safety
        #score = 0
        #for piece in board.get_pieces(colour):
            #score += piece.spaces_to_home()  # Adjust based on piece position
        #return score
        return Heuristic.evaluate(board, colour)

    def get_possible_moves(self, board, colour, dice_rolls):            #needs to be changed 
        # Returns a list of possible moves given the board and colour
        moves = []
        valid_pieces = board.get_pieces(colour)
        for piece in valid_pieces:
            for die_roll in dice_rolls:
                if board.is_move_possible(piece, die_roll):
                    moves.append((piece.location, die_roll))  # Store piece location and dice roll
        return moves
    
    def move_recursively_player(self, board, colour, dice_rolls):
        best_board_value = float('inf')
        best_pieces_to_move = []
        board_after_moves = [] # Store all of the copied boards we created.

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
                    result = self.move_recursively_player(board_copy, colour, dice_rolls_left)
                    if len(result['best_moves']) == 0:
                        # we have done the best we can do
                        board_value = self.evaluate_board(board_copy, colour)
                        if board_value > best_board_value and len(best_pieces_to_move) < 2:
                            best_board_value = board_value
                            best_pieces_to_move = [{'die_roll': die_roll, 'piece_at': piece.location}]
                    elif result['best_value'] > best_board_value:
                        new_best_moves_length = len(result['best_moves']) + 1
                        if new_best_moves_length >= len(best_pieces_to_move):
                            best_board_value = result['best_value']
                            move = {'die_roll': die_roll, 'piece_at': piece.location}
                            best_pieces_to_move = [move] + result['best_moves']
                else:
                    board_value = self.evaluate_board(board_copy, colour)
                    if board_value > best_board_value and len(best_pieces_to_move) < 2:
                        best_board_value = board_value
                        best_pieces_to_move = [{'die_roll': die_roll, 'piece_at': piece.location}]

                board_after_moves.append(board_copy) # Saves the finialized board after completing every move.

        return {'best_value': best_board_value,
                'best_moves': best_pieces_to_move,
                'boards_after_moves_list': board_after_moves}
    

    def generate_dice_rolls(dice_faces=6):
        # Generate all possible pairs of dice rolls (1 to 6)
        dice_rolls = list(product(range(1, dice_faces + 1), repeat=2))
        
        # Filter out symmetrical rolls (like (1,3) and (3,1))
        dice_rolls = [roll for roll in dice_rolls if roll[0] <= roll[1]]
        
        return dice_rolls

    
    def tomer_move(self, board, colour, dice_roll, make_move, opponents_activity):
        # First, perform the recursive moves for the player
        result_player = self.move_recursively_player(board, colour, dice_roll) # return a dict which hold the best move for the player, the value of it, and all of the boards
        
        # Now that the player has made their moves, we check all of the resulting boards and evaluate them
        boards_after_moves = result_player['boards_after_moves_list']
        
        best_board_value = float('inf')
        best_moves = []
        dice_rolls = self.generate_dice_rolls(dice_faces=6) # Creates all possible pairs of dice
        # For each resulting board from the player's move, evaluate the opponent's possible moves
        for saved_board in boards_after_moves: # Iterate on each of the saved boards
            for dice_roll in dice_rolls:
                result_opponent = self.move_recursively_opponent(saved_board, colour, dice_roll, opponents_activity)

            # Needs to do some override on results that we take as the best move.
            # After evaluating the opponents moves, the results we get from there consider to be the best move for us
            # Even if their value is lower then the players results , since we level down in the recursion.

            # Compare the result from the opponent's recursive evaluation
            if result_opponent['best_value'] < best_board_value:
                best_board_value = result_opponent['best_value']
                best_moves = result_opponent['best_moves']

        # Make the best moves based on the evaluation
        if best_moves:
            for move in best_moves:
                make_move(move['piece_at'], move['die_roll'])

        return best_board_value, best_moves
    

    
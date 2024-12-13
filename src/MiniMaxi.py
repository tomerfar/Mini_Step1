from src.strategies import Strategy
from src.piece import Piece
from src.colour import Colour
from src.board import Board
import time
import threading



class MiniMax(Strategy):


    def __init__(self, depth=2, time_limit=5.0):
        super().__init__()
        self.MAX_DEPTH = depth
        #self.time_limit = time_limit  # Time limit in seconds
        self.stop_input_event = threading.Event()  # Event to signal stopping input

        self.weights = { # Dictionary that holds values for the evaluate function
             #'pieces on board': 1.0,
             'sum distances': -0.5,
             'number of_safe_zones': 5.0,
             'number of singles': -3.0,
             'number of opponent safe zones': -1.0,
             'sum_single_distance_away_from_home': -1,
             'sum_distances_to_endzone': -1.0,
             'taken_pieces': -5.0,
             'sum distances opponent': 0.5,
             'number_of_opponent_safe_zones': -5.0,
             'number_of_opponent_singles': 3.0,
             'sum_opponent_single_distance_away_from_home': 1,
             'opponents_taken_pieces': 5,
             #'opponent_pieces': -1.0
        }

    @staticmethod
    def get_difficulty():
        return "Minimax"
    
    def move(self, board, colour, dice_rolls, make_move, opponents_activity):
        """
        Select the best move based on the minimax algorithm and execute it using make_move.

        Args:
            board (Board): The current board state.
            colour (str): The colour of the player.
            dice_rolls (list): List of dice rolls (e.g., [3, 5] or [6, 6, 6, 6]).
            make_move (callback): Callback function to handle the actual move.
            opponents_activity (any): Information about the opponent's activity (currently unused).

        Returns:
            None
        """

        if board.has_game_ended():
            return

         # Start the timer thread
        # self.stop_input_event.clear()
        # timer_thread = threading.Thread(target=self._start_timer)
        # timer_thread.start()
        
        best_score = float('-inf')
        optimal_move = []
         
        # try:     
        #if not board.has_game_ended():
        print("It is AI turn, his colour is %s, your roll is %s" % (colour, dice_rolls))
        possible_boards_with_moves = self.generate_boards(board, colour, dice_rolls) # List of all possible boards for the player with the current dice rolls
        # best_score = float('-inf')
        #optimal_board = None # To store the board with the best score
        # optimal_move = [] # To store the sequence of moves led to the best board

        for b, moves in possible_boards_with_moves.items(): # Iterating through the dict key&value
            if self.stop_input_event.is_set():
                print("Time limit reached during AI computation. Making the best move found so far.")
                break

            score_for_board_state = self.minimax(board=b,colour=colour, depth=self.MAX_DEPTH, is_maximizing_player=True)
            if score_for_board_state > best_score:
                print(f"new move is the best now, and the move is : {moves}")
                best_score = score_for_board_state
                #optimal_board = b
                optimal_move = moves

        # finally:
        #     self.stop_input_event.set()  # Ensure the timer thread stops

        if len(optimal_move) > 0:
            for move in optimal_move:
                make_move(move['piece_at'], move['die_roll'])

    def _start_timer(self):
        """
        Timer thread to stop input after the time limit.
        """
        time.sleep(self.time_limit)
        self.stop_input_event.set()


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
        player_pieces.sort(key=Piece.spaces_to_home, reverse=True) # Sorts them by their distance to home. maybe we don't need it

        die_roll = dice_rolls[0]
        remaining_die_roll = dice_rolls[1:]

        resulting_boards = {} # Dictionary to store boards and their corresponding moves

        for piece in player_pieces:
            if board.is_move_possible(piece, die_roll):
                # Create a copy of the board and move the piece
                board_copy = board.create_copy()
                new_piece = board_copy.get_piece_at(piece.location)
                board_copy.move_piece(new_piece, die_roll)

                # Recursively generate boards for the remaining dice rolls after
                subsequent_boards = self.generate_boards(board_copy, colour, remaining_die_roll)
                for new_board, moves in subsequent_boards.items():
                    resulting_boards[new_board] = [{'piece_at': piece.location, 'die_roll':die_roll}] + moves

        return resulting_boards
    

    def generate_dice_rolls(self):
        """
        Generate all possible dice rolls (d1, d2) where d1 and d2 are between 1 and 6,
        and treats [1,2] as equivalent to [2,1] for backgammon, adding only [1,2] and not [2,1].
        """
        dice_rolls = []

        for d1 in range(1, 7):
            for d2 in range(d1, 7):
                if d1 == d2:  # Only generate one of [1,2] or [2,1], not both
                    probability = 1 / 36
                else:
                    probability = 1 / 18
                
                dice_rolls.append(((d1, d2), probability))

        return dice_rolls


    def minimax(self, board, colour, depth, is_maximizing_player):
        """
            Recursively calculates the minimax score for a given board state, considering all possible dice rolls and moves.

            Args:
                board (Board): The current board state.
                depth (int): The depth of recursion (how many moves ahead to consider).
                is_maximizing_player (bool): Flag indicating whether the current player is the maximizing player.

            Returns:
                float: The evaluated score for the current board state.
                    - A higher score is better for the maximizing player, and a lower score is better for the minimizing player.
                    - The score is adjusted based on dice probabilities.
            """
        #print(f"Entering minimax: Depth={depth}, Maximizing Player={is_maximizing_player}")

        if self.stop_input_event.is_set():
            print("Time limit reached, stopping input.")
            return float('-inf') if is_maximizing_player else float('inf')
        if depth == 0 : #Tomer - needs to add here some function / methods that the function will also stop depending on the time
            #self.stop_input_event.is_set() maybe we need it
            return self.evaluate_board(board,colour=colour) # Needs to asses board here, add a function
        
        all_combinations = self.generate_dice_rolls() # Check if it creates doubles.
        
        for (d1, d2), prob in all_combinations:
            possible_boards = self.generate_boards(board, colour.other() if is_maximizing_player else colour, dice_rolls=[d1,d2])

        if is_maximizing_player:
            best_score = float('-inf')
            for b, moves in possible_boards.items():
                if self.stop_input_event.is_set():
                        print("Time limit reached, stopping input.")
                        return best_score  # Return the best score found so far
                score_for_board_state = self.minimax(b,colour=colour, depth=depth - 1, is_maximizing_player=not is_maximizing_player)
                score_for_board_state *= prob
                best_score = max(best_score, score_for_board_state)
            #print(f"best score: {best_score}")
        
        else:
            best_score = float('inf')
            for b, moves in possible_boards.items():
                if self.stop_input_event.is_set():
                        print("Time limit reached, stopping input.")
                        return best_score  # Return the best score found so far
                score_for_board_state = self.minimax(b,colour=colour, depth=depth - 1, is_maximizing_player=not is_maximizing_player)
                score_for_board_state *= prob
                best_score = min(best_score, score_for_board_state)
            #print(f"best score: {best_score}")

        return best_score

    
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
        opponent_pieces = (myboard.get_pieces(colour.other()))

        for piece in opponent_pieces:
            sum_distances_opponent += piece.spaces_to_home()
        return {
            #'pieces on board': pieces_on_board,
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
            #'opponent_pieces': opponent_pieces
                }
    

    def evaluate_board(self, myboard, colour):
            """
        This method evaluates the board for a given player (colour) and returns a score.
        The score should reflect how favorable the board state is for the given player.
        """
            board_stats = self.assess_board(colour, myboard)
            board_result = 0

            for key in board_stats.keys():
                board_result +=  board_stats[key] * self.weights[key]
            
            return board_result




from src.strategies import Strategy
from src.piece import Piece
from src.colour import Colour
from src.board import Board



class MiniMax(Strategy):


    def __init__(self, depth=3):
        super().__init__()
        self.MAX_DEPTH = depth

    @staticmethod
    def get_difficulty():
        return "Minimax"
    
    def move(self, board, colour, dice_rolls, make_move, opponents_activity):
        """
        Select the best move based on the minimax algorithm and execute it using make_move.

        Args:
            board (BoardState): The current board state.
            colour (str): The colour of the player.
            dice_rolls (list): List of dice rolls (e.g., [3, 5] or [6, 6, 6, 6]).
            make_move (callback): Callback function to handle the actual move.
            opponents_activity (any): Information about the opponent's activity (currently unused).

        Returns:
            None
        """
        possible_boards_with_moves = self.generate_boards(board, colour, dice_rolls) # List of all possible boards for the player with the current dice rolls

        best_score = float('-inf')
       #optimal_board = None # To store the board with the best score
        optimal_move = [] # To store the sequence of moves led to the best board

        for b, moves in possible_boards_with_moves.items(): # Iterating through the dict key&value
            score_for_board_state = self.minimax(board=b,colour=colour, depth=self.MAX_DEPTH, is_maximizing_player=True)
            if score_for_board_state > best_score:
                best_score = score_for_board_state
                #optimal_board = b
                optimal_move = moves

        if len(optimal_move) > 0:
            for move in optimal_move:
                make_move(move['piece_at'], move['die_roll'])


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
                    resulting_boards[new_board] = [{'piece_at': piece.location, 'die_roll':die_roll}] + moves ## Needs to check this one if its correct.

        return resulting_boards
    

    def generate_dice_rolls(self):
        """
        Generate all possible dice rolls (d1, d2) where d1 and d2 are between 1 and 6,
        and treats [1,2] as equivalent to [2,1] for backgammon, adding only [1,2] and not [2,1].
        """
        dice_rolls = []

        for d1 in range(1, 7):
            for d2 in range(d1, 7):  # Only generate one of [1,2] or [2,1], not both
                probability = 1 / 36  # Each pair of dice rolls has a probability of 1/36
                dice_rolls.append(((d1, d2), probability))

        return dice_rolls


    def minimax(self, board, colour, depth, is_maximizing_player):
        """
            Recursively calculates the minimax score for a given board state, considering all possible dice rolls and moves.

            Args:
                board (BoardState): The current board state.
                depth (int): The depth of recursion (how many moves ahead to consider).
                is_maximizing_player (bool): Flag indicating whether the current player is the maximizing player.

            Returns:
                float: The evaluated score for the current board state.
                    - A higher score is better for the maximizing player, and a lower score is better for the minimizing player.
                    - The score is adjusted based on dice probabilities.
            """
        print(f"Entering minimax: Depth={depth}, Maximizing Player={is_maximizing_player}")
        if depth == 0:
            return self.evaluate_board(board,colour=colour) # Needs to asses board here, add a function
        
        all_combinations = self.generate_dice_rolls()
        
        for (d1, d2), prob in all_combinations:
            possible_boards = self.generate_boards(board,colour.other() if is_maximizing_player else colour, dice_rolls=[d1,d2])
            print(f"Dice: {d1}, {d2}, Prob: {prob}")
            print(f"Possible boards: {possible_boards}")

        if is_maximizing_player:
            best_score = float('-inf')
            for b, moves in possible_boards.items():
                score_for_board_state = self.minimax(b,colour=colour, depth=depth - 1, is_maximizing_player=not is_maximizing_player)
                score_for_board_state *= prob
                print(f"Is Max: {is_maximizing_player}, Dice: ({d1}, {d2}), Prob: {prob}")
                print(f"best score: {best_score}, score_for_board_state: {score_for_board_state}")
                best_score = max(best_score, score_for_board_state)
                print(f"best score: {best_score}")
        
        else:
            best_score = float('inf')
            for b, moves in possible_boards.items():
                score_for_board_state = self.minimax(b,colour=colour, depth=depth - 1, is_maximizing_player=not is_maximizing_player)
                score_for_board_state *= prob
                print(f"Is Min: {is_maximizing_player}, Dice: ({d1}, {d2}), Prob: {prob}")
                print(f"best score: {best_score}, score_for_board_state: {score_for_board_state}")
                best_score = min(best_score, score_for_board_state)
                print(f"best score: {best_score}")

        return best_score
    
    def assess_board(self, colour, myboard):
        pieces = myboard.get_pieces(colour)  # Get the pieces for the given color
        sum_distances = 0
        number_of_singles = 0
        number_occupied_spaces = 0
        sum_distances_to_endzone = 0
        opponents_taken_pieces = len(myboard.get_taken_pieces(colour.other()))  # Count the opponent's taken pieces

        # Calculate the sum of distances and other statistics for the player's pieces
        for piece in pieces:
            distance_to_home = piece.spaces_to_home()
            sum_distances += distance_to_home
            if distance_to_home > 6:
                sum_distances_to_endzone += distance_to_home - 6  # Calculate distance beyond the end zone
            if distance_to_home <= 6:  # Pieces that are "safe" or close to home
                number_of_singles += 1  # If the piece is alone

        # Count occupied spaces on the board
        for location in range(1, 25):
            pieces_at_location = myboard.pieces_at(location)
            if len(pieces_at_location) > 0 and pieces_at_location[0].colour == colour:
                if len(pieces_at_location) == 1:
                    number_of_singles += 1  # Add to the singles count
                elif len(pieces_at_location) > 1:
                    number_occupied_spaces += 1  # Count the space as occupied

        # Return a dictionary with the values needed for evaluation
        return {
            'sum_distances': sum_distances,
            'number_of_singles': number_of_singles,
            'number_occupied_spaces': number_occupied_spaces,
            'opponents_taken_pieces': opponents_taken_pieces,
        }


    def evaluate_board(self, myboard, colour):
        board_stats = self.assess_board(colour, myboard)

        board_value = board_stats['sum_distances'] + 2 * board_stats['number_of_singles'] - \
                      board_stats['number_occupied_spaces'] - board_stats['opponents_taken_pieces']
        return board_value




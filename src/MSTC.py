from src.strategies import Strategy
from src.piece import Piece
from src.colour import Colour
from src.board import Board
import time
import threading
from collections import defaultdict
import numpy as np

global_time_limit = None


class MonteCarloTreeSearchNode(Strategy):
    def __init__(self, state, parent=None, parent_action=None):
        self.state = state # Represent the current Board
        self.parent = parent # None for the root
        self.parent_action = parent_action
        self.children = [] # Data structure might need to change, hold all possible moves 
        self._number_of_visits = 0 # Number of times we visited a node
        self._results = defaultdict(int) # Holds the result from each traverse 
        self._results[1] = 0 # Number of wins
        self._results[-1] = 0 # Number of losses
        self._untried_actions = None #
        self._untried_actions = self.untried_actions() # list of moves we haven't explored yet


    @staticmethod
    def get_difficulty():
        return "MSTC"


    def move(self, board, colour, dice_rolls, make_move, opponents_activity): # main function
        if board.has_game_ended():
            return
        global_time_limit = board.getTheTimeLim()
        start_time = time.time()

        root = MonteCarloTreeSearchNode(state=board)
        selected_node = root.best_action()
        
        for move in optimal_move: # Callback for handle_move
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
        # player_pieces.sort(key=Piece.spaces_to_home, reverse=True) # Sorts them by their distance to home. maybe we don't need it

        # die_roll = dice_rolls[0]
        # remaining_die_roll = dice_rolls[1:]

        resulting_boards = {} # Dictionary to store boards and their corresponding moves
        # Consider both orders of dice rolls
        #print(set(permutations(dice_rolls)))
        for dice_order in (set(permutations(dice_rolls))):
            die_roll = dice_order[0]
            remaining_die_roll = dice_order[1:]

            #valid_move_found = False  # Flag to track if any valid move is found for this die roll

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

            # If no valid moves were found for the remaining die rolls, add the board with the current die roll move
            # if not valid_move_found and len(remaining_die_roll) == 0:
            #     # Add the board after the current move (even if no further moves are possible)
            #     resulting_boards[board] = [{'piece_at': piece.location, 'die_roll': die_roll}]

        return resulting_boards
            

    def untried_actions(self):
        self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions
    

    def n(self):
        return self._number_of_visits
    

    def expand(self):
        action = self._untried_actions.pop()
        next_state = self.state.move(action)
        child_node = MonteCarloTreeSearchNode(next_state, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node 
        
        
    def is_terminal_node(self):
        return self.state.has_game_ended()


    def rollout(self):
        current_rollout_state = self.state
        while not current_rollout_state.has_game_ended():
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.move(action)
        return current_rollout_state.game_result()


    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)


    def is_fully_expanded(self):
        return len(self._untried_actions) == 0


    def best_child(self, c_param=0.1):
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]


    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]


    def _tree_policy(self):
        current_node = self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node
    

    def best_action(self):
        simulation_no = 100
        for i in range(simulation_no):
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        return self.best_child(c_param=0.)
    

    def game_result(self):
        '''
        Modify according to your game or 
        needs. Returns 1 or 0 or -1 depending
        on your state corresponding to win,
        tie or a loss.
        '''
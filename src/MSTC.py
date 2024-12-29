from itertools import permutations
from random import randint, shuffle
from src.strategies import Strategy
from src.piece import Piece
from src.colour import Colour
from src.board import Board
import time
import threading
from collections import defaultdict
import numpy as np

global_time_limit = None
start_time = time.time()


class MonteCarloTreeSearchNode(Strategy):

    def __init__(self, state, colour, dice_rolls, parent=None, parent_action=None):
        self.state = state # Represent the current Board
        self.parent = parent # None for the root
        self.parent_action = parent_action
        self.children = [] # Data structure might need to change, hold all possible moves 
        self._number_of_visits = 0 # Number of times we visited a node
        self.wins_losses = 0
        self._untried_actions = self.generate_boards(state, colour, dice_rolls) # list of moves we haven't explored yet
        self.colour = colour



    @staticmethod
    def get_difficulty():
        return "MSTC"


    def move(self, board, colour, dice_rolls, make_move, opponents_activity): # main function
        if board.has_game_ended():
            return
        global_time_limit = board.getTheTimeLim() - 0.5

        root = MonteCarloTreeSearchNode(state=board, colour=colour, dice_rolls=dice_rolls)
        if len(self._untried_actions) == 0:
            print("Didn't generate any boards.\n")

        selected_node = root.best_action()

        
        for move in selected_node.parent_action: # Callback for handle_move
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
            

    def untried_actions(self,):
        return self._untried_actions
    

    def n(self):
        return self._number_of_visits
        
        
    def is_terminal_node(self):
        return self.state.has_game_ended()


    def rollout(self):
        current_rollout_state = self.state.create_copy() # Board according to the move we decided to do, might need to copy it.
        colour = self.colour
        while not current_rollout_state.has_game_ended(): # or time ended
            dice_roll = [randint(1, 6), randint(1, 6)]
            if dice_roll[0] == dice_roll[1]:
                dice_roll = [dice_roll[0]] * 4

            for die_roll in dice_roll:
                valid_pieces = current_rollout_state.get_pieces(colour)
                shuffle(valid_pieces) # makes the random action
                for piece in valid_pieces:
                    if current_rollout_state.is_move_possible(piece, die_roll):
                        current_rollout_state.move_piece(piece.location, die_roll)
                        break
            colour = Colour.other()

        return current_rollout_state.game_result(current_rollout_state)


    def backpropagate(self, result):
        self._number_of_visits += 1.
        self.wins_losses += result
        if self.parent:
            self.parent.backpropagate(result)


    def is_fully_expanded(self):
        return len(self._untried_actions) == 0
    

    def expand(self):
        next_state, action = next(iter(self._untried_actions.items()))
        print(f"move that led to next state is {action}") 
        del(self._untried_actions[next_state]) # Delete the key-value pair of the untried_actions field
        child_node = MonteCarloTreeSearchNode(next_state, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node 

        
    def best_child(self, c_param=0.1): #UCB, need to multiply -1 if its the opponent's turn
        choices_weights = [(c.wins_losses / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
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
        simulation_no = 0
        elapsed_time = time.time() - start_time
        # Might need to insert here time limit check
        while elapsed_time > 0 or simulation_no != 100:
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
            simulation_no +=1
        return self.best_child(c_param=0.)
    

    def game_result(self, current_rollout_state):
        '''
        Returns score depending
        on your state corresponding to win, a loss or mars.
        '''
        # Check for mars
        if len(current_rollout_state.get_pieces(self.colour) == 0 and current_rollout_state.get_pieces(self.colour.other) == 15):
            return 2
        elif len(current_rollout_state.get_pieces(self.colour) == 15 and current_rollout_state.get_pieces(self.colour.other) == 0):
            return -2
        # Regular win
        return 1 if len(current_rollout_state.get_pieces(self.colour)) == 0 else -1

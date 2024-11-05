import random
from random import randint
from src.colour import Colour
from src.game import Game
from src.strategies import HumanStrategy

def print_tournament_placement(player_names):
    print("Tournament Placement:")
    random.shuffle(player_names)
    for i in range(0, len(player_names), 2):
        if i + 1 < len(player_names):
            print(f"{player_names[i]} vs {player_names[i + 1]}")
        else:
            print(f"{player_names[i]} gets a bye")

def print_tournament_branch(tournament_branch):
    print("\nTournament Branch:")
    for round_num, matchups in enumerate(tournament_branch, start=1):
        print(f"Round {round_num}:")
        for matchup in matchups:
            print(f"  {matchup}")

def run_tournament(player_names):
    players = {name: HumanStrategy(name) for name in player_names}
    print_tournament_placement(player_names)
    game_results = []
    tournament_branch = []
    while len(players) > 1:
        next_round_players = {}
        player_names = list(players.keys())
        random.shuffle(player_names)
        round_matchups = []
        for i in range(0, len(player_names), 2):
            if i + 1 >= len(player_names):
                next_round_players[player_names[i]] = players[player_names[i]]
                continue
            player1 = player_names[i]
            player2 = player_names[i + 1]
            round_matchups.append(f"{player1} vs {player2}")
            print(f"Starting game: {player1} vs {player2}")  
            colour1 = Colour(randint(0, 1))
            colour2 = colour1.other()
            first_player = Colour(randint(0, 1))
            game = Game(
                white_strategy=players[player1] if colour1 == Colour.WHITE else players[player2],
                black_strategy=players[player1] if colour1 == Colour.BLACK else players[player2],
                first_player=first_player
            )
            game.run_game(verbose=False)
            winner = game.who_won()
            winner_name = player1 if winner == colour1 else player2
            next_round_players[winner_name] = players[winner_name]
            game_results.append(f"{player1} vs {player2}: {winner_name} won")
            print(f"{winner_name} won the match!")
        tournament_branch.append(round_matchups)
        players = next_round_players
    final_winner = list(players.keys())[0]
    print(f"{final_winner} is the tournament champion!")
    print("\nTournament Results:")
    for result in game_results:
        print(result)
    print_tournament_branch(tournament_branch)

if __name__ == '__main__':
    num_players = int(input("Enter the number of players: "))
    player_names = [input(f"Name of player {i + 1}: ") for i in range(num_players)]
    run_tournament(player_names)

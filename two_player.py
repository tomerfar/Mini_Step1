from random import randint
from src.MLplayer import MLPlayer
from src.MiniMaxi import MiniMax
from src.colour import Colour
from src.game import Game
from src.strategies import HumanStrategy


if __name__ == '__main__':
    players = {
        Colour.WHITE: "ML Player",
        Colour.BLACK: "Heuristic",
    }

    
    time_limit = input("Enter time limit in seconds (or 'inf' for no limit): ")
    if time_limit.lower() == 'inf':
        time_limit = -1
    else:
        time_limit = int(time_limit)

    number = 100
    for brains in range(10):
        wins = {players[Colour.WHITE]: 0, players[Colour.BLACK]: 0}
        print(f"Series: ML{number} vs Heuristic")
        for _ in range(10):
            game = Game(
                white_strategy=MLPlayer(f"brain_checkpoint_{number}.pt"),
                black_strategy=MiniMax(),
                first_player=Colour(randint(0, 1)),
                time_limit=time_limit
            )

            game.run_game(verbose=False)
            winner = game.who_won()
            winner_name = players[winner]
            wins[winner_name] += 1

            print("%s won!" % winner_name)

        print(f"{players[Colour.WHITE]}: {wins[players[Colour.WHITE]]} wins")
        print(f"{players[Colour.BLACK]}: {wins[players[Colour.BLACK]]} wins")
        number += 100
        print("End of Series!\n") 
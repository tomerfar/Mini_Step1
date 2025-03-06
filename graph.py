import pandas as pd
import matplotlib.pyplot as plt
from random import randint
from src.MLplayer import MLPlayer
from src.MiniMaxi import MiniMax
from src.colour import Colour
from src.game import Game
from src.strategies import TrainingPhase2
from src.strategies import MoveFurthestBackStrategy 
from src.compare_all_moves_strategy import CompareAllMoves

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

    num_games_per_series = 10  # Run 10 games per iteration
    num_iterations = 10  # Run 10 iterations (100.pt to 1000.pt)
    mlplayer_wins_list = []  # Store MLPlayer wins per iteration
    brain_checkpoints = list(range(1000, 20001, 1000))  # 100, 200, ..., 1000

    for brain_number in brain_checkpoints:
        wins = {players[Colour.WHITE]: 0, players[Colour.BLACK]: 0}
        print(f"Running series with MLPlayer brain: compwithsigmoid_{brain_number}.pt")

        for _ in range(num_games_per_series):
            game = Game(
                white_strategy=MLPlayer(f"compwithsigmoid_{brain_number}"),
                black_strategy=CompareAllMoves(True),
                first_player=Colour(randint(0, 1)),
                time_limit=time_limit
            )

            game.run_game(verbose=False)
            winner = game.who_won()
            winner_name = players[winner]
            wins[winner_name] += 1

            print(f"{winner_name} won!")

        # Store how many times MLPlayer won
        mlplayer_wins = wins[players[Colour.WHITE]]
        mlplayer_wins_list.append(mlplayer_wins)

        print(f"{players[Colour.WHITE]}: {mlplayer_wins} wins")
        print(f"{players[Colour.BLACK]}: {wins[players[Colour.BLACK]]} wins")
        print("End of Series!\n")

    # Convert results to DataFrame
    df = pd.DataFrame({
        'Brain Checkpoint': brain_checkpoints,
        'MLPlayer Wins': mlplayer_wins_list
    })

    # Save results to Excel
    excel_filename = "mlplayer_wins.xlsx"
    df.to_excel(excel_filename, index=False)

    # Generate a graph
    plt.figure(figsize=(8, 5))
    plt.plot(df['Brain Checkpoint'], df['MLPlayer Wins'], marker='o', linestyle='-')
    plt.xlabel("Brain Checkpoint (MLPlayer)")
    plt.ylabel("MLPlayer Wins (out of 10 games)")
    plt.title("MLPlayer Wins vs. Brain Checkpoint")
    plt.ylim(0, 10)  # Since max possible wins per series is 10
    plt.grid()
    plt.savefig("mlplayer_wins_graph.png")  # Save graph as image
    plt.show()

    print(f"Data saved to {excel_filename} and graph saved as mlplayer_wins_graph.png")

import pandas as pd
import matplotlib.pyplot as plt
from random import randint
from src.MLplayer import MLPlayer
from src.MiniMaxi import MiniMax
from src.colour import Colour
from src.game import Game

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
    win_differences = []  # Store the average win difference per iteration
    brain_checkpoints = list(range(100, 1100, 100))  # 100, 200, ..., 1000

    for brain_number in brain_checkpoints:
        wins = {players[Colour.WHITE]: 0, players[Colour.BLACK]: 0}
        print(f"Running series with MLPlayer brain: brain_checkpoint_{brain_number}.pt")

        for _ in range(num_games_per_series):
            game = Game(
                white_strategy=MLPlayer(f"brain_checkpoint_{brain_number}.pt"),
                black_strategy=MiniMax(),
                first_player=Colour(randint(0, 1)),
                time_limit=time_limit
            )

            game.run_game(verbose=False)
            winner = game.who_won()
            winner_name = players[winner]
            wins[winner_name] += 1

            print(f"{winner_name} won!")

        # Compute the average win difference
        diff = abs(wins[players[Colour.WHITE]] - wins[players[Colour.BLACK]]) / num_games_per_series
        win_differences.append(diff)

        print(f"{players[Colour.WHITE]}: {wins[players[Colour.WHITE]]} wins")
        print(f"{players[Colour.BLACK]}: {wins[players[Colour.BLACK]]} wins")
        print(f"Average Win Difference: {diff:.2f}")
        print("End of Series!\n")

    # Convert results to DataFrame
    df = pd.DataFrame({
        'Brain Checkpoint': brain_checkpoints,
        'Avg Win Difference': win_differences
    })

    # Save results to Excel
    excel_filename = "average_win_differences.xlsx"
    df.to_excel(excel_filename, index=False)

    # Generate a graph
    plt.figure(figsize=(8, 5))
    plt.plot(df['Brain Checkpoint'], df['Avg Win Difference'], marker='o', linestyle='-')
    plt.xlabel("Brain Checkpoint (MLPlayer)")
    plt.ylabel("Average Win Difference")
    plt.title("Average Win Difference vs. Brain Checkpoint")
    plt.grid()
    plt.savefig("average_win_differences_graph.png")  # Save graph as image
    plt.show()

    print(f"Data saved to {excel_filename} and graph saved as average_win_differences_graph.png")

from src.Training import Training
from src.colour import Colour
from src.game import Game
from src.strategy_factory import StrategyFactory
from src.strategies import HumanStrategy

# Script for running and training the neural network
def main():
    total_iterations = 10000
    save_interval = 1000  # Save every 1000 iterations
    save_checkpoints = list(range(save_interval, total_iterations + 1, save_interval))
    save_names = [f"checkpoint1000{i}" for i in save_checkpoints]

    # Initialize Training instance with the brain
    training_instance = Training("brain_checkpoint_1000.pt")

    print(f"Starting training for {total_iterations} iterations...")

    # The train function handles its own iterations and saving
    training_instance.train(iterations=save_checkpoints, names=save_names)

    # Save final trained model
    print("Training complete. Saving final model...")
    training_instance.brain.save_brain("master_brain10000")

if __name__ == "__main__":
    main()
from src.Training import Training
from src.colour import Colour
from src.game import Game
from src.strategy_factory import StrategyFactory
from src.strategies import HumanStrategy

# Script for running and training the neural network
def main():
    total_iterations = 2000
    save_checkpoints = [5000, 6000]
    save_names = [f"checkpoint{i}" for i in save_checkpoints]

    # Initialize Training instance with the brain
    training_instance = Training("checkpoint4000")

    print(f"Starting training for {total_iterations} iterations...")

    # The train function handles its own iterations and saving
    training_instance.train(iterations=save_checkpoints, names=save_names)

    # Save final trained model
    print("Training complete. Saving final model...")
    training_instance.brain.save_brain("master_brain6000")

if __name__ == "__main__":
    main()
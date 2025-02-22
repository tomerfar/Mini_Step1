from src.Training import Training
from src.colour import Colour
from src.game import Game
from src.strategy_factory import StrategyFactory
from src.strategies import HumanStrategy

def main():
    # total_iterations = 1000
    # save_interval = 100  # Save every 100 iterations
    # save_checkpoints = list(range(save_interval, total_iterations + 1, save_interval))
    # save_names = [f"brain_checkpoint_{i}" for i in save_checkpoints]

    # # Initialize Training instance with the brain
    # training_instance = Training("brain_20")

    # print(f"Starting training for {total_iterations} iterations...")

    # # The train function handles its own iterations and saving
    # training_instance.train(iterations=save_checkpoints, names=save_names)

    # # Save final trained model
    # print("Training complete. Saving final model...")
    # training_instance.brain.save_brain("brain_final.pt")


    # # Define the number of training iterations and checkpoints
    # iteration_checkpoints = [1000]  # Save the model at these iteration milestones
    # brain_save_names = ["brain_30"]  # File names for saved models

    # # Create an instance of the Training class
    training_instance = Training()
    # training_instance = Training("brain_20")
    # # Train the neural network
    # print("Starting training...")
    # training_instance.train(iterations=iteration_checkpoints, names=brain_save_names)
    # print("Training complete.")

if __name__ == "__main__":
    main()

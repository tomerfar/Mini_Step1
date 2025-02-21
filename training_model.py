from src.Training import Training
from src.colour import Colour
from src.game import Game
from src.strategy_factory import StrategyFactory
from src.strategies import HumanStrategy

def main():
    # Define the number of training iterations and checkpoints
    iteration_checkpoints = [100, 200, 300, 400]  # Save the model at these iteration milestones
    brain_save_names = ["brain_100", "brain_200", "brain_300", "brain_400"]  # File names for saved models

    # Create an instance of the Training class
    training_instance = Training()
    # for _ in range (10):
    #training_instance.initialize_neural_network()

    # Train the neural network
    # print("Starting training...")
    # training_instance.train(iterations=iteration_checkpoints, names=brain_save_names)
    # print("Training complete.")

if __name__ == "__main__":
    main()

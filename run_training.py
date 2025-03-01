from src.Training import Training

if __name__ == "__main__":
    trainer = Training("brain_iteration_1000")  # Initialize the training class
    trainer.initialize_neural_network()  # Start training with 1000 iterations

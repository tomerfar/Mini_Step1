from src.compare_all_moves_strategy import CompareAllMovesSimple
from src.strategies import MoveFurthestBackStrategy, HumanStrategy, MoveRandomPiece, MoveRandomTraining
from src.MiniMaxi import MiniMax
from src.MSTC import MonteCarloTreeSearchNode
from src.MLplayer import MLPlayer



class StrategyFactory:
    @staticmethod
    def create_by_name(strategy_name):
        for strategy in StrategyFactory.get_all():
            if strategy.__name__ == strategy_name:
                if strategy_name == "MonteCarloTreeSearchNode":
                    return MonteCarloTreeSearchNode(state=None, colour=None,dice_rolls=None)
                
                return strategy()

        raise Exception("Cannot find strategy %s" % strategy_name)

    @staticmethod
    def get_all():
        strategies = [
            MoveRandomPiece,
            MoveFurthestBackStrategy,
            CompareAllMovesSimple,
            HumanStrategy,
            MiniMax,
            MonteCarloTreeSearchNode,
            MLPlayer,
            MoveRandomTraining
        ]
        return strategies

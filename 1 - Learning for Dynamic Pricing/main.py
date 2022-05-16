from typing import List

from BanditLearner import step3
from GreedyLearner import GreedyLearner
from Learner import Learner
from TSLearner import TSLearner
from UCBLearner import UCBLearner
from GaussianThompsonLearner import GaussianTSLearner
from parameters import environment

if __name__ == '__main__':

    learners: List[Learner] = [
        GreedyLearner(),
        UCBLearner(step3),
        # TSLearner(step3)
        GaussianTSLearner(step3)
    ]
    for learner in learners:
        environment.reset_day()
        learner.run_experiment(50, log=False)

# TODO: Tune down the model and debug whatever is happening with the bandit algorithms

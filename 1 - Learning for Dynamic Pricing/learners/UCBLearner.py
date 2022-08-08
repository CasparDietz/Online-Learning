from typing import List

import numpy as np

from BanditLearner import BanditLearner, BanditConfiguration
from entities import Product


class UCBLearner(BanditLearner):
    def _reset_parameters(self):
        self.means = [[0 for _ in product.candidate_prices] for product in self._products]
        self.widths = [[np.inf for _ in product.candidate_prices] for product in self._products]
        self.rewards_per_arm_per_product = [[[] for _ in product.candidate_prices] for product in self._products]

    def _select_price_criteria(self, product: Product) -> List[float]:
        return np.array(self.means[product.id]) + np.array(self.widths[product.id])

    def __init__(self, config: BanditConfiguration):
        super().__init__(config)

    def _update_learner_state(self, selected_price_indexes, product_rewards, t):
        for product_id, product_reward in enumerate(product_rewards):
            pulled_arm = selected_price_indexes[product_id]

            self.rewards_per_arm_per_product[product_id][pulled_arm].append(product_reward)
            self.means[product_id][pulled_arm] = np.mean(
                self.rewards_per_arm_per_product[product_id][pulled_arm])
            n = len(self.rewards_per_arm_per_product[product_id][pulled_arm])
            if n > 0:
                self.widths[product_id][pulled_arm] = np.sqrt(2 * np.log(t + 1) / n)
            else:
                self.widths[product_id][pulled_arm] = np.inf

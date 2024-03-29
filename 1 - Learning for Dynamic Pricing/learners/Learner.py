from typing import List, Tuple, Optional, NamedTuple, Dict

import scipy.ndimage
from matplotlib import pyplot as plt

from entities import Environment, Product, SimulationConfig, Customer
from tqdm import tqdm
import numpy as np

from parameter_estimators import ParameterHistoryEntry

ShallContinue = bool
Reward = float
PriceIndexes = List[int]
ProductRewards = List[float]
ChangeDetected = bool
ChangeDetectorParams = Optional[Tuple]
ClairvoyantReward = float


def draw_reward_graph(rewards: List[Reward], name: str):
    # Plot the current_reward over iterations
    x_iteration = list(range(1, len(rewards) + 1))
    # Plot the standard deviation over iterations
    for i in range(1, len(x_iteration)):
        sd_reward = np.std(rewards, axis=0) / np.sqrt(i)
        plt.plot(i, scipy.ndimage.uniform_filter1d(rewards, size=10) + sd_reward)
        plt.plot(i, scipy.ndimage.uniform_filter1d(rewards, size=10) - sd_reward)

    plt.plot(x_iteration, scipy.ndimage.uniform_filter1d(rewards, size=10))

    plt.xlabel("Iteration")
    plt.ylabel("Reward")
    plt.title(f"{name} Reward")
    plt.show()


def draw_selection_index_graph(products: List[Product], selected_price_indexes: List[PriceIndexes], name: str):
    # Plot the prices p1, p2, p3, p4 and p5 over the iterations
    x_iteration = list(range(1, len(selected_price_indexes) + 1))
    for product in products:
        prices = []
        for selected_price_index in selected_price_indexes:
            prices.append(product.candidate_prices[selected_price_index[product.id]])

        plt.plot(x_iteration, prices, label=product.name)
    plt.xlabel("Iteration")
    plt.ylabel("Prices per product")
    plt.title(f"{name} Prices")
    plt.legend()
    plt.show()


def draw_product_reward_graph(products: List[Product], product_rewards: List[ProductRewards], name: str):
    x_iteration = list(range(1, len(product_rewards) + 1))
    fig, axs = plt.subplots(5, sharex=True, sharey=True)

    axs[0].set_title(f"{name} Product rewards")
    for product in products:
        axs[product.id].plot(x_iteration, [product_reward[product.id] for product_reward in product_rewards],
                             label=product.name)
        axs[product.id].legend(loc="upper right")
    plt.ylabel("Product rewards")
    plt.xlabel("Iteration")
    plt.show()


class ExperimentHistoryItem(NamedTuple):
    reward: Reward
    selected_price_indexes: PriceIndexes
    product_rewards: ProductRewards
    change_detected: ChangeDetected
    change_detector_params: ChangeDetectorParams
    clairvoyant_reward: ClairvoyantReward
    customers: Optional[List["Customer"]]  # For some reason typing resolves the module, not the class
    estimators: Optional[Dict[str, ParameterHistoryEntry]]
    upper_bound: float


class Learner:
    name: str
    _products: List[Product]
    _environment: Environment
    _config: SimulationConfig
    absolute_clairvoyant: Optional[float] = None
    clairvoyant_indexes: Optional[List[int]] = None
    clairvoyant_product_rewards: Optional[ProductRewards] = None

    def refresh_vars(self, products: List[Product], environment: Environment, config: SimulationConfig):
        self._products = products
        self._environment = environment
        self._config = config
        self.absolute_clairvoyant = None
        self.clairvoyant_indexes = None
        self.clairvoyant_product_rewards = None

    def _upper_bound(self):
        raise NotImplementedError()

    def __init__(self):
        ## This mechanism is ugly, but let's keep it now :(
        if not hasattr(self, "_products"):
            self._products = []
        self._experiment_history: List[ExperimentHistoryItem] = []

    def reset(self):
        raise NotImplementedError()

    def iterate_once(self) -> ShallContinue:
        raise NotImplementedError()

    def update_experiment_days(self, days: int):
        raise NotImplementedError()

    def run_experiment(self, max_days: int, *, plot_graphs: bool = True, current_n: Optional[int] = None) -> None:
        ## TODO: This is a very bad way, we want more presentable results :)
        running = True
        self.update_experiment_days(max_days)
        with tqdm(total=max_days, leave=False) as pbar:
            pbar.set_description(
                f"Running {self.name}{' for experiment ' + str(current_n) if current_n is not None else ''}")
            while running and len(self._experiment_history) < max_days:
                running = self.iterate_once()
                pbar.update(1)

        if plot_graphs:
            rewards = [reward for reward, _, _, _, _ in self._experiment_history]
            draw_reward_graph(rewards, self.name)

            selected_prices = [prices for _, prices, _, _, _ in self._experiment_history]
            draw_selection_index_graph(self._products, selected_prices, self.name)

            product_rewards = [product_reward for _, _, product_reward, _, _ in self._experiment_history]
            draw_product_reward_graph(self._products, product_rewards, self.name)

    def _clairvoyant_reward_calculate(self, price_indexes) -> float:
        raise NotImplementedError()

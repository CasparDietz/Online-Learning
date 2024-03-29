from typing import List, NamedTuple

from entities import Customer


class ChangeHistoryItem(NamedTuple):
    g_plus: float
    g_minus: float
    sample: float


class ChangeDetectionAlgorithm:
    def has_changed(self) -> bool:
        # This approach works as only one detection for all cases
        # It is not arm specific
        raise NotImplementedError()

    def update(self, last_customers: List["Customer"]) -> NamedTuple:
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()


class CumSum(ChangeDetectionAlgorithm):
    def __init__(self, collect_for_days, drift, threshold):
        self.collect_for = collect_for_days
        self.drift = drift
        self.threshold = threshold
        self.reset()

    def _calculate_sample(self, last_customers: List["Customer"]) -> float:
        total_visits = 0
        total_purchases = 0
        for customer in last_customers:
            total_visits += len(customer.products_clicked)
            total_purchases += sum(1 if value[0] > 0 else 0 for value in customer.products_bought.values())

        sample = total_purchases / total_visits

        return sample

    def update(self, last_customers: List["Customer"]) -> ChangeHistoryItem:

        sample = self._calculate_sample(last_customers)
        history_item = ChangeHistoryItem(0, 0, sample)
        if self.t < self.collect_for:
            self.samples[-1] += sample / self.collect_for
            self.alerts.append(False)
        else:
            s = sample - self.samples[-1]
            g_plus = max(self.g_pluses[-1] + s - self.drift, 0)
            g_minus = max(self.g_minuses[-1] - s - self.drift, 0)
            alert = g_plus > self.threshold or g_minus > self.threshold
            if alert:
                g_plus = 0
                g_minus = 0
            self.samples.append(sample)
            self.g_pluses.append(g_plus)
            self.g_minuses.append(g_minus)
            self.alerts.append(alert)
            history_item = ChangeHistoryItem(g_plus, g_minus, sample)
        self.t += 1
        return history_item

    def has_changed(self) -> bool:
        has_changed = self.alerts[-1]
        return has_changed

    def reset(self):
        self.t = 0
        self.g_pluses = [0.0]
        self.g_minuses = [0.0]
        self.alerts = []
        self.samples = [0.0]

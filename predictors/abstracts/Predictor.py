from abc import ABC, abstractmethod
import pandas as pd


class Predictor(ABC):
    def __init__(self, **kwargs):
        self.model = None
        self.params = kwargs

    @abstractmethod
    def build_model(self):
        pass

    @abstractmethod
    def train(self, x_train: pd.DataFrame, y_train: pd.DataFrame):
        pass

    @abstractmethod
    def evaluate(self, x_test: pd.DataFrame, y_test: pd.DataFrame, save_model: bool = True) -> dict:
        pass

    @abstractmethod
    def predict(self, x: pd.DataFrame):
        pass

    @abstractmethod
    def save_model(self, filename: str):
        pass

    @abstractmethod
    def load_model(self, filename: str):
        pass

    @abstractmethod
    def fine_tune(self, x: pd.DataFrame, y: pd.DataFrame, epochs: int = 5, save_fine_tuned=False):
        pass
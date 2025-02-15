from abc import ABC, abstractmethod
from typing import Union, Tuple
import numpy as np


class Match(ABC):
    @abstractmethod
    def match(self, image: Union[str, np.ndarray], template: Union[str, np.ndarray], threshold: float) -> bool:
        pass

    @abstractmethod
    def locate_center(self, image: Union[str, np.ndarray], template: Union[str, np.ndarray]) -> Tuple[int, int]:
        pass

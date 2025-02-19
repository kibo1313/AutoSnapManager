from abc import ABC, abstractmethod
from typing import Union, Tuple, List

import numpy as np


class Match(ABC):
    @abstractmethod
    def match(self, image: Union[str, np.ndarray], template: Union[str, np.ndarray], threshold: float = None) -> bool:
        """匹配模板"""
        pass

    @abstractmethod
    def locate_center(self, image: Union[str, np.ndarray], template: Union[str, np.ndarray],
                      threshold: float = None) -> Tuple[int, int]:
        """定位匹配区域最大相似度的中心坐标"""
        pass

    def locate_center_repeated(self,
                               image: Union[str, np.ndarray], template: Union[str, np.ndarray],
                               min_distance: Tuple[int, int] = (0, 0), threshold: float = None
                               ) -> Tuple[List[int], List[int]]:
        """定位匹配区域中指定阈值内的所有中心坐标"""
        pass

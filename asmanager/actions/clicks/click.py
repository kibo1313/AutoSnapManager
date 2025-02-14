"""点击操作的抽象基类模块"""

from abc import ABC, abstractmethod


class Click(ABC):
    """点击操作抽象基类"""
    
    @abstractmethod
    def click(self, x: int, y: int) -> None:
        """
        在指定坐标执行点击操作
        
        Args:
            x: 点击位置的横坐标
            y: 点击位置的纵坐标
        """

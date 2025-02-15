from abc import ABC, abstractmethod


class Manager(ABC):

    @abstractmethod
    def screenshot(self, save_path: str = None) -> None:
        """截取屏幕截图，可选择保存到指定路径"""
        pass

    @abstractmethod
    def match(self, template_path: str) -> bool:
        """匹配模板是否存在"""
        pass

    @abstractmethod
    def click(self, template_path: str) -> None:
        """点击匹配区域中心位置"""
        pass

    @abstractmethod
    def clickTo(self, x: int, y: int) -> None:
        """点击指定位置"""
        pass

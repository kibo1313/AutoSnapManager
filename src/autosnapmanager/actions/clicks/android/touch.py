from abc import abstractmethod
from autosnapmanager.actions.clicks.click import Click


class Touch(Click):
    @abstractmethod
    def click(self, x: int, y: int, duration: int = None) -> None:
        pass

    @abstractmethod
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        pass

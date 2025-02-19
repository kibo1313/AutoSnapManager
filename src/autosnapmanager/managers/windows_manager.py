from typing import Union, Tuple, Optional, List

import numpy as np

from autosnapmanager.actions.clicks.click import Click
from autosnapmanager.managers.manager import Manager
from autosnapmanager.managers.manager_config import System, ScreenCaps, Matches, Clicks, DefaultArgs
from autosnapmanager.matches.match import Match
from autosnapmanager.screencaps.screencap import ScreenCap
from autosnapmanager.utils.dpi_tools import set_dpi_awareness


class WindowsManager(Manager):
    def __init__(self,
                 window_name: Optional[str] = None,
                 screencap: Optional[Union[str, ScreenCaps, ScreenCap]] = None,
                 match: Optional[Union[str, Matches, Match]] = None,
                 click: Optional[Union[str, Clicks, Click]] = None
                 ):
        """
        初始化 WindowsManager 对象

        Args:
            window_name: 目标窗口名称
            screencap: 截图方法类
            match: 匹配方法类
            click: 点击方法类
        """
        set_dpi_awareness()  # 设置DPI感知

        for key in ['ScreenCap', 'Click']:
            DefaultArgs[System.Windows][key]['window_name'] = window_name

        super().__init__(system=System.Windows, params=DefaultArgs[System.Windows], screencap=screencap, match=match,
                         click=click)

    def screenshot(self, save_path: str = None) -> None:
        """获取屏幕截图"""
        self.screenCaps.save_screencap(save_path)

    def match(self, template: str, threshold: float = None) -> bool:
        """匹配模板"""
        return self.matches.match(self.screenCaps.screencap(), template, threshold)

    def click(self, template: Union[str, tuple], threshold: float = None,
              repeat: bool = False, min_distance: Tuple[int, int] = (1, 1)
              ) -> None:
        """点击匹配位置, 接受图片路径与点击坐标元组"""
        if isinstance(template, str):
            x, y = self._locate_center(template, threshold) \
                if not repeat \
                else self._locate_center_repeated(template, min_distance, threshold)
        else:
            x, y = template

        with self.click_lock:
            if repeat:
                for cx, cy in zip(x, y):
                    self.clicks.click(cx, cy)
            else:
                self.clicks.click(x, y)

    def _locate_center(self, template: Union[str, np.ndarray], threshold: float = None) -> Tuple[int, int]:
        """定位匹配区域最大相似度的中心坐标"""
        return self.matches.locate_center(self.screenCaps.screencap(), template, threshold)

    def _locate_center_repeated(self, template: Union[str, np.ndarray],
                                min_distance: Tuple[int, int] = (0, 0),
                                threshold: float = None
                                ) -> Tuple[List[int], List[int]]:
        """定位匹配区域中指定阈值内的所有中心坐标"""
        return self.matches.locate_center_repeated(self.screenCaps.screencap(), template, min_distance, threshold)


if __name__ == "__main__":
    win = WindowsManager()
    # win.screenshot()

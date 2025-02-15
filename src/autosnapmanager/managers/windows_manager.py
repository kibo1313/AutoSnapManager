from threading import Lock
from typing import Union, Tuple, Any, Optional

import numpy as np
from autosnapmanager.actions.clicks.click import Click
from autosnapmanager.managers.manager import Manager
from autosnapmanager.managers.manager_config import CLASSMAP, DefaultMethods, System, ScreenCaps, Matches, Clicks
from autosnapmanager.matches.match import Match
from autosnapmanager.screencaps.screencap import ScreenCap
from autosnapmanager.utils.dpi_tools import set_dpi_awareness
from autosnapmanager.utils.module_class import get_class_name, check_class_name, get_module_class as module


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
        self.window_name = window_name

        set_dpi_awareness()  # 设置DPI感知

        self.screenCaps = self._init_method(screencap, ScreenCap)
        self.matches = self._init_method(match, Match)
        self.clicks = self._init_method(click, Click)

        self.click_lock = Lock()

    def screenshot(self, save_path: str = None) -> None:
        """获取屏幕截图"""
        self.screenCaps.save_screencap(save_path)

    def match(self, template: str) -> bool:
        """匹配模板"""
        return self.matches.match(self.screenCaps.screencap(), template)

    def _locate_center(self, template: Union[str, np.ndarray]) -> Tuple[int, int]:
        """定位匹配区域的中心坐标"""
        return self.matches.locate_center(self.screenCaps.screencap(), template)

    def click(self, template: str) -> None:
        """点击匹配位置"""
        x, y = self._locate_center(template)

        with self.click_lock:
            self.clicks.click(x, y)

    def clickTo(self, x: int, y: int) -> None:
        """点击指定位置"""
        with self.click_lock:
            self.clicks.click(x, y)

    def _init_method(self, method: Any, super_class) -> Union[ScreenCap, Match, Click]:
        """初始化方法类"""
        if method is None:
            return self._set_default_method(super_class)

        if isinstance(method, super_class):
            return method

        if isinstance(method, str):
            method = module(CLASSMAP[super_class.__name__], method, System.Windows)
            return method(window_name=self.window_name)

        if isinstance(method, type) and issubclass(method, super_class):
            class_name = get_class_name(method)
            super_name = get_class_name(super_class)
            check_class_name(CLASSMAP[super_name], System.Windows, class_name)
            return method(window_name=self.window_name)

        raise TypeError(f"传入的 '{method}' 参数未能解析")

    def _set_default_method(self, super_class) -> Union[ScreenCap, Match, Click]:
        """设置方法默认值"""

        default_methods = DefaultMethods.get(super_class.__name__).get(System.Windows)
        map_table = CLASSMAP[super_class.__name__]

        return module(map_table, default_methods[0], System.Windows)(window_name=self.window_name) \
            if self.window_name else (
            module(map_table, default_methods[1], System.Windows)())

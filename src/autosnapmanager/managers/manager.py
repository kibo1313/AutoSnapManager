from abc import ABC, abstractmethod
from typing import Union, Optional, Any

from autosnapmanager.actions.clicks.click import Click
from autosnapmanager.managers.manager_config import (
    CLASSMAP, DefaultMethods, System, ScreenCaps, Matches, Clicks
)
from autosnapmanager.matches.match import Match
from autosnapmanager.screencaps.screencap import ScreenCap
from autosnapmanager.utils.module_class import get_class_name, check_class_name, get_module_class as module


class Manager(ABC):
    def __init__(self,
                 system: System,
                 params: dict,
                 screencap: Optional[Union[str, ScreenCaps, ScreenCap]] = None,
                 match: Optional[Union[str, Matches, Match]] = None,
                 click: Optional[Union[str, Clicks, Click]] = None
                 ):
        """
        :param system: 系统类型
        :param params: 系统指定参数，如 window_name, serial
        :param screencap: 截图方法
        :param match: 匹配方法
        :param click: 点击方法
        """
        self.screenCaps = self._init_method(system, params, screencap, ScreenCap)
        self.matches = self._init_method(system, params, match, Match)
        self.clicks = self._init_method(system, params, click, Click)

    @abstractmethod
    def screenshot(self, save_path: str = None) -> None:
        """截取屏幕截图，可选择保存到指定路径"""
        pass

    @abstractmethod
    def match(self, template_path: str, threshold: float = None) -> bool:
        """匹配模板是否存在"""
        pass

    @abstractmethod
    def click(self, template: Union[str, tuple], threshold: float = None) -> None:
        """点击匹配位置(可选图片路径或元组坐标)"""
        pass

    def _init_method(self, system: System, params: dict, method: Any, super_class) -> Union[ScreenCap, Match, Click]:
        """初始化方法类"""
        if method is None:
            return self._set_default_method(system, params, super_class)

        if isinstance(method, super_class):
            return method

        if isinstance(method, str):
            method = module(CLASSMAP[super_class.__name__], method, system)
            return method(**params[super_class.__name__])

        if isinstance(method, type) and issubclass(method, super_class):
            class_name = get_class_name(method)
            super_name = get_class_name(super_class)
            check_class_name(CLASSMAP[super_name], system, class_name)
            return method(**params[super_class.__name__])

        raise TypeError(f"传入的 '{method}' 参数未能解析")

    @staticmethod
    def _set_default_method(system: System, params: dict, super_class) -> Union[ScreenCap, Match, Click]:
        """设置方法默认值"""
        default_methods = DefaultMethods.get(super_class.__name__).get(system)
        map_obj = CLASSMAP[super_class.__name__]
        param = params.get(super_class.__name__)

        if system == System.Windows and super_class in (ScreenCap, Click):
            if list(param.values())[0] is None:
                return module(map_obj, default_methods[1], system)()
        else:
            return module(map_obj, default_methods[0], system)(**param)

from typing import TypeVar, Union, Type, Optional, Dict, Generic

from autosnapmanager.actions.clicks.click import Click
from autosnapmanager.managers.manager import Manager
from autosnapmanager.managers.manager_config import System, MANAGER, PARAMS_MAP
from autosnapmanager.matches.match import Match
from autosnapmanager.screencaps.screencap import ScreenCap
from autosnapmanager.utils.module_class import get_module_class

# 定义类型变量，限制为 Manager 的子类
T = TypeVar("T", bound=Manager)


class ASM(Generic[T]):
    def __init__(self, system: System):
        self.system = system

    def __getattr__(self, name):
        if name == "manager":
            ManagerClass = get_module_class(MANAGER, self.system)
            return ManagerClass

    def create(self,
               screencap: Optional[Union[str, ScreenCap, Type[ScreenCap]]] = None,
               match: Optional[Union[str, Match, Type[Match]]] = None,
               click: Optional[Union[str, Click, Type[Click]]] = None,
               # 系统专用参数
               window_name: Optional[str] = None,
               serial: Optional[str] = None
               ) -> T:
        system_params = self._get_system_params(
            window_name=window_name,
            serial=serial
        )

        ManagerClass = get_module_class(MANAGER, self.system)

        return ManagerClass(
            screencap=screencap,
            match=match,
            click=click,
            **system_params,
        )

    def _get_system_params(self, **kwargs) -> Dict:
        return {k: v for k, v in kwargs.items()
                if k in PARAMS_MAP.get(self.system, [])}


if __name__ == '__main__':
    m = ASM(system=System.Windows)
    # m.screenshot()
    # for x, y in m.matches.locate_center_repeated(m.screenCaps.screencap(), r"C:\Users\YXS\Downloads\tmpAF47.png"):
    #     m.clickTo(x, y)
    # m.screenshot()

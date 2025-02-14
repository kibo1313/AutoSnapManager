from functools import reduce
from typing import Any, Dict, Hashable, Union, List
import importlib

from utils.process_dict_tools import find_key_position_at_level, get_value_by_key


def get_class_name(obj):
    """判断是否是类还是类实例"""
    if isinstance(obj, type):
        return obj.__name__
    else:
        return obj.__class__.__name__


def get_module_class(map_table: Dict[Hashable, Any], key: str, path: str = None) -> Any:
    """
    根据给定的映射表和键值动态导入模块，并返回对应的类。

    Args:
        map_table (Dict[Hashable, Any]): 包含'module.class'格式字符串作为值的字典。
        key (str): 用于在map_table中查找对应类的键。
        path(str): 用于检查key是否在指定path下

    Return:
        Any: 对应于'module.class'指定的类对象。

    Raises:
        ValueError: 如果map_table不是字典，或者'module.class'格式不正确。
        KeyError: 如果提供的key在map_table中找不到。
        ModuleNotFoundError: 如果无法找到指定的模块。
        AttributeError: 如果在模块中找不到指定的类。
    """
    if not isinstance(map_table, dict):
        raise ValueError("The provided argument must be a dictionary.")

    if path is not None:
        if (loc := find_key_position_at_level(map_table, key, path)) is None:
            raise ValueError(f"'{key}' not found in the '{path}'")
        value = reduce(lambda table, p: table[p], loc, map_table)
    else:
        value = get_value_by_key(map_table, key)

    if value is None:
        raise KeyError(f"Key '{key}' not found in the {map_table}.")
    if not isinstance(value, str):
        raise ValueError(f"The value corresponding to the {key} must be a string in the ‘module.class’ format.")
    if '.' not in value:
        raise ValueError(f"The value '{value}' is not in the 'module.class' format.")

    module_name, class_name = value.rsplit('.', 1)

    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(f"Module '{module_name}' could not be found.") from e
    except AttributeError as e:
        raise AttributeError(f"Class '{class_name}' could not be found in module '{module_name}'.") from e


def check_class_name(arg: Dict[Hashable, Any], keys: Union[Hashable, List[Hashable]], class_name: str) -> bool:
    """
    检查字典中给定键路径下的所有值是否与提供的类名匹配。

    Args:
        arg (Dict[Hashable, Any]): 包含嵌套键和值的字典。
        keys (Union[Hashable, List[Hashable]]): 单个键或键列表，表示要检查的路径。
        class_name (str): 要匹配的类名。

    Returns:
        bool: 如果所有类名与提供的类名匹配，则返回 True；如果遇到不匹配的类名则返回 False。
              如果指定路径下的值不是字符串形式，则忽略这些值。

    Raises:
        ValueError: 如果提供的 `arg` 不是字典。
        KeyError: 如果路径中的任何键在字典中找不到。

    Examples:
        # 假设 SCREENCAP 定义如下：
        # SCREENCAP = {
        #     'android': {
        #         'adb': 'android.adb.AdbDevice',
        #         'shell': 'android.shell.ShellCommand',
        #     },
        #     'ios': {
        #         'idevice': 'ios.idevice.IDevice',
        #     }
        # }

        # 检查 android.adb 是否为 AdbDevice 类
        result = check_class_name(SCREENCAP, ['android', 'adb'], 'AdbDevice')
    """
    if not isinstance(keys, list):
        keys = [keys]

    if not isinstance(arg, dict):
        raise ValueError("The provided argument must be a dictionary.")

    current = arg
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(f"Key '{key}' not found in the provided argument.")
        current = current[key]

    def is_class_name(value: str, name: str) -> bool:
        """检查最后一个阶段之后值的最后一部分是否等于class_name"""
        return isinstance(value, str) and value.endswith(name) and value.rsplit('.', 1)[-1] == name

    def check_values(sub_arg: Union[Dict[Hashable, Any], str]) -> bool:
        """递归检查嵌套字典结构中的所有字符串值是否与给定的类名匹配"""
        if isinstance(sub_arg, dict):
            for v in sub_arg.values():
                if isinstance(v, dict):
                    # 递归检查嵌套字典
                    if check_values(v):
                        return True
                elif is_class_name(v, class_name):
                    return True

        if is_class_name(sub_arg, class_name):
            return True

        return False

    return check_values(current)

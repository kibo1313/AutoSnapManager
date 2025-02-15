from typing import Any, Dict, Hashable, Optional, List, Union


def get_value_by_key(nested_dict: Dict[Hashable, Any], key: str, default: Optional[Any] = None) -> Any:
    """
    获取嵌套字典中指定键的值。

    Args:
        nested_dict: 嵌套字典。
        key: 要查找的键。
        default: 如果键不存在，返回的默认值（默认为 None）

    Returns:
        键对应的值，如果键不存在则返回默认值。
    """
    if key in nested_dict:
        return nested_dict[key]

    for k, v in nested_dict.items():
        if isinstance(v, dict):
            result = get_value_by_key(v, key, default)
            if result is not default:
                return result

    return default


def find_key_position(nested_dict: Dict[Hashable, Any], key: str) -> Optional[List[Hashable]]:
    """
    递归搜索嵌套字典中的键，并返回键的路径

    Args:
        nested_dict: 要搜索的嵌套词典
        key: 在字典中查找的键

    Returns:
        Optional[List[Hashable]]: 一个列表，表示键的路径（如果找到），否则为 None
                                 path 是指向目标键的键列表
    """
    for k, v in nested_dict.items():
        if k == key:
            return [k]
        elif isinstance(v, dict):
            result = find_key_position(v, key)
            if result:
                return [k] + result
    return None


def find_key_position_at_level(
        nested_dict: Dict[Hashable, Any],
        key: str,
        path: Union[str, List[Hashable]]
        ) -> Optional[List[Hashable]]:
    """
    在指定层级下查找键，并返回键的完整路径

    Args:
        nested_dict: 要搜索的嵌套词典
        key: 在字典中查找的键
        path: 指定层级的路径，可以是单个键（str）或键的列表（List[Hashable]）

    Returns:
        Optional[List[Hashable]]: 一个列表，表示键的完整路径（如果找到），否则为 None
    """
    if isinstance(path, str):
        path = [path]
    elif not isinstance(path, list):
        raise ValueError(f"'{path}' 必须是 str 或 List[Hashable]")

    current_dict = nested_dict.copy()
    key_path = []

    if (key_position := find_key_position(current_dict, path[0])) is None:
        return None
    key_path += key_position

    current_dict = get_value_by_key(current_dict, path[0])

    if len(path) > 1:
        for p in path[1]:
            if (current_dict := current_dict.get(p)) is None:
                return None
            key_path += p

    if not isinstance(current_dict, dict):
        raise ValueError(f"path 参数中的键对应的值可能不是字典")

    if (key_position := find_key_position(current_dict, key)) is None:
        return None
    key_path += key_position

    return key_path

import os


def check_path(path: str) -> None:
    """
    检测文件或路径。

    参数:
    path: 要检查的路径。

    异常:
    FileNotFoundError: 如果路径不存在。
    PermissionError: 如果路径无写入权限。
    TypeError: 如果传入的路径类型不是字符串、字节或os.PathLike。
    """

    if not isinstance(path, (str, bytes, os.PathLike)):
        raise TypeError("路径类型必须是字符串、字节或os.PathLike对象。")

    if os.path.isdir(path):
        path_type = "目录"
    elif os.path.isfile(path):
        path_type = "文件"
    else:
        path_type = "路径"  # 可能是其他类型的路径，如符号链接

    if not os.path.exists(path):
        raise FileNotFoundError(f"{path_type}路径不存在: {path}")

    if not os.access(path, os.W_OK):
        raise PermissionError(f"{path_type}路径无写入权限: {path}")

import inspect


def print_config() -> None:
    """打印调用者模块的所有配置项"""
    # 获取调用者的帧对象
    caller_frame = inspect.currentframe().f_back
    # 获取调用者模块的变量字典
    caller_vars = caller_frame.f_locals
    caller_globals = caller_frame.f_globals
    
    # 合并局部变量和全局变量
    all_vars = {
        name: value
        for name, value in {**caller_globals, **caller_vars}.items()
        if not name.startswith('_') and name.isupper()
    }

    print("\n=== 配置变量列表 ===")
    for name, value in all_vars.items():
        print(f"{name}: {value}")
    print("==================")

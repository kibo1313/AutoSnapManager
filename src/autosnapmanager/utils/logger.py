from loguru import logger
from autosnapmanager.utils.utils_config import WORK_DIR

logger.add(
    sink=f"{WORK_DIR}/error_log",  # 日志文件的路径
    format="{time} {level} {message}",  # 自定义日志格式
    level="ERROR",  # 设置日志级别
    rotation="00:00",  # 每天00:00进行日志轮转
    retention="7 days",  # 保留最近7天的日志
    enqueue=True,  # 异步写入
    backtrace=True,  # 记录堆栈跟踪
    diagnose=True,  # 记录诊断信息
)

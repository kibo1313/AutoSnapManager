from dataclasses import dataclass


@dataclass
class DeviceInfo:
    """设备信息数据类"""
    abi: str = None
    sdk: str = None
    id: int = None
    width: int = None
    height: int = None
    size: float = None
    density: float = None
    fps: int = None
    rotation: int = None

    def __post_init__(self):
        """初始化后处理"""
        self.vm_size = f"{self.height}x{self.width}"

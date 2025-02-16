# AutoSnapManager

AutoSnapManager 是一个用于统一管理自动化操作的工具库，旨在简化系统自动化任务的开发流程。无论是 Windows 桌面应用还是 Android 移动设备，本库都提供了简单易用的接口来实现屏幕截图、模板匹配、点击操作等功能(待扩展)。

## 安装

```bash
pip install autosnapmanager
```

## 快速开始

1. **导入模块**  
   ```python
   import autosnapmanager as asm
   ```

2. **创建管理者对象**  
   根据目标平台选择对应的管理者对象：
   - **Windows**:  
     ```python
     manager = asm.Windows()
     manager = asm.Windows(window_name='MyApp')
     ```
   - **Android**:  
     ```python
     manager = asm.Android(serial='your_device_serial')
     ```

3. **使用核心功能**  
   以下是一个简单的示例，展示如何使用 `screenshot`、`match` 和 `click` 方法：
   ```python
   # 截图并保存
   manager.screenshot(save_path='screenshot.png')

   # 匹配模板
   if manager.match(template_path='template.png', threshold=0.8):
       print("模板匹配成功！")

   # 点击匹配位置
   manager.click(template='template.png', threshold=0.8)
   
   # 点击指定位置
   manager.click((100, 200)) 
   ```

---

## 功能概述

### 核心 API

`WindowsManager` 和 `AndroidManager` 继承自抽象基类 `Manager`，实现了以下核心方法：

#### 1. `screenshot(save_path: str = None)`
- **功能**: 截取屏幕截图。
- **参数**: 
  - `save_path`: 可选参数，指定截图保存路径，默认保存在当前目录。
- **返回值**: 无

#### 2. `match(template_path: str, threshold: float = None)`
- **功能**: 检查模板是否匹配成功。
- **参数**: 
  - `template_path`: 模板图片路径。
  - `threshold`: 匹配阈值，默认为 `0.9`。
- **返回值**: 返回布尔值，表示匹配是否成功。

#### 3. `click(template: Union[str, tuple], threshold: float = None)`
- **功能**: 点击匹配位置或指定坐标。
- **参数**: 
  - `template`: 可以是模板图片路径或元组坐标 `(x, y)`。
  - `threshold`: 匹配阈值（仅当 `template` 为图片时有效）。
- **返回值**: 无

---

## 平台支持

### 1. WindowsManager

#### 初始化参数
- `window_name`: 可选窗口名称。
- `screencap`: 指定截图方法，默认为 `WindowScreenCap`（如果窗口存在），否则为 `FullScreenCap`。
- `match`: 指定模板匹配方法，默认为 `OpenCVMatch`。
- `click`: 指定点击方法，默认为 `Win32GuiClick`（如果窗口存在），否则为 `PyAutoGuiClick`。

#### 示例
```python
manager = asm.Windows(
    window_name="MyApp",
    screencap=asm.ScreenCaps.Window,
    match=asm.Matches.OpenCV,
    click=asm.Clicks.Win32Gui
)
```

---

### 2. AndroidManager

#### 初始化参数
- `serial`: 设备序列号。
- `screencap`: 指定截图方法，默认为 `MiniCap`。
- `match`: 指定模板匹配方法，默认为 `OpenCVMatch`。
- `click`: 指定点击方法，默认为 `ADBTouch`。

#### 示例
```python
manager = asm.Android(
    serial="device_serial",
    screencap=asm.ScreenCaps.MiniCap,
    match=asm.Matches.OpenCV,
    click=asm.Clicks.Adb
)
```

#### 特殊方法
- **滑动操作**:  
  ```python
  manager.swipe(start_x=100, start_y=200, end_x=400, end_y=200)
  ```

---

### 3. 参数格式详解

为了方便用户灵活配置，`AutoSnapManager` 支持多种参数格式：

#### (1) 字符串格式
直接通过字符串指定方法名称：
```python
manager = asm.Windows(screencap='window', click='pyautogui')
manager = asm.Android(screencap='minicap', click='minitouch')
```

#### (2) 枚举变量格式
使用枚举变量指定方法：
```python
manager = asm.Windows(screencap=asm.ScreenCaps.Window, click=asm.Clicks.Win32Gui)
manager = asm.Android(screencap=asm.ScreenCaps.MiniCap, click=asm.Clicks.MiniTouch)
```

#### (3) 类实例格式
通过类实例自定义参数：
```python
# Windows 示例
manager = asm.Windows(
    screencap=asm.WindowScreenCap(window_name="MyApp"),
    match=asm.OpenCVMatch(threshold=0.8, colors=True),
    click=asm.Win32Api(window_name="MyApp")
)

# Android 示例
manager = asm.Android(
    screencap=asm.MiniCap(serial="device_serial", rate=60, quality=80),
    click=asm.MiniTouch(serial="device_serial")
)
```

---

## 截图方法

### 1. FullScreenCap（Windows）
- **功能**: 全屏截图。
- **性能**: 快，适合全屏操作。
- **初始化**: 无需额外参数。

### 2. WindowScreenCap（Windows）
- **功能**: 窗口截图，即使窗口被遮挡也能截取。
- **性能**: 快，适合特定窗口操作。
- **初始化**: 需要提供窗口名称。

### 3. ADBCap（Android）
- **功能**: 使用 ADB 截图。
- **性能**: 较慢（300ms之上）。
- **初始化**: 需要提供设备序列号。

### 4. MiniCap（Android）
- **功能**: 高效实时屏幕传输工具。
- **性能**: 极快（约 20-30ms）。
- **初始化**: 支持多种参数（如帧率、质量等）。

---

## 模板匹配方法

### OpenCVMatch
- **功能**: 基于 OpenCV 的模板匹配。
- **参数**: 
  - `threshold`: 匹配阈值，默认 `0.9`。
  - `colors`: 是否启用色彩匹配，默认 `False`。
  - `scale`: 是否启用缩放匹配，默认 `False`。

---

## 点击与触摸方法

### Windows 点击
- **PyAutoGuiClick**: 操作真实鼠标。
- **Win32GuiClick**: 操作虚拟鼠标，不影响真实鼠标。

### Android 触摸
- **ADBTouch**: 支持点到点直线滑动。
- **MiniTouch**: 支持曲线滑动，低延迟，不支持安卓13以上。
- **MAATouch**: MiniTouch 的增强版本，不支持安卓13以上。

---

## 贡献与反馈

欢迎贡献代码或提出问题！请访问 [AutoSnapManager](https://github.com/kibo1313/AutoSnapManager) 提交 Issue 或 Pull Request。

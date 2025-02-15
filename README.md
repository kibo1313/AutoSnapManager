# AutoSnapManager
旨在通过一个管理者对象对不同系统的自动化操作进行一个统一的管理，使其变得简单有序

## 安装
`pip install autosnapmanager`

## 使用说明
1. 导入模块 `import autosnapmanager as asm`
2. 创建一个管理者对象（目前支持Windows和Android端控制）
   * `asm.Android() 或 asm.Windows()`
3. 管理者对象说明
   * 支持screenshot保存截图
   * 支持click模板点击与位置点击
   * 支持match匹配成功判断
   * android端支持swipe滑动操作

## API文档说明
Windows与Android继承自Manager抽象基类，实现了screenshot，match，click方法
screenshot支持自定义保存路径参数，默认保存在当前目录下
match支持自定义匹配阈值参数，默认不指定阈值
click支持图片路径与元组坐标(x, y)进行点击操作

### Manager管理抽象类
#### WindowsManager管理类
#### AndroidManager管理类

### ScreenCap截图抽象类
#### FullScreenCap截图类（windows）
#### WindowScreenCap截图类（windows）
#### ADBCap截图类（android）
#### MiniCap截图类（android）

### Match模板匹配抽象类
#### OpenCVMatch匹配类（windows | android）

### Click点击操作抽象类
#### PyAutoGui点击类（windows）
#### Win32Gui点击类（windows）
#### Win32Api点击类（windows）

* ### Touch触摸操作抽象类
  * #### ADBTouch触摸类（android）
  * #### MiniTouch触摸类（android）
  * #### MAATouch触摸类（android）

* ScreenCap
  * 抽象方法screencap，捕获屏幕内容并返回numpy数组 
  * 成员方法save_screencap，保存numpy数组数据到指定路径
* Match
  * 抽象方法match，判断匹配成功与否
  * 抽象方法locate_center， 返回匹配成功的中心坐标
* Click
  * 抽象方法click，点击操作
* Touch抽象类
  * 继承自Click
  * 抽象方法touch，点击操作
  * 抽象方法swipe，滑动操作

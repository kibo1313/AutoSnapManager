from adbutils import adb

from autosnapmanager.actions.clicks.android.touch import Touch


class ADBTouch(Touch):
    def __init__(self, serial: str):
        self._adb = adb.device(serial)

    def click(self, x: int, y: int, duration: int = None) -> None:
        if duration:
            adb_command = ['input', 'swipe', str(x), str(y), str(x), str(y), str(duration / 1000.0)]
        else:
            adb_command = ['input', 'touchscreen', 'tap', str(x), str(y)]
        result = self._adb.shell2(adb_command)
        if result.returncode != 0:
            raise RuntimeError(result.output)

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 300) -> None:
        self._adb.swipe(start_x, start_y, end_x, end_y, duration / 1000.0)


if __name__ == "__main__":
    touch = ADBTouch('127.0.0.1:16384')
    # touch.click(500, 500)
    touch.swipe(800, 800, 100, 800, 100)

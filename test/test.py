import src.autosnapmanager as asm

an = asm.Android("127.0.0.1:16384", screencap=asm.ScreenCaps.Adb,
                 click=asm.Clicks.Adb)
# an.swipe(100, 800, 800, 800)
an.click((200, 150))

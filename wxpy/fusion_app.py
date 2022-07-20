import wx
from frame_main import FrameMain


class MainApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.frame = None       # 这里声明一下self变量可以避免警告

    def OnInit(self):
        self.frame = FrameMain(None)
        self.frame.Show(True)
        return True             # 返回False程序将会立即退出

    def OnExit(self):
        self.frame = None       # 非必要，只是为了用一下self
        return 0                # 返回状态码


if __name__ == '__main__':
    app = MainApp()
    app.MainLoop()
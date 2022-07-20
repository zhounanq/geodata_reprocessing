import wx


class FrameMain(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=-1, title="Raster fusion", size=(500, 400))    # 设置窗体

        # 状态栏
        bar = self.CreateStatusBar()
        self.SetStatusBar(bar)

        """
        panel和sizer是wxpython提供的窗口部件。是容器部件，可以用于存放其他窗口部件
        """
        panel = wx.Panel(self)
        # sizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.GridSizer(rows=3, cols=3, vgap=5, hgap=5)    # vgap hgap代表水平距离和垂直距离
        panel.SetSizer(sizer)

        # 创建静态文本组件
        txt = wx.StaticText(panel, -1, "Image @ t1", pos=(10, 10), size=(80, 25), style=wx.ALIGN_CENTER)
        font = wx.Font(12, wx.DEFAULT, wx.ITALIC, wx.NORMAL, True)
        txt.SetFont(font)
        # sizer.Add(txt)

        # 创建文本输入框
        input_text = wx.TextCtrl(panel, -1, "", pos=(100, 10), size=(300, -1))
        input_text.SetInsertionPoint(1)      # 设置焦点
        # sizer.Add(input_text)

        # 按钮
        btn = wx.Button(panel, -1, "...", pos=(400, 10), size=(80, 30))
        # sizer.Add(btn, 0, wx.TOP | wx.LEFT, 50)
        btn.Bind(wx.EVT_BUTTON, self.OnClick)
        btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter2)
        btn.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        # sizer.Add(btn)


        # 表格控件
        #

        self.Center()       # 将窗口放在桌面环境的中间



    def OnClick(self, event):
        # dialog = wx.Dialog(None, title="Hi, Clicked!", size=(300, 200))
        # dialog.Show()
        #self.Close(True)

        dialog = wx.TextEntryDialog(None, message="请输入文件名:", caption="文件", value="test")
        res = dialog.ShowModal()
        print (res)


    def OnMouseEnter(self, event):
        print ("Mouse enter")


    def OnMouseEnter2(self, event):
        print ("Mouse enter2")
        event.Skip()        # 后注册的事件响应函数会覆盖之前的，默认仅执行一个，如需继续则调用Skip


    def OnMouseLeave(self, event):
        print ("Mouse leave")


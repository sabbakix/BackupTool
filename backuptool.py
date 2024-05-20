import wx
import shutil
import os
from wx.lib.dialogs import ScrolledMessageDialog

def backup_files(source, destination):
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, False, None)
        else:
            shutil.copy2(s, d)

class BackupTool(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Backup Tool", size=(600, 300))

        panel = wx.Panel(self)

        source_label = wx.StaticText(panel, label="Source Directory:")
        self.source_dir = wx.DirPickerCtrl(panel)

        destination_label = wx.StaticText(panel, label="Destination Directory:")
        self.destination_dir = wx.DirPickerCtrl(panel)

        self.backup_button = wx.Button(panel, label="Start backup")
        self.backup_button.Bind(wx.EVT_BUTTON, self.start_backup)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(source_label, 0, wx.ALL, 5)
        sizer.Add(self.source_dir, 0, wx.ALL, 5)
        sizer.Add(destination_label, 0, wx.ALL, 5)
        sizer.Add(self.destination_dir, 0, wx.ALL, 5)
        sizer.Add(self.backup_button, 0, wx.ALL, 5)

        panel.SetSizer(sizer)

    def start_backup(self, event):
        source = self.source_dir.GetPath()
        destination = self.destination_dir.GetPath()
        backup_files(source, destination)

app = wx.App(False)
frame = BackupTool()
frame.Show()
app.MainLoop()
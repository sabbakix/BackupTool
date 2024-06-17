import wx
import os
import csv
import hashlib
import time
from datetime import datetime
from filecmp import dircmp

class Mywin(wx.Frame):
    def __init__(self, parent, title): 
        super(Mywin, self).__init__(parent, title = title, size = (300,300)) 
        panel = wx.Panel(self) 
        vbox = wx.BoxSizer(wx.VERTICAL) 

        source_label = wx.StaticText(panel, label="Source Directory:")
        self.source_dir_picker = wx.DirPickerCtrl(panel)
        destination_label = wx.StaticText(panel, label="Destination Directory:")
        self.destination_dir_picker = wx.DirPickerCtrl(panel)
        self.btn = wx.Button(panel, -1, "Start") 
        self.btn.Bind(wx.EVT_BUTTON, self.OnClicked) 

        vbox.Add(source_label, 2, flag = wx.EXPAND)
        vbox.Add(self.source_dir_picker, 1, flag = wx.EXPAND, border = 5) 
        vbox.Add(destination_label, 2, flag = wx.EXPAND)
        vbox.Add(self.destination_dir_picker, 1, flag = wx.EXPAND, border = 5) 
        vbox.Add(self.btn, 1, flag = wx.EXPAND, border = 5) 

        panel.SetSizer(vbox) 
        self.Centre() 
        self.Show(True) 

    def OnClicked(self, event): 
        source_dir = self.source_dir_picker.GetPath()
        destination_dir = self.destination_dir_picker.GetPath()
        self.scan_directory(source_dir, 'source.csv')
        self.scan_directory(destination_dir, 'destination.csv')
        self.compare_directories('source.csv', 'destination.csv', 'comparison.csv')

    def scan_directory(self, directory, output_file):
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Path', 'Modification Time', 'Hash']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    modification_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    file_hash = self.hash_file(file_path)
                    writer.writerow({'Path': file_path, 'Modification Time': modification_time, 'Hash': file_hash})

    def hash_file(self, file_path):
        BUF_SIZE = 65536
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()

    def compare_directories(self, source_file, destination_file, output_file):
        source_files = self.read_csv(source_file)
        destination_files = self.read_csv(destination_file)
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Path', 'Status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for file in source_files:
                if file not in destination_files:
                    writer.writerow({'Path': file, 'Status': 'Missing'})
                elif source_files[file] != destination_files[file]:
                    writer.writerow({'Path': file, 'Status': 'Modified'})

    def read_csv(self, file):
        with open(file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return {row['Path']: row for row in reader}

app = wx.App() 
Mywin(None,"Directory Comparison") 
app.MainLoop()
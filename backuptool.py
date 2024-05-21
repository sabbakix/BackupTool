import wx
import shutil
import os
from wx.lib.dialogs import ScrolledMessageDialog
import threading
import csv
import hashlib

def get_file_info(path):
    size = os.path.getsize(path)
    mod_time = os.path.getmtime(path)
    with open(path, 'rb') as f:
        bytes = f.read()
        readable_hash = hashlib.sha256(bytes).hexdigest()
    return size, mod_time, readable_hash

def get_dir_info(path):
    mod_time = os.path.getmtime(path)
    return mod_time

def count_files_and_dirs(path):
    num_files = 0
    num_dirs = 0
    for dirpath, dirnames, filenames in os.walk(path):
        num_files += len(filenames)
        num_dirs += len(dirnames)
    return num_files, num_dirs


def scan_dir(source, destination, progress):

    num_files, num_dirs = count_files_and_dirs(source)
    print(f"Number of files: {num_files}")
    print(f"Number of directories: {num_dirs}")

    with open('file_info.csv', 'w', newline='') as csvfile:
        fieldnames = ['type', 'path', 'size', 'modification_time', 'sha256_hash']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        print(f"Scanning {source}")
        print(f"Destination: {destination}")
        print("Scanning files and directories...")
        print("This may take a while...")
        print("Please wait...")
        i=0
        for dirpath, dirnames, filenames in os.walk(source):
            #print(f"Scanning {dirpath}")
            #print(f"Directories: {dirnames}")
            progress_val = int( i / (num_files + num_dirs) * 100)
            print(f"Progress: {progress_val}%")
            wx.CallAfter(progress.SetValue, progress_val)
            i=i+1
            for d in dirnames:
                s = os.path.join(dirpath, d)
                try:
                    mod_time = get_dir_info(s)
                    writer.writerow({'type': 'd', 'path': s, 'size': 'N/A', 'modification_time': mod_time, 'sha256_hash': 'N/A'})
                except Exception as e:
                    print(f"Error scanning {s}: {e}")
            for f in filenames:
                s = os.path.join(dirpath, f)
                try:
                    size, mod_time, hash = get_file_info(s)
                    writer.writerow({'type': 'f', 'path': s, 'size': size, 'modification_time': mod_time, 'sha256_hash': hash})
                except Exception as e:
                    print(f"Error scanning {s}: {e}")
        print("Scan complete")

def copy_files(source, destination, progress):
    with open('file_info.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        files = list(reader)
        num_files = len(files)
        for i, row in enumerate(files):
            s = row['path']
            d = os.path.join(destination, os.path.relpath(s, source))
            try:
                if row['type'] == 'd':
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(d), exist_ok=True)
                    shutil.copy2(s, d)
            except Exception as e:
                print(f"Error copying {s} to {d}: {e}")

            progress_val = int((i+1) / num_files * 100)
            wx.CallAfter(progress.SetValue, progress_val)

def backup_files(source, destination, progress):
    files = os.listdir(source)
    num_files = len(files)
    with open('file_info.csv', 'w', newline='') as csvfile:
        fieldnames = ['type','path', 'size', 'modification_time', 'sha256_hash']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, item in enumerate(files):
            s = os.path.join(source, item)
            d = os.path.join(destination, item)
            try:
                if os.path.isdir(s):
                    shutil.copytree(s, d, False, None)
                    mod_time = get_dir_info(s)
                    writer.writerow({'type':'d','path': s, 'size': 'N/A', 'modification_time': mod_time, 'sha256_hash': 'N/A'})
                else:
                    shutil.copy2(s, d)
                    size, mod_time, hash = get_file_info(s)
                    writer.writerow({'type':'f','path': s, 'size': size, 'modification_time': mod_time, 'sha256_hash': hash})
            except Exception as e:
                print(f"Error copying {s} to {d}: {e}")
            
            progress_val = int((i+1) / num_files * 100)
            wx.CallAfter(progress.SetValue, progress_val)




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

        self.progress = wx.Gauge(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(source_label, 0, wx.ALL, 5)
        sizer.Add(self.source_dir, 0, wx.ALL, 5)
        sizer.Add(destination_label, 0, wx.ALL, 5)
        sizer.Add(self.destination_dir, 0, wx.ALL, 5)
        sizer.Add(self.backup_button, 0, wx.ALL, 5)
        sizer.Add(self.progress, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)

    def start_backup(self, event):
        source = self.source_dir.GetPath()
        destination = self.destination_dir.GetPath()
        self.backup_thread = threading.Thread(target=scan_dir, args=(source, destination, self.progress))
        self.backup_thread.start()

app = wx.App(False)
frame = BackupTool()
frame.Show()
app.MainLoop()

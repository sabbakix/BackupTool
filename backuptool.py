import shutil
import os
import threading
import csv
import hashlib
import datetime
import configparser
import time

import wx
from wx.lib.dialogs import ScrolledMessageDialog

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

def get_timestamp():
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
    #print(timestamp)
    return timestamp


def scan_dir(job, source, destination, progress, status, list_of_files_file_path):

    num_files, num_dirs = count_files_and_dirs(source)
    print(f"Number of files: {num_files}")
    print(f"Number of directories: {num_dirs}")

    file_list = "".join(["file_info_", get_timestamp() , ".csv"])

    with open( file_list, 'w', newline='') as csvfile:
        fieldnames = ['type', 'path', 'size', 'modification_time', 'sha256_hash']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        print(f"Scanning {source}")
        print(f"Destination: {destination}")
        print("Scanning files and directories...")
        i=1
        for dirpath, dirnames, filenames in os.walk(source):
            #print(f"Scanning {dirpath}")
            #print(f"Directories: {dirnames}")
            for d in dirnames:
                i=i+1
                s = os.path.join(dirpath, d)
                status_val = f"Scanning {s}"
                try:
                    mod_time = get_dir_info(s)
                    writer.writerow({'type': 'd', 'path': s, 'size': 'N/A', 'modification_time': mod_time, 'sha256_hash': 'N/A'})
                except Exception as e:
                    print(f"Error scanning {s}: {e}")
            for f in filenames:
                i=i+1
                s = os.path.join(dirpath, f)
                status_val = f"Scanning {s}"
                try:
                    size, mod_time, hash = get_file_info(s)
                    writer.writerow({'type': 'f', 'path': s, 'size': size, 'modification_time': mod_time, 'sha256_hash': hash})
                except Exception as e:
                    print(f"Error scanning {s}: {e}")
            
            progress_val = int( i / (num_files + num_dirs) * 100)
            if progress_val > 100:
                progress_val = 100
            print(f"Progress: {progress_val}%")
            wx.CallAfter(progress.SetValue, progress_val)
            wx.CallAfter(status.SetLabel, status_val)
            wx.CallAfter(list_of_files_file_path.SetLabel, file_list)
        status.SetLabel('Scan complete')
        print("Scan complete")

def copy_files(job, source, destination, progress):

    file_list = "file_info".join([str(job), ".csv"])
    with open( file_list, 'r', newline='') as csvfile:
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

def backup_files(job, source, destination, progress):
    files = os.listdir(source)
    num_files = len(files)

    file_list = "".join([str(job), ".csv"])
    with open(file_list, 'w', newline='') as csvfile:
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


# Define the BackupTool class, which is a subclass of wx.Frame
class BackupTool(wx.Frame):
    # The __init__ method initializes the object
    def __init__(self, parent, title):
        # Call the constructor of the parent class
        super(BackupTool, self).__init__(parent, title=title, size=(900, 300))

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        if 'BackupTool' in self.config:
            self.last_selected_source_dir = self.config['BackupTool'].get('last_selected_source_dir', '')
            self.last_selected_destination_dir = self.config['BackupTool'].get('last_selected_destination_dir', '')
        else:
            self.last_selected_source_dir = ''
            self.last_selected_destination_dir = ''

        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
        print(timestamp)
        self.job = timestamp

        # Create a panel on the frame
        panel = wx.Panel(self)

        # Create a vertical box sizer
        box = wx.BoxSizer(wx.VERTICAL)

        # Create a horizontal box sizer
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        # Create a static text widget with the label 'SOURCE:'
        source_label = wx.StaticText(panel, label="Source Directory:")
        self.source_dir = wx.DirPickerCtrl(panel)
        self.source_dir.SetPath(self.last_selected_source_dir)

        # Create a static text widget with the label 'DESTINATION:'
        destination_label = wx.StaticText(panel, label="Destination Directory:")
        self.destination_dir = wx.DirPickerCtrl(panel)
        self.destination_dir.SetPath(self.last_selected_destination_dir)

        # Bind the directory changed event of the directory picker controls
        self.source_dir.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_source_dir_changed)
        self.destination_dir.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_destination_dir_changed)

        # Add the static text and directory picker controls to the horizontal box sizer
        hbox1.Add(source_label, flag=wx.RIGHT, border=8)
        hbox1.Add(self.source_dir, proportion=1)
        hbox1.Add(destination_label , flag=wx.LEFT, border=40)
        hbox1.Add(self.destination_dir, proportion=1)
        # Add the horizontal box sizer to the vertical box sizer
        box.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Add a spacer to the vertical box sizer
        box.Add((-1, 10))


        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.scanning_button = wx.Button(panel, label="Start scanning")
        self.scanning_button.Bind(wx.EVT_BUTTON, self.start_scan_dir)
        hbox2.Add(self.scanning_button, flag=wx.RIGHT, border=8)
        #box.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

        self.backup_button = wx.Button(panel, label="Start backup")
        self.backup_button.Bind(wx.EVT_BUTTON, self.start_backup)
        hbox2.Add(self.backup_button, flag=wx.RIGHT, border=8)
        #box.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

        self.close_button = wx.Button(panel, label="Close")
        self.close_button.Bind(wx.EVT_BUTTON, self.on_close_button)
        hbox2.Add(self.close_button, flag=wx.RIGHT, border=8)
        box.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

        box.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, label='PROGRESS:')
        hbox3.Add(st3, flag=wx.RIGHT, border=8)
        box.Add(hbox3, flag=wx.LEFT | wx.TOP, border=10)

        # Add a spacer to the vertical box sizer
        box.Add((-1, 10))

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.progress = wx.Gauge(panel)
        hbox4.Add(self.progress, proportion=1, flag=wx.EXPAND)
        box.Add(hbox4, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)

        # Add a spacer to the vertical box sizer
        box.Add((-1, 10))

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.status = wx.StaticText(panel, label='Status')
        hbox5.Add(self.status, flag=wx.RIGHT, border=8)
        box.Add(hbox5, flag=wx.LEFT | wx.TOP, border=10)

        # Add a spacer to the vertical box sizer
        box.Add((-1, 10))
        
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.list_of_files_file_path = wx.StaticText(panel, label='list of files:')
        hbox6.Add(self.list_of_files_file_path, flag=wx.RIGHT, border=8)
        box.Add(hbox6, flag=wx.LEFT | wx.TOP, border=10)

        # Add a spacer to the vertical box sizer
        box.Add((-1, 10))

        # Set the sizer for the panel
        panel.SetSizer(box)
        # Center the frame on the screen
        self.Centre()
        # Show the frame
        self.Show(True)

    def on_source_dir_changed(self, event):
        path = event.GetPath()
        self.last_selected_source_dir = path
        print(f"Selected source directory: {path}")
        self.save_config()

    def on_destination_dir_changed(self, event):
        path = event.GetPath()
        self.last_selected_destination_dir = path
        print(f"Selected destination directory: {path}")
        self.save_config()

    def save_config(self):
        self.config['BackupTool'] = {
            'last_selected_source_dir': self.last_selected_source_dir,
            'last_selected_destination_dir': self.last_selected_destination_dir
        }
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def start_scan_dir(self, event):
        source = self.source_dir.GetPath()
        destination = self.destination_dir.GetPath()
        self.scan_thread = threading.Thread(target=scan_dir, args=(self.job, source, destination, self.progress, self.status, self.list_of_files_file_path))
        self.scan_thread.start()

    def start_backup(self, event):
        source = self.source_dir.GetPath()
        destination = self.destination_dir.GetPath()
        self.backup_thread = threading.Thread(target=scan_dir, args=(self.job, source, destination, self.progress, self.status))
        self.backup_thread.start()
    
    def on_close_button(self, event):
        self.Close(True)


# Define the Model class
class Model:
    def __init__(self):
        self.data = []

    def add_data(self, data):
        self.data.append(data)
        # Simulate a long-running task
        time.sleep(5)

class View(wx.Frame):
    def __init__(self, controller):
        # Initialize the frame
        # Create widgets
        frame = BackupTool(None, "Backup Tool")
        frame.Show()
        #self.button = wx.Button(self, label="Add Data")
        #self.button.Bind(wx.EVT_BUTTON, controller.on_button_click)

class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)

    def on_button_click(self, event):
        thread = threading.Thread(target=self.model.add_data, args=("New data",))
        thread.start()

if __name__ == '__main__':
    app = wx.App(False)
    
    controller = Controller()
    app.MainLoop()
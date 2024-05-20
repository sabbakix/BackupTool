import shutil
import os
from tkinter import filedialog
from tkinter import Tk, Label, Button, StringVar

def backup_files(source, destination):
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, False, None)
        else:
            shutil.copy2(s, d)

class BackupTool:
    def __init__(self, master):
        self.master = master
        master.title("Backup Tool")

        self.source_dir = StringVar()
        self.destination_dir = StringVar()

        self.source_label = Label(master, textvariable=self.source_dir)
        self.source_label.pack()

        self.destination_label = Label(master, textvariable=self.destination_dir)
        self.destination_label.pack()

        self.source_button = Button(master, text="Select source directory", command=self.select_source)
        self.source_button.pack()

        self.destination_button = Button(master, text="Select destination directory", command=self.select_destination)
        self.destination_button.pack()

        self.backup_button = Button(master, text="Start backup", command=self.start_backup)
        self.backup_button.pack()

    def select_source(self):
        self.source_dir.set(filedialog.askdirectory())

    def select_destination(self):
        self.destination_dir.set(filedialog.askdirectory())

    def start_backup(self):
        backup_files(self.source_dir.get(), self.destination_dir.get())

root = Tk()
backup_tool = BackupTool(root)
root.mainloop()
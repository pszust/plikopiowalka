import tkinter as tk
from tkinter import filedialog
import re
import os
import shutil

padd = 5


class Application:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Plikopiowalka")
        self.window.geometry("700x700")
        if os.path.isfile('icon.ico'):
            self.window.iconbitmap("icon.ico")

        self.cwd = ''  # current working directory
        self.rawFiles = []  # list of raw files from cwd
        self.filterList = []  # filter which files are to be removed from list (as a mask where 1 means stay and 0 remove)
        self.folders = {}  # dict to hold folder/sample names as keys and files as values

        self.create_menu()
        self.create_win_cnt()

        self.window.mainloop()

    def create_menu(self):
        self.menu = tk.Menu(self.window)

        cascade = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Program", menu=cascade)
        cascade.add_command(label="Open", command=self.open_directory)

        self.window.config(menu=self.menu)

    def create_win_cnt(self):
        # FIRST COLUMN
        col1 = tk.Frame(self.window)
        col1.grid(row=0, column=0, padx=padd, sticky='n')

        frame = tk.Frame(col1)
        frame.pack(fill=tk.Y, padx=padd)
        label = tk.Label(frame, text='List of current data files')
        label.pack(side=tk.LEFT)

        # listbox
        frame = tk.Frame(col1)
        frame.pack(fill=tk.Y, padx=padd)
        self.listboxFiles = tk.Listbox(frame, height=20, width=30)
        self.listboxFiles.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollFiles = tk.Scrollbar(frame)
        scrollFiles.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.listboxFiles.config(yscrollcommand=scrollFiles.set)
        scrollFiles.config(command=self.listboxFiles.yview)

        # filters
        frame = tk.Frame(col1)
        frame.pack(fill=tk.Y, padx=padd)
        label = tk.Label(frame, text='Filter files:')
        label.pack(side=tk.LEFT, pady=padd)

        frame = tk.Frame(col1)
        frame.pack(fill=tk.Y, padx=padd)
        self.filterVar = tk.StringVar()
        self.filterVar.trace_add('write', lambda name,
                                 index, mode: self.calculate_filter())
        entry = tk.Entry(frame, width=30, textvariable=self.filterVar)
        entry.pack(side=tk.LEFT, fill=tk.BOTH)

        frame = tk.Frame(col1)
        frame.pack(fill=tk.Y, padx=padd)
        self.radioSel = tk.IntVar()
        self.radioSel.trace_add('write', lambda name,
                                index, mode: self.calculate_filter())
        r1 = tk.Radiobutton(frame, text='Include only these',
                            variable=self.radioSel, value=0)
        r1.pack(side=tk.TOP)
        r2 = tk.Radiobutton(frame, text='Exclude these',
                            variable=self.radioSel, value=1)
        r2.pack(side=tk.TOP)
        btn = tk.Button(frame, text='Apply filter',
                        width=20, command=self.apply_filter)
        btn.pack(side=tk.TOP)

        # SECOND COLUMN
        col2 = tk.Frame(self.window)
        col2.grid(row=0, column=1, padx=padd, sticky='n')

        frame = tk.Frame(col2)
        frame.pack(fill=tk.Y, padx=padd, side=tk.TOP)
        label = tk.Label(frame, text='List of samples folders to create')
        label.pack(side=tk.LEFT)

        # listbox
        frame = tk.Frame(col2)
        frame.pack(fill=tk.Y, padx=padd)
        self.listboxFolders = tk.Listbox(frame, height=20, width=30)
        self.listboxFolders.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollFolders = tk.Scrollbar(frame)
        scrollFolders.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.listboxFolders.config(yscrollcommand=scrollFolders.set)
        scrollFolders.config(command=self.listboxFolders.yview)

        # buttons
        frame = tk.Frame(col2)
        frame.pack(fill=tk.Y, padx=padd)

        self.btnMoveFiles = tk.Button(frame, text='Move files', width=20,
                        command=self.move_files)
        self.btnMoveFiles.pack(side=tk.TOP)
        self.btnMoveFiles['state'] = 'disabled'

        # THIRD COLUMN
        col3 = tk.Frame(self.window)
        col3.grid(row=0, column=2, padx=padd, sticky='n')

        frame = tk.Frame(col3)
        frame.pack(fill=tk.Y, padx=padd, side=tk.TOP)
        label = tk.Label(frame, text='List files in selected folder')
        label.pack(side=tk.LEFT)

        # listbox
        frame = tk.Frame(col3)
        frame.pack(fill=tk.Y, padx=padd)
        self.listboxFilesFolder = tk.Listbox(frame, height=20, width=30)
        self.listboxFilesFolder.pack(side=tk.LEFT, fill=tk.BOTH)
        # detect click in the folders listbox to manipulate this listbox
        self.listboxFolders.bind("<<ListboxSelect>>", self.update_files_folder)

        scrollFFolders = tk.Scrollbar(frame)
        scrollFFolders.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.listboxFilesFolder.config(yscrollcommand=scrollFFolders.set)
        scrollFFolders.config(command=self.listboxFilesFolder.yview)

    def open_directory(self):
        '''
        Updates current working directory (self.cwd) and gets a list of files
        '''
        self.cwd = tk.filedialog.askdirectory()
        if self.cwd != '':
            self.rawFiles = os.listdir(self.cwd)
            self.filterList = len(self.rawFiles) * [1]  # reset filter
            self.filterVar.set('')
            self.update_files_folder('')
            self.update_boxes()

    def calculate_filter(self):
        '''
        Updates filter based on filter phrase (user input from self.filterVar) and wherther inclusion or exclusion was selected (self.radioSel)
        '''
        phrase = self.filterVar.get()
        self.filterList = len(self.rawFiles) * [1]
        if phrase != '':  # dont filter when no filter is entered
            self.filterList = len(self.rawFiles) * [1]

            # inclusion
            if self.radioSel.get() == 0:  
                for i in range(0, len(self.rawFiles)):
                    file = self.rawFiles[i]
                    if re.search(phrase, file):
                        self.filterList[i] = 1
                    else:
                        self.filterList[i] = 0

            # exclusion
            if self.radioSel.get() == 1:  
                for i in range(0, len(self.rawFiles)):
                    file = self.rawFiles[i]
                    if re.search(phrase, file):
                        self.filterList[i] = 0
                    else:
                        self.filterList[i] = 1

        self.update_boxes()

    def apply_filter(self):
        '''
        Applies filter to the list of raw files (ie. deletes elements from self.rawFiles)
        '''
        if self.filterVar.get() != '':
            oldFiles = self.rawFiles.copy()
            self.rawFiles = []
            for fil, file in zip(self.filterList, oldFiles):
                if fil == 1:
                    self.rawFiles.append(file)
            self.calculate_filter()
        self.filterVar.set('')  # reset the filter

    def update_boxes(self):
        '''
        Applies coloring to the raw files listbox based on current filter (se;f.filterList). 
        Updates folders to be created (self.folders) based on raw files names. 
        Populates the middle listbox with that folders
        '''
        # populate the list for files
        self.listboxFiles.delete(0, tk.END)
        for i, file in enumerate(self.rawFiles):
            self.listboxFiles.insert(i, file)

        # add colors when filtering is on
        if self.filterVar.get() != '':
            for i, fil in enumerate(self.filterList):
                if fil == 0:
                    self.listboxFiles.itemconfig(
                        i, {'bg': '#bf423b'})  # light red color
                if fil == 1:
                    self.listboxFiles.itemconfig(
                        i, {'bg': '#32a852'})  # light green color

        # get file destinations
        self.folders = {}
        for file in self.rawFiles:
            # find numeric postfix (ie. any digits before .)
            x = re.search('\d+(?=\.)', file)
            s = file[:x.span()[0]]
            # find postifx separator (currently searching for -, _ or space)
            x = re.search('[-_ ]$', s)
            if x != None:
                # if separator was found, exclude it from sample name (ie. so its is not called SAMPLE_ but just SAMPLE)
                s = s[:x.span()[0]]
            # create folder entry in folders or append to existing one
            if s not in self.folders.keys():
                self.folders[s] = [file]
            else:
                self.folders[s].append(file)

        # populate the list of folders
        self.listboxFolders.delete(0, tk.END)
        for i, fol in enumerate(self.folders.keys()):
            self.listboxFolders.insert(i, fol)

        # change state of the move button according to available files
        if self.folders:            
            self.btnMoveFiles['state'] = 'normal'
        else:            
            self.btnMoveFiles['state'] = 'disabled'

    def update_files_folder(self, event):
        '''
        Gets the currently selected folders names and lists files to be moved to that folders 
        '''
        self.listboxFilesFolder.delete(0, tk.END)

        folder_names = [self.listboxFolders.get(
            i) for i in self.listboxFolders.curselection()]

        if len(folder_names) > 0:
            files = []
            for folder_name in folder_names:
                if folder_name in self.folders.keys():
                    # get list of files to be moved to that folder
                    files += self.folders[folder_name]
            if len(files) != 0:
                for i, file in enumerate(files):
                    self.listboxFilesFolder.insert(i, file)
        else:
            self.listboxFilesFolder.insert(0, 'Select folder to list files...')


    def move_files(self):
        '''
        This moves the files according to setttings
        '''
        answer = tk.messagebox.askyesno('Move files?', 'Are you sure you want to move the files?')
        if answer:
            for folder in self.folders.keys():
                # create folder using sample name
                if ~os.path.isdir(os.path.join(self.cwd, folder)):
                    os.mkdir(os.path.join(self.cwd, folder))

                # move all sample files there
                for file in self.folders[folder]:
                    src = os.path.join(self.cwd, file)
                    dst = os.path.join(self.cwd, folder, file)
                    # print(f'{src} --> {dst}')
                    shutil.move(src, dst)

            # resets all variables
            self.cwd = ''
            self.rawFiles = []
            self.filterList = []
            self.folders = {}
            self.update_boxes()

            # make the move button uavailable
            self.btnMoveFiles['state'] = 'disabled'


if __name__ == '__main__':
    app = Application()

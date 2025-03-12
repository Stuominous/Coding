#SafVaultER
#Automated Backup System
#Fivety-Five Technologies 2025

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import shutil
import os
import threading
import time

class SafVaultER:
    def __init__(self, root):
        self.root = root
        self.root.title("SafVaultER - Automated Backup")
        self.root.geometry("650x700")
        self.root.configure(bg='#222222')
        self.root.resizable(False, False)
        
        # Frame with Border
        self.frame = tk.Frame(root, bg='#333333', bd=3, relief="ridge")
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title Label
        ttk.Label(self.frame, text="SafVaultER", font=("Arial", 22, "bold"), background='#333333', foreground='white').pack(pady=20)
        
        # Frequency Dropdown
        ttk.Label(self.frame, text="Backup Frequency:", font=("Arial", 14, "bold"), background='#333333', foreground='white').pack()
        self.frequency_var = tk.StringVar()
        self.frequency_dropdown = ttk.Combobox(self.frame, textvariable=self.frequency_var, values=["Minutes", "Hours", "Days", "Weeks", "Months", "Years"], state="readonly", width=25)
        self.frequency_dropdown.pack(pady=7)
        
        # Time Entry
        ttk.Label(self.frame, text="Specify Time (e.g., 30 for 30 minutes):", font=("Arial", 14, "bold"), background='#333333', foreground='white').pack()
        self.time_entry = ttk.Entry(self.frame, width=35)
        self.time_entry.pack(pady=7)
        
        # Type of Backup Dropdown
        ttk.Label(self.frame, text="Backup Type:", font=("Arial", 14, "bold"), background='#333333', foreground='white').pack()
        self.type_var = tk.StringVar()
        self.type_dropdown = ttk.Combobox(self.frame, textvariable=self.type_var, values=["Incremental", "Overwrite", "Full"], state="readonly", width=25)
        self.type_dropdown.pack(pady=7)
        
        # Backup Location Dropdown
        ttk.Label(self.frame, text="Backup Location:", font=("Arial", 14, "bold"), background='#333333', foreground='white').pack()
        self.location_var = tk.StringVar()
        self.location_dropdown = ttk.Combobox(self.frame, textvariable=self.location_var, values=["USB", "External Drive", "Server", "Internal Location"], state="readonly", width=25)
        self.location_dropdown.pack(pady=7)
        self.location_dropdown.bind("<<ComboboxSelected>>", self.select_backup_path)
        
        # Path Entry
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.frame, textvariable=self.path_var, state='readonly', width=50)
        self.path_entry.pack(pady=7)
        
        # Browse Button
        self.browse_button = ttk.Button(self.frame, text="Browse", command=self.browse_path)
        self.browse_button.pack(pady=7)
        
        # File Selection
        ttk.Label(self.frame, text="Select Files to Backup:", font=("Arial", 14, "bold"), background='#333333', foreground='white').pack()
        self.files_listbox = tk.Listbox(self.frame, width=55, height=5)
        self.files_listbox.pack(pady=7)
        self.add_file_button = ttk.Button(self.frame, text="Add Files", command=self.add_files)
        self.add_file_button.pack(pady=5)
        
        # Redundant Backup Option
        self.redundant_backup_var = tk.BooleanVar()
        self.redundant_backup_check = ttk.Checkbutton(self.frame, text="Enable Redundant Backup", variable=self.redundant_backup_var, command=self.toggle_redundant_backup)
        self.redundant_backup_check.pack(pady=7)
        
        self.redundant_frame = tk.Frame(self.frame, bg='#444444', bd=2, relief="ridge")
        self.redundant_location_var = tk.StringVar()
        ttk.Label(self.redundant_frame, text="Redundant Backup Location:", background='#444444', foreground='white').pack()
        self.redundant_location_dropdown = ttk.Combobox(self.redundant_frame, textvariable=self.redundant_location_var, values=["USB", "External Drive", "Server", "Internal Location"], state="readonly", width=25)
        self.redundant_location_dropdown.pack(pady=5)
        self.redundant_path_var = tk.StringVar()
        self.redundant_path_entry = ttk.Entry(self.redundant_frame, textvariable=self.redundant_path_var, state='readonly', width=50)
        self.redundant_path_entry.pack(pady=5)
        self.redundant_browse_button = ttk.Button(self.redundant_frame, text="Browse", command=self.browse_redundant_path)
        self.redundant_browse_button.pack(pady=5)
        
        # Start Backup Button
        self.start_button = tk.Button(self.frame, text="Start Backup", command=self.start_backup, font=("Arial", 14, "bold"), bg='#39FF14', fg='black', width=22)
        self.start_button.pack(pady=20)
        
        # Footer Label
        ttk.Label(self.frame, text="Fivety-Five Technologies 2025", font=("Arial", 12, "bold"), background='#333333', foreground='white').pack(pady=10)
    
    def select_backup_path(self, event=None):
        """Updates the path entry field based on the selected backup location."""
        location = self.location_var.get()
        if location in ["USB", "External Drive", "Server", "Internal Location"]:
            self.browse_path()
    
    def browse_path(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_var.set(folder_selected)
    
    def browse_redundant_path(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.redundant_path_var.set(folder_selected)
    
    def add_files(self):
        files = filedialog.askopenfilenames()
        for file in files:
            self.files_listbox.insert(tk.END, file)
    
    def toggle_redundant_backup(self):
        if self.redundant_backup_var.get():
            self.redundant_frame.pack(pady=10)
        else:
            self.redundant_frame.pack_forget()
    
    def start_backup(self):
        messagebox.showinfo("Backup Running", "Backup process started!")
        # Backup logic to be implemented...

if __name__ == "__main__":
    root = tk.Tk()
    app = SafVaultER(root)
    root.mainloop()

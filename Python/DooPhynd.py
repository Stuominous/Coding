#DooPhynd
#!/usr/bin/env python3
# DooPhynd - Duplicate Music File Finder

import os
import hashlib
import threading
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
import struct

class RetroTheme:
    """Theme colors and fonts for retro green screen look"""
    BG_COLOR = "#303030"          # Black background
    TEXT_COLOR = "#13CD13"        # Bright green text
    ACCENT_COLOR = "#00AA00"      # Darker green for accents
    HIGHLIGHT_COLOR = "#CCFFCC"   # Light green for highlights
    FONT_FAMILY = ("VERANDA", 10) # Monospaced font
    HEADING_FONT = ("VERANDA", 12, "bold")

class DooPhynd:
    def __init__(self, root):
        self.root = root
        self.root.title("DooPhynd - Retro Edition")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Apply retro theme to root
        self.root.configure(bg=RetroTheme.BG_COLOR)
        
        # Configure styles
        self.configure_styles()
        
        # Setup the main frame
        main_frame = tk.Frame(root, bg=RetroTheme.BG_COLOR, bd=2, relief="ridge")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title banner
        title_frame = tk.Frame(main_frame, bg=RetroTheme.BG_COLOR)
        title_frame.pack(fill=tk.X, pady=5)
        
        title_label = tk.Label(title_frame, text="◆♪ DOOPHYND v1.0 - MUSIC FILE DUPLICATE FINDER ♪◆", 
                               bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                               font=RetroTheme.HEADING_FONT)
        title_label.pack(pady=5)
        
        # Folder selection
        folder_frame = tk.Frame(main_frame, bg=RetroTheme.BG_COLOR)
        folder_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(folder_frame, text="MUSIC DIR:", bg=RetroTheme.BG_COLOR, 
                 fg=RetroTheme.TEXT_COLOR, font=RetroTheme.FONT_FAMILY).pack(side=tk.LEFT, padx=5)
        
        self.folder_var = tk.StringVar()
        entry = tk.Entry(folder_frame, textvariable=self.folder_var, width=50, 
                         bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR, 
                         insertbackground=RetroTheme.TEXT_COLOR,
                         font=RetroTheme.FONT_FAMILY, relief="sunken")
        entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(folder_frame, text="BROWSE", command=self.browse_folder,
                               bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                               activebackground=RetroTheme.ACCENT_COLOR,
                               activeforeground=RetroTheme.HIGHLIGHT_COLOR,
                               font=RetroTheme.FONT_FAMILY, bd=2, relief="raised")
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Options
        options_frame = tk.LabelFrame(main_frame, text=" SCAN OPTIONS ", bg=RetroTheme.BG_COLOR,
                                     fg=RetroTheme.TEXT_COLOR, font=RetroTheme.FONT_FAMILY)
        options_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.use_metadata = tk.BooleanVar(value=True)
        self.use_hash = tk.BooleanVar(value=True)
        self.music_extensions_var = tk.BooleanVar(value=True)
        
        # Configure checkbutton style
        check_frame1 = tk.Frame(options_frame, bg=RetroTheme.BG_COLOR)
        check_frame1.pack(fill=tk.X, anchor=tk.W)
        
        check1 = tk.Checkbutton(check_frame1, text="FIND BY METADATA (ARTIST/TITLE)", 
                               variable=self.use_metadata, 
                               bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                               selectcolor=RetroTheme.BG_COLOR, 
                               activebackground=RetroTheme.BG_COLOR,
                               activeforeground=RetroTheme.HIGHLIGHT_COLOR,
                               font=RetroTheme.FONT_FAMILY)
        check1.pack(anchor=tk.W)
        
        check_frame2 = tk.Frame(options_frame, bg=RetroTheme.BG_COLOR)
        check_frame2.pack(fill=tk.X, anchor=tk.W)
        
        check2 = tk.Checkbutton(check_frame2, text="FIND BY FILE CONTENT", 
                               variable=self.use_hash,
                               bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                               selectcolor=RetroTheme.BG_COLOR, 
                               activebackground=RetroTheme.BG_COLOR,
                               activeforeground=RetroTheme.HIGHLIGHT_COLOR,
                               font=RetroTheme.FONT_FAMILY)
        check2.pack(anchor=tk.W)
        
        check_frame3 = tk.Frame(options_frame, bg=RetroTheme.BG_COLOR)
        check_frame3.pack(fill=tk.X, anchor=tk.W)
        
        check3 = tk.Checkbutton(check_frame3, text="PROCESS AUDIO FILES ONLY (.MP3, .FLAC, ETC)", 
                               variable=self.music_extensions_var,
                               bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR, 
                               selectcolor=RetroTheme.BG_COLOR,
                               activebackground=RetroTheme.BG_COLOR,
                               activeforeground=RetroTheme.HIGHLIGHT_COLOR,
                               font=RetroTheme.FONT_FAMILY)
        check3.pack(anchor=tk.W)
        
        # Search button
        button_frame = tk.Frame(main_frame, bg=RetroTheme.BG_COLOR)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.search_button = tk.Button(button_frame, text=">> FIND DUPLICATES NOW <<", 
                                     command=self.start_search,
                                     bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                                     activebackground=RetroTheme.ACCENT_COLOR,
                                     activeforeground=RetroTheme.HIGHLIGHT_COLOR,
                                     font=RetroTheme.FONT_FAMILY, bd=2, relief="raised",
                                     padx=10, pady=5)
        self.search_button.pack(pady=5)
        
        # Progress frame
        progress_frame = tk.Frame(main_frame, bg=RetroTheme.BG_COLOR)
        progress_frame.pack(fill=tk.X, pady=5)
        
        # Create a custom progress bar (since ttk ones are harder to theme)
        progress_label = tk.Label(progress_frame, text="PROGRESS:", 
                                 bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                                 font=RetroTheme.FONT_FAMILY)
        progress_label.pack(anchor=tk.W, side=tk.LEFT, padx=5)
        
        self.progress_frame = tk.Frame(progress_frame, bg=RetroTheme.BG_COLOR, bd=1, relief="sunken")
        self.progress_frame.pack(fill=tk.X, expand=True, padx=5)
        
        self.progress_bar = tk.Frame(self.progress_frame, bg=RetroTheme.TEXT_COLOR, width=0, height=20)
        self.progress_bar.pack(side=tk.LEFT, anchor=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_var.trace_add("write", self.update_progress_bar)
        
        self.status_var = tk.StringVar(value="SYSTEM READY")
        status = tk.Label(main_frame, textvariable=self.status_var,
                        bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                        font=RetroTheme.FONT_FAMILY)
        status.pack(anchor=tk.W, pady=2)
        
        # Results notebook
        self.notebook = tk.Frame(main_frame, bg=RetroTheme.BG_COLOR)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Notebook tabs (we'll implement a custom notebook with old-school look)
        tabs_frame = tk.Frame(self.notebook, bg=RetroTheme.BG_COLOR)
        tabs_frame.pack(fill=tk.X)
        
        self.current_tab = tk.StringVar(value="metadata")
        
        # Metadata tab button
        self.metadata_button = tk.Button(tabs_frame, text="METADATA", 
                                       command=lambda: self.show_tab("metadata"),
                                       bg=RetroTheme.ACCENT_COLOR, fg=RetroTheme.HIGHLIGHT_COLOR,
                                       activebackground=RetroTheme.TEXT_COLOR,
                                       activeforeground=RetroTheme.BG_COLOR,
                                       font=RetroTheme.FONT_FAMILY, bd=1, relief="raised")
        self.metadata_button.pack(side=tk.LEFT, padx=2)
        
        # Hash tab button
        self.hash_button = tk.Button(tabs_frame, text="CONTENT", 
                                   command=lambda: self.show_tab("hash"),
                                   bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                                   activebackground=RetroTheme.TEXT_COLOR,
                                   activeforeground=RetroTheme.BG_COLOR,
                                   font=RetroTheme.FONT_FAMILY, bd=1, relief="raised")
        self.hash_button.pack(side=tk.LEFT, padx=2)
        
        # Error tab button
        self.error_button = tk.Button(tabs_frame, text="ERRORS",
                                    command=lambda: self.show_tab("error"),
                                    bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                                    activebackground=RetroTheme.TEXT_COLOR,
                                    activeforeground=RetroTheme.BG_COLOR,
                                    font=RetroTheme.FONT_FAMILY, bd=1, relief="raised")
        self.error_button.pack(side=tk.LEFT, padx=2)
        
        # Content frames
        self.tab_content = tk.Frame(self.notebook, bg=RetroTheme.BG_COLOR, bd=1, relief="sunken")
        self.tab_content.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # Metadata content
        self.metadata_frame = tk.Frame(self.tab_content, bg=RetroTheme.BG_COLOR)
        self.metadata_text = scrolledtext.ScrolledText(self.metadata_frame, wrap=tk.WORD,
                                                     bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                                                     insertbackground=RetroTheme.TEXT_COLOR,
                                                     font=RetroTheme.FONT_FAMILY)
        self.metadata_text.pack(fill=tk.BOTH, expand=True)
        
        # Hash content
        self.hash_frame = tk.Frame(self.tab_content, bg=RetroTheme.BG_COLOR)
        self.hash_text = scrolledtext.ScrolledText(self.hash_frame, wrap=tk.WORD,
                                                 bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                                                 insertbackground=RetroTheme.TEXT_COLOR,
                                                 font=RetroTheme.FONT_FAMILY)
        self.hash_text.pack(fill=tk.BOTH, expand=True)
        
        # Error content
        self.error_frame = tk.Frame(self.tab_content, bg=RetroTheme.BG_COLOR)
        self.error_text = scrolledtext.ScrolledText(self.error_frame, wrap=tk.WORD,
                                                  bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                                                  insertbackground=RetroTheme.TEXT_COLOR,
                                                  font=RetroTheme.FONT_FAMILY)
        self.error_text.pack(fill=tk.BOTH, expand=True)
        
        # Show default tab
        self.show_tab("metadata")
        
        # Add footer
        footer_frame = tk.Frame(main_frame, bg=RetroTheme.BG_COLOR)
        footer_frame.pack(fill=tk.X, pady=5)
        
        footer_text = tk.Label(footer_frame, 
                              text="(C) 2025 - PRESS F1 FOR HELP - ESC TO EXIT",
                              bg=RetroTheme.BG_COLOR, fg=RetroTheme.ACCENT_COLOR,
                              font=RetroTheme.FONT_FAMILY)
        footer_text.pack()
        
        # Initialize variables
        self.metadata_duplicates = {}
        self.hash_duplicates = {}
        self.files_processed = 0
        self.total_files = 0
        self.errors = []
        self.music_extensions = ['.mp3', '.flac', '.m4a', '.mp4', '.wav', '.ogg', '.wma', '.aac']
        
        # Add key bindings
        self.root.bind("<F1>", self.show_help)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
    
    def configure_styles(self):
        """Configure ttk styles for the application"""
        style = ttk.Style()
        style.configure("TFrame", background=RetroTheme.BG_COLOR)
        style.configure("TLabel", background=RetroTheme.BG_COLOR, foreground=RetroTheme.TEXT_COLOR)
        style.configure("TButton", background=RetroTheme.BG_COLOR, foreground=RetroTheme.TEXT_COLOR)
    
    def show_tab(self, tab_name):
        """Switch between tabs"""
        # Hide all frames
        self.metadata_frame.pack_forget()
        self.hash_frame.pack_forget()
        self.error_frame.pack_forget()
        
        # Reset all button colors
        self.metadata_button.config(bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR)
        self.hash_button.config(bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR)
        self.error_button.config(bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR)
        
        # Show selected frame and highlight button
        if tab_name == "metadata":
            self.metadata_frame.pack(fill=tk.BOTH, expand=True)
            self.metadata_button.config(bg=RetroTheme.ACCENT_COLOR, fg=RetroTheme.HIGHLIGHT_COLOR)
        elif tab_name == "hash":
            self.hash_frame.pack(fill=tk.BOTH, expand=True)
            self.hash_button.config(bg=RetroTheme.ACCENT_COLOR, fg=RetroTheme.HIGHLIGHT_COLOR)
        elif tab_name == "error":
            self.error_frame.pack(fill=tk.BOTH, expand=True)
            self.error_button.config(bg=RetroTheme.ACCENT_COLOR, fg=RetroTheme.HIGHLIGHT_COLOR)
    
    def update_progress_bar(self, *args):
        """Update the custom progress bar based on progress_var"""
        progress = self.progress_var.get()
        width = int((self.progress_frame.winfo_width() - 2) * progress / 100)
        self.progress_bar.config(width=width)
        self.root.update_idletasks()
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_var.set(folder_path)
    
    def is_music_file(self, file_path):
        """Check if the file has a music extension."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.music_extensions
    
    def get_metadata(self, file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".mp3":
                try:
                    audio = EasyID3(file_path)
                except mutagen.id3.ID3NoHeaderError:
                    # Try to handle non-ID3 mp3 files
                    self.log_error(f"No ID3 header in {file_path}")
                    return None
            elif ext == ".flac":
                try:
                    audio = FLAC(file_path)
                except:
                    self.log_error(f"Error reading FLAC file {file_path}")
                    return None
            elif ext == ".m4a" or ext == ".mp4":
                try:
                    audio = MP4(file_path)
                except:
                    self.log_error(f"Error reading MP4/M4A file {file_path}")
                    return None
            else:
                return None
            
            # Different files might have different tag structures
            try:
                if ext == ".mp4" or ext == ".m4a":
                    # MP4 has a different tag structure
                    artist = audio.get('\xa9ART', ['Unknown'])[0]
                    title = audio.get('\xa9nam', ['Unknown'])[0]
                    album = audio.get('\xa9alb', ['Unknown'])[0]
                else:
                    # MP3, FLAC, etc
                    artist = audio.get('artist', ['Unknown'])[0]
                    title = audio.get('title', ['Unknown'])[0]
                    album = audio.get('album', ['Unknown'])[0]
            except (struct.error, IndexError) as e:
                # Handle "unpack requires a buffer of 4 bytes" and similar errors
                self.log_error(f"Error unpacking metadata in {file_path}: {e}")
                return None
                
            return artist, title, album
        except Exception as e:
            self.log_error(f"Error processing {file_path}: {str(e)}")
            return None
    
    def get_file_hash(self, file_path):
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'rb') as f:
                try:
                    # Read first 1MB and last 1MB for large files
                    # or the whole file for smaller files
                    if file_size > 2*1024*1024:  # If larger than 2MB
                        first_part = f.read(1024*1024)  # First MB
                        f.seek(-1024*1024, 2)  # Seek to last MB
                        last_part = f.read()
                        return hashlib.md5(first_part + last_part).hexdigest()
                    else:
                        return hashlib.md5(f.read()).hexdigest()
                except (struct.error, OSError) as e:
                    self.log_error(f"Error reading file {file_path}: {e}")
                    return None
        except Exception as e:
            self.log_error(f"Error hashing {file_path}: {str(e)}")
            return None
    
    def log_error(self, message):
        """Log an error message to be displayed later."""
        self.errors.append(message)
        # Also update the status for immediate feedback
        self.update_status(f"ERROR: {message}")
    
    def start_search(self):
        music_folder = self.folder_var.get()
        if not os.path.isdir(music_folder):
            self.update_status("ERROR: PLEASE SELECT A VALID FOLDER")
            return
        
        # Clear previous results
        self.metadata_text.delete(1.0, tk.END)
        self.hash_text.delete(1.0, tk.END)
        self.error_text.delete(1.0, tk.END)
        self.errors = []
        
        # Count total files first (only music files if option is selected)
        self.total_files = 0
        for root, _, files in os.walk(music_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if not self.music_extensions_var.get() or self.is_music_file(file_path):
                    self.total_files += 1
        
        if self.total_files == 0:
            self.update_status("NO FILES TO PROCESS IN SELECTED DIRECTORY")
            return
        
        # Disable search button during processing
        self.search_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.files_processed = 0
        
        # Start search in a separate thread to keep UI responsive
        self.update_status("SCANNING FILES... PLEASE WAIT...")
        threading.Thread(target=self.find_duplicates, args=(music_folder,), daemon=True).start()
    
    def find_duplicates(self, music_folder):
        self.metadata_duplicates = {}
        self.hash_duplicates = {}
        
        try:
            for root, _, files in os.walk(music_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Skip non-music files if option is enabled
                    if self.music_extensions_var.get() and not self.is_music_file(file_path):
                        continue
                    
                    self.update_status(f"SCANNING: {os.path.basename(file_path)}")
                    
                    if self.use_metadata.get():
                        metadata = self.get_metadata(file_path)
                        if metadata:
                            key = (metadata[0].lower(), metadata[1].lower())  # (artist, title)
                            if key in self.metadata_duplicates:
                                self.metadata_duplicates[key].append(file_path)
                            else:
                                self.metadata_duplicates[key] = [file_path]
                    
                    if self.use_hash.get():
                        file_hash = self.get_file_hash(file_path)
                        if file_hash:
                            if file_hash in self.hash_duplicates:
                                self.hash_duplicates[file_hash].append(file_path)
                            else:
                                self.hash_duplicates[file_hash] = [file_path]
                    
                    # Update progress
                    self.files_processed += 1
                    progress = (self.files_processed / self.total_files) * 100
                    self.progress_var.set(progress)
        
            # Filter out non-duplicates
            self.metadata_duplicates = {k: v for k, v in self.metadata_duplicates.items() if len(v) > 1}
            self.hash_duplicates = {k: v for k, v in self.hash_duplicates.items() if len(v) > 1}
            
            # Display results
            self.display_results()
            
            # Re-enable search button
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
            self.update_status(f"SCAN COMPLETE: {self.files_processed} FILES PROCESSED")
        
        except Exception as e:
            self.log_error(f"CRITICAL ERROR: {str(e)}")
            # Re-enable search button
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
            self.update_status("SCAN FAILED - CHECK ERROR LOG")
            self.display_results()  # Display any results collected so far
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_var.set(message))
    
    def display_results(self):
        def update_metadata_text():
            if not self.metadata_duplicates:
                self.metadata_text.insert(tk.END, "╔════════════════════════════════════════╗\n")
                self.metadata_text.insert(tk.END, "║    NO METADATA-BASED DUPLICATES FOUND  ║\n")
                self.metadata_text.insert(tk.END, "╚════════════════════════════════════════╝\n")
                return
            
            self.metadata_text.insert(tk.END, "╔══════════════════════════════════════════════════════════════╗\n")
            self.metadata_text.insert(tk.END, "║                METADATA-BASED DUPLICATES                     ║\n")
            self.metadata_text.insert(tk.END, "╚══════════════════════════════════════════════════════════════╝\n\n")
            
            for i, (key, files) in enumerate(self.metadata_duplicates.items(), 1):
                self.metadata_text.insert(tk.END, f"GROUP #{i}: ARTIST: '{key[0]}', TITLE: '{key[1]}'\n")
                self.metadata_text.insert(tk.END, f"{'─' * 60}\n")
                for j, f in enumerate(files, 1):
                    self.metadata_text.insert(tk.END, f"  {j}. {f}\n") 
                self.metadata_text.insert(tk.END, "\n")
            
            self.metadata_text.insert(tk.END, f"{'═' * 60}\n")
            self.metadata_text.insert(tk.END, f"TOTAL DUPLICATE GROUPS: {len(self.metadata_duplicates)}\n")
        
        def update_hash_text():
            if not self.hash_duplicates:
                self.hash_text.insert(tk.END, "╔════════════════════════════════════════╗\n")
                self.hash_text.insert(tk.END, "║    NO CONTENT-BASED DUPLICATES FOUND   ║\n")
                self.hash_text.insert(tk.END, "╚════════════════════════════════════════╝\n")
                return
            
            self.hash_text.insert(tk.END, "╔══════════════════════════════════════════════════════════════╗\n")
            self.hash_text.insert(tk.END, "║                 CONTENT-BASED DUPLICATES                     ║\n")
            self.hash_text.insert(tk.END, "╚══════════════════════════════════════════════════════════════╝\n\n")
            
            for i, (key, files) in enumerate(self.hash_duplicates.items(), 1):
                self.hash_text.insert(tk.END, f"GROUP #{i}: FILES WITH IDENTICAL CONTENT\n")
                self.hash_text.insert(tk.END, f"{'─' * 60}\n")
                for j, f in enumerate(files, 1):
                    self.hash_text.insert(tk.END, f"  {j}. {f}\n")
                self.hash_text.insert(tk.END, "\n")
            
            self.hash_text.insert(tk.END, f"{'═' * 60}\n")
            self.hash_text.insert(tk.END, f"TOTAL DUPLICATE GROUPS: {len(self.hash_duplicates)}\n")
        
        def update_error_text():
            if not self.errors:
                self.error_text.insert(tk.END, "╔════════════════════════════════════════╗\n")
                self.error_text.insert(tk.END, "║        NO ERRORS DURING SCANNING       ║\n")
                self.error_text.insert(tk.END, "╚════════════════════════════════════════╝\n")
                return
            
            self.error_text.insert(tk.END, "╔══════════════════════════════════════════════════════════════╗\n")
            self.error_text.insert(tk.END, "║                      ERROR LOG                               ║\n")
            self.error_text.insert(tk.END, "╚══════════════════════════════════════════════════════════════╝\n\n")
            
            for i, error in enumerate(self.errors, 1):
                self.error_text.insert(tk.END, f"ERROR #{i}: {error}\n")
            
            self.error_text.insert(tk.END, f"\n{'═' * 60}\n")
            self.error_text.insert(tk.END, f"TOTAL ERRORS: {len(self.errors)}\n")
        
        self.root.after(0, update_metadata_text)
        self.root.after(0, update_hash_text)
        self.root.after(0, update_error_text)
    
    def show_help(self, event=None):
        """Display help information in a new window"""
        help_window = tk.Toplevel(self.root)
        help_window.title("DooPhynd Help")
        help_window.configure(bg=RetroTheme.BG_COLOR)
        help_window.geometry("600x400")
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD,
                                            bg=RetroTheme.BG_COLOR, fg=RetroTheme.TEXT_COLOR,
                                            font=RetroTheme.FONT_FAMILY)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
╔══════════════════════════════════════════════════════╗
║                 DOOPHYND HELP SYSTEM                 ║
╚══════════════════════════════════════════════════════╝

KEYBOARD SHORTCUTS:
  F1    - Show this help screen
  ESC   - Exit application

FINDING DUPLICATES:
  1. Select a music folder using the BROWSE button
  2. Choose your scan options:
     - METADATA: Find duplicates based on Artist/Title
     - CONTENT: Find duplicates based on file content
     - AUDIO ONLY: Only scan audio file types
  3. Click FIND DUPLICATES to begin scan

TABS:
  [METADATA] - Shows duplicates found by Artist/Title
  [CONTENT]  - Shows duplicates found by file content
  [ERRORS]   - Shows any errors encountered during scan

SCAN OPTIONS:
  - METADATA SCAN: Identifies duplicates with same artist and title
  - CONTENT SCAN: Finds files with identical audio content
  - AUDIO FILES ONLY: Limits scan to known music file types

TIPS:
  - Ensure you have read/write permissions to the selected folder
  - Large music libraries may take some time to process
  - Use both metadata and content scans for thorough duplicate detection

(C) 2025 DooPhynd - DUPLICATE MUSIC FILE FINDER
        """
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)  # Make read-only
        
def main():
    """Main entry point for the DooPhynd application"""
    # Create the main Tkinter root window
    root = tk.Tk()
    
    # Initialize the application
    app = DooPhynd(root)
    
    # Start the Tkinter event loop
    root.mainloop()

# Ensure the script can be run directly or imported
if __name__ == "__main__":
    main()

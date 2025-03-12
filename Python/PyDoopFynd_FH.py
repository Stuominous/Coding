#PyDoopFynd_FH
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

class DuplicateMusicFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Music Finder")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Setup the main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Folder selection
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(folder_frame, text="Music Folder:").pack(side=tk.LEFT, padx=5)
        
        self.folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.folder_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(folder_frame, text="Browse...", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.pack(fill=tk.X, pady=5)
        
        self.use_metadata = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Find duplicates by metadata (artist, title)", 
                        variable=self.use_metadata).pack(anchor=tk.W)
        
        self.use_hash = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Find duplicates by file content", 
                        variable=self.use_hash).pack(anchor=tk.W)
        
        self.music_extensions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Only process music files (.mp3, .flac, .m4a, etc.)", 
                        variable=self.music_extensions_var).pack(anchor=tk.W)
        
        # Search button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.search_button = ttk.Button(button_frame, text="Find Duplicates", command=self.start_search)
        self.search_button.pack(pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).pack(anchor=tk.W, pady=2)
        
        # Results with tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tab for metadata duplicates
        self.metadata_tab = ttk.Frame(notebook)
        notebook.add(self.metadata_tab, text="Metadata Duplicates")
        
        self.metadata_text = scrolledtext.ScrolledText(self.metadata_tab, wrap=tk.WORD)
        self.metadata_text.pack(fill=tk.BOTH, expand=True)
        
        # Tab for hash duplicates
        self.hash_tab = ttk.Frame(notebook)
        notebook.add(self.hash_tab, text="Content Duplicates")
        
        self.hash_text = scrolledtext.ScrolledText(self.hash_tab, wrap=tk.WORD)
        self.hash_text.pack(fill=tk.BOTH, expand=True)
        
        # Tab for errors
        self.error_tab = ttk.Frame(notebook)
        notebook.add(self.error_tab, text="Errors")
        
        self.error_text = scrolledtext.ScrolledText(self.error_tab, wrap=tk.WORD)
        self.error_text.pack(fill=tk.BOTH, expand=True)
        
        # Initialize variables
        self.metadata_duplicates = {}
        self.hash_duplicates = {}
        self.files_processed = 0
        self.total_files = 0
        self.errors = []
        self.music_extensions = ['.mp3', '.flac', '.m4a', '.mp4', '.wav', '.ogg', '.wma', '.aac']
    
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
        self.update_status(f"Error: {message}")
    
    def start_search(self):
        music_folder = self.folder_var.get()
        if not os.path.isdir(music_folder):
            self.update_status("Please select a valid folder")
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
            self.update_status("No files to process in the selected folder")
            return
        
        # Disable search button during processing
        self.search_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.files_processed = 0
        
        # Start search in a separate thread to keep UI responsive
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
                    
                    self.update_status(f"Processing: {os.path.basename(file_path)}")
                    
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
                    self.update_progress(progress)
        
            # Filter out non-duplicates
            self.metadata_duplicates = {k: v for k, v in self.metadata_duplicates.items() if len(v) > 1}
            self.hash_duplicates = {k: v for k, v in self.hash_duplicates.items() if len(v) > 1}
            
            # Display results
            self.display_results()
            
            # Re-enable search button
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
            self.update_status(f"Search completed. Processed {self.files_processed} files.")
        
        except Exception as e:
            self.log_error(f"Critical error during search: {str(e)}")
            # Re-enable search button
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
            self.update_status("Search failed due to an error")
            self.display_results()  # Display any results collected so far
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_var.set(message))
    
    def update_progress(self, value):
        self.root.after(0, lambda: self.progress_var.set(value))
    
    def display_results(self):
        def update_metadata_text():
            if not self.metadata_duplicates:
                self.metadata_text.insert(tk.END, "No metadata-based duplicates found.\n")
                return
            
            for key, files in self.metadata_duplicates.items():
                self.metadata_text.insert(tk.END, f"\nDuplicate: Artist: {key[0]}, Title: {key[1]}\n")
                for f in files:
                    self.metadata_text.insert(tk.END, f"  • {f}\n")
            
            self.metadata_text.insert(tk.END, f"\nTotal metadata-based duplicate groups: {len(self.metadata_duplicates)}\n")
        
        def update_hash_text():
            if not self.hash_duplicates:
                self.hash_text.insert(tk.END, "No content-based duplicates found.\n")
                return
            
            for key, files in self.hash_duplicates.items():
                self.hash_text.insert(tk.END, f"\nDuplicate files with identical content:\n")
                for f in files:
                    self.hash_text.insert(tk.END, f"  • {f}\n")
            
            self.hash_text.insert(tk.END, f"\nTotal content-based duplicate groups: {len(self.hash_duplicates)}\n")
        
        def update_error_text():
            if not self.errors:
                self.error_text.insert(tk.END, "No errors encountered during processing.\n")
                return
            
            self.error_text.insert(tk.END, f"Encountered {len(self.errors)} errors during processing:\n\n")
            for i, error in enumerate(self.errors, 1):
                self.error_text.insert(tk.END, f"{i}. {error}\n")
        
        self.root.after(0, update_metadata_text)
        self.root.after(0, update_hash_text)
        self.root.after(0, update_error_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateMusicFinder(root)
    root.mainloop()
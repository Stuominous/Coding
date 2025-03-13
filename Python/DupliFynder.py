#DupliFynder.py
#A simple duplicate file finder application using PyQt6 and hashlib.

import sys
import os
import hashlib
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar, QStatusBar, QHBoxLayout, QGridLayout, QFrame, QInputDialog, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

class DupliFynder(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Set up the main window
        self.setWindowTitle("DupliFynder")
        self.setGeometry(100, 100, 600, 600)
        self.setStyleSheet("background-color: #1d1d1f; color: white;")
        
        layout = QVBoxLayout()
        
        # Directory selection section
        self.label = QLabel("Select a directory to scan for duplicate files:")
        self.label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.label)
        
        self.selectButton = QPushButton("Select Folder")
        self.selectButton.setFont(QFont("Arial", 9, QFont.Weight.Bold))  # 10% smaller
        self.selectButton.setStyleSheet("background-color: #2980B9; color: white; padding: 9px; border: 2px solid #3498DB; border-radius: 5px;")  # 10% smaller padding
        self.selectButton.clicked.connect(self.selectFolder)
        layout.addWidget(self.selectButton)
        
        # File type selection section
        self.fileTypeLabel = QLabel("What type of files are included in the search?")
        self.fileTypeLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.fileTypeLabel)
        
        self.addFileTypeButtons(layout, "Include")
        
        self.addFileTypeButton = QPushButton("Add Other File Type")
        self.addFileTypeButton.setFont(QFont("Arial", 9, QFont.Weight.Bold))  # 10% smaller
        self.addFileTypeButton.setStyleSheet("background-color: #2980B9; color: white; padding: 9px; border: 2px solid #3498DB; border-radius: 5px;")  # 10% smaller padding
        self.addFileTypeButton.clicked.connect(lambda: self.addOtherFileType("Include"))
        layout.addWidget(self.addFileTypeButton)
        
        # Exclude file types section
        self.excludeFileTypeLabel = QLabel("What type of files are excluded from the search?")
        self.excludeFileTypeLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.excludeFileTypeLabel)
        
        self.addFileTypeButtons(layout, "Exclude")
        
        self.addExcludeFileTypeButton = QPushButton("Add Other File Type")
        self.addExcludeFileTypeButton.setFont(QFont("Arial", 9, QFont.Weight.Bold))  # 10% smaller
        self.addExcludeFileTypeButton.setStyleSheet("background-color: #5d3939; color: white; padding: 9px; border: 2px solid #4b2e2e; border-radius: 5px;")  # 10% smaller padding
        self.addExcludeFileTypeButton.clicked.connect(lambda: self.addOtherFileType("Exclude"))
        layout.addWidget(self.addExcludeFileTypeButton)
        
        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Scan button section
        self.scanButton = QPushButton("Scan for Duplicates")
        self.scanButton.setFont(QFont("Arial", 9, QFont.Weight.Bold))  # 10% smaller
        self.scanButton.setStyleSheet("background-color: #E67E22; color: white; padding: 9px; border: 2px solid #D35400; border-radius: 5px;")  # 10% smaller padding
        self.scanButton.clicked.connect(self.scanDuplicates)
        layout.addWidget(self.scanButton)
        
        # Tag message
        self.tagMessage = QLabel("*if no file types are selected, then all duplicates will be found!")
        tagFont = QFont("Arial", 9)  # 10% smaller
        tagFont.setItalic(True)
        self.tagMessage.setFont(tagFont)
        self.tagMessage.setStyleSheet("color: #FFFFFF;")
        self.tagMessage.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.tagMessage)
        
        # Progress bar section
        self.progressBar = QProgressBar()
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progressBar)
        
        # Results display section
        self.resultText = QTextEdit()
        self.resultText.setReadOnly(True)
        self.resultText.setStyleSheet("background-color: #34495E; color: white; border: 2px solid #3498DB; border-radius: 5px;")
        layout.addWidget(self.resultText)
        
        # Export button section
        self.exportButton = QPushButton("Export Report to Excel")
        self.exportButton.setFont(QFont("Arial", 9, QFont.Weight.Bold))  # 10% smaller
        self.exportButton.setStyleSheet("background-color: #2980B9; color: white; padding: 9px; border: 2px solid #3498DB; border-radius: 5px;")  # 10% smaller padding
        self.exportButton.clicked.connect(self.exportReport)
        self.exportButton.setEnabled(False)
        layout.addWidget(self.exportButton)
        
        # Status bar section
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("background-color: #2980B9; color: white;")
        layout.addWidget(self.statusBar)
        
        self.setLayout(layout)
        
        self.folderPath = ""
        self.duplicates = []
        self.searchEntireDir = False
    
    def addFileTypeButtons(self, layout, mode):
        # Define file type buttons
        self.fileTypes = {
            ".jpg": QPushButton(".jpg"),
            ".jpeg": QPushButton(".jpeg"),
            ".png": QPushButton(".png"),
            ".gif": QPushButton(".gif"),
            ".bmp": QPushButton(".bmp"),
            ".mp3": QPushButton(".mp3"),
            ".wav": QPushButton(".wav"),
            ".flac": QPushButton(".flac"),
            ".m4a": QPushButton(".m4a"),
            ".tif": QPushButton(".tif"),
            ".tiff": QPushButton(".tiff"),
            ".ogg": QPushButton(".ogg"),
            ".doc": QPushButton(".doc"),
            ".docx": QPushButton(".docx"),
            ".xls": QPushButton(".xls"),
            ".xlsx": QPushButton(".xlsx"),
            ".ppt": QPushButton(".ppt"),
            ".pptx": QPushButton(".pptx"),
            ".pdf": QPushButton(".pdf"),
            ".txt": QPushButton(".txt"),
            ".zip": QPushButton(".zip"),
            ".rar": QPushButton(".rar"),
            ".7z": QPushButton(".7z"),
            ".tar": QPushButton(".tar"),
            ".gz": QPushButton(".gz")
        }
        
        # Layout for file type buttons
        self.fileTypeLayout = QGridLayout()
        row, col = 0, 0
        for ext, button in self.fileTypes.items():
            button.setCheckable(True)
            button.setFont(QFont("Arial", 9, QFont.Weight.Bold))  # 10% smaller
            if mode == "Include":
                button.setStyleSheet("background-color: #848383; color: white; padding: 4.41px; border: 2px solid #0c0c0b; border-radius: 5px;")  # 12% smaller padding
                button.clicked.connect(lambda checked, btn=button: self.toggleButton(btn, "Include"))
            else:
                button.setStyleSheet("background-color: #5d3939; color: white; padding: 4.41px; border: 2px solid #4b2e2e; border-radius: 5px;")  # 12% smaller padding
                button.clicked.connect(lambda checked, btn=button: self.toggleButton(btn, "Exclude"))
            self.fileTypeLayout.addWidget(button, row, col)
            col += 1
            if col == 6:
                col = 0
                row += 1
        
        layout.addLayout(self.fileTypeLayout)
    
    def toggleButton(self, button, mode):
        # Toggle button style on selection
        if button.isChecked():
            if mode == "Include":
                button.setStyleSheet("background-color: #39FF14; color: black; padding: 4.41px; border: 2px solid #39FF14; border-radius: 5px;")  # 12% smaller padding
            else:
                button.setStyleSheet("background-color: red; color: black; padding: 4.41px; border: 2px solid #4b2e2e; border-radius: 5px;")  # 12% smaller padding
        else:
            if mode == "Include":
                button.setStyleSheet("background-color: #848383; color: white; padding: 4.41px; border: 2px solid #0c0c0b; border-radius: 5px;")  # 12% smaller padding
            else:
                button.setStyleSheet("background-color: #5d3939; color: white; padding: 4.41px; border: 2px solid #4b2e2e; border-radius: 5px;")  # 12% smaller padding
    
    def addOtherFileType(self, mode):
        # Add other file type button
        text, ok = QInputDialog.getText(self, 'Add File Type', 'Enter file extension (e.g., .txt):')
        if ok and text:
            if not text.startswith('.'):
                text = '.' + text
            if text not in self.fileTypes:
                button = QPushButton(text)
                button.setCheckable(True)
                button.setFont(QFont("Arial", 9, QFont.Weight.Bold))  # 10% smaller
                if mode == "Include":
                    button.setStyleSheet("background-color: #848383; color: white; padding: 4.41px; border: 2px solid #0c0c0b; border-radius: 5px;")  # 12% smaller padding
                    button.clicked.connect(lambda checked, btn=button: self.toggleButton(btn, "Include"))
                else:
                    button.setStyleSheet("background-color: #5d3939; color: white; padding: 4.41px; border: 2px solid #4b2e2e; border-radius: 5px;")  # 12% smaller padding
                    button.clicked.connect(lambda checked, btn=button: self.toggleButton(btn, "Exclude"))
                self.fileTypes[text] = button
                row = self.fileTypeLayout.rowCount()
                col = self.fileTypeLayout.columnCount()
                if col == 6:
                    col = 0
                    row += 1
                self.fileTypeLayout.addWidget(button, row, col)
    
    def selectFolder(self):
        # Select folder dialog
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folderPath = folder
            self.resultText.setText(f"Selected Folder: {folder}")
    
    def scanDuplicates(self):
        # Scan for duplicate files
        if not self.folderPath:
            self.resultText.setText("Please select a folder first.")
            return
        
        file_hashes = {}
        self.duplicates = []
        
        file_list = []
        for root, _, files in os.walk(self.folderPath):
            for file in files:
                file_path = os.path.join(root, file)
                if not self.is_excluded_file(file) and self.is_included_file(file):
                    file_list.append(file_path)
        
        total_files = len(file_list)
        self.progressBar.setMaximum(total_files)
        
        for idx, file_path in enumerate(file_list, 1):
            file_hash = self.hash_file(file_path)
            if file_hash in file_hashes:
                file_hashes[file_hash].append(file_path)
            else:
                file_hashes[file_hash] = [file_path]
            self.progressBar.setValue(idx)
            self.statusBar.showMessage(f"Scanning file {idx} of {total_files}")
        
        for paths in file_hashes.values():
            if len(paths) > 1:
                self.duplicates.append(paths)
        
        self.displayResults()
    
    def hash_file(self, file_path, chunk_size=8192):
        # Generate hash for a file
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
        except Exception as e:
            return None
        return hasher.hexdigest()
    
    def is_excluded_file(self, filename):
        # Check if file is excluded based on selected file types
        for ext, button in self.fileTypes.items():
            if filename.lower().endswith(ext) and button.isChecked():
                return True
        return False
    
    def is_included_file(self, filename):
        # Check if file is included based on selected file types
        for ext, button in self.fileTypes.items():
            if filename.lower().endswith(ext) and button.isChecked():
                return True
        return False
    
    def displayResults(self):
        # Display scan results
        if not self.duplicates:
            self.resultText.setText("No duplicates found.")
            self.statusBar.showMessage("Scan complete. No duplicates found.")
            return
        
        result_str = "Duplicate Files Found:\n\n"
        for group in self.duplicates:
            result_str += "\n".join(group) + "\n\n"
        self.resultText.setText(result_str)
        self.exportButton.setEnabled(True)
        self.statusBar.showMessage("Scan complete. Duplicates found.")
    
    def exportReport(self):
        # Export scan results to Excel
        if not self.duplicates:
            return
        
        data = []
        for group in self.duplicates:
            for file in group:
                file_stats = os.stat(file)
                data.append({
                    "Path": file,
                    "Name": os.path.basename(file),
                    "Type": os.path.splitext(file)[1],
                    "Size (bytes)": file_stats.st_size,
                    "Timestamp": file_stats.st_mtime,
                })
        
        df = pd.DataFrame(data)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"DupliFyndReport_{now}.xlsx"
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Report", default_filename, "Excel Files (*.xlsx)")
        if save_path:
            df.to_excel(save_path, index=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DupliFynder()
    window.show()
    sys.exit(app.exec())

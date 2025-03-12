#DupliFynder.py
#A simple duplicate file finder application using PyQt6 and hashlib.

import sys
import os
import hashlib
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar, QStatusBar
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class DupliFynder(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("DupliFynder")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("background-color: #555555; color: white;")
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Select a directory to scan for duplicate files:")
        self.label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.label)
        
        self.selectButton = QPushButton("Select Folder")
        self.selectButton.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.selectButton.setStyleSheet("background-color: #23272A; color: white; padding: 10px;")
        self.selectButton.clicked.connect(self.selectFolder)
        layout.addWidget(self.selectButton)
        
        self.scanButton = QPushButton("Scan for Duplicates")
        self.scanButton.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.scanButton.setStyleSheet("background-color: #23272A; color: white; padding: 10px;")
        self.scanButton.clicked.connect(self.scanDuplicates)
        layout.addWidget(self.scanButton)
        
        self.progressBar = QProgressBar()
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progressBar)
        
        self.resultText = QTextEdit()
        self.resultText.setReadOnly(True)
        layout.addWidget(self.resultText)
        
        self.exportButton = QPushButton("Export Report to Excel")
        self.exportButton.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.exportButton.setStyleSheet("background-color: #23272A; color: white; padding: 10px;")
        self.exportButton.clicked.connect(self.exportReport)
        self.exportButton.setEnabled(False)
        layout.addWidget(self.exportButton)
        
        self.statusBar = QStatusBar()
        layout.addWidget(self.statusBar)
        
        self.setLayout(layout)
        
        self.folderPath = ""
        self.duplicates = []
    
    def selectFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folderPath = folder
            self.resultText.setText(f"Selected Folder: {folder}")
    
    def scanDuplicates(self):
        if not self.folderPath:
            self.resultText.setText("Please select a folder first.")
            return
        
        file_hashes = {}
        self.duplicates = []
        
        file_list = []
        for root, _, files in os.walk(self.folderPath):
            for file in files:
                file_path = os.path.join(root, file)
                if not self.is_excluded_file(file):
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
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
        except Exception as e:
            return None
        return hasher.hexdigest()
    
    def is_excluded_file(self, filename):
        excluded_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp3", ".wav", ".flac", ".m4a", ".tif", ".tiff", ".ogg"}
        return any(filename.lower().endswith(ext) for ext in excluded_extensions)
    
    def displayResults(self):
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
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "duplicate_report.xlsx", "Excel Files (*.xlsx)")
        if save_path:
            df.to_excel(save_path, index=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DupliFynder()
    window.show()
    sys.exit(app.exec())

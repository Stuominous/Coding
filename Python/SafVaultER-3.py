#SafVaultER-3.py
#SafVaultER - Automated Backup Tool
#Author: Fivety-Five Technologies

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QListWidget, QCheckBox, QFileDialog, QMessageBox, QFrame, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class SafVaultER(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("SafVaultER - Automated Backup")
        self.setGeometry(100, 100, 650, 700)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Frame with Border
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: #34495e; border: 3px solid #1abc9c; border-radius: 10px;")
        layout.addWidget(self.frame)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)
        
        # Title Label
        title_label = QLabel("SafVaultER", self.frame)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # Frequency Dropdown
        freq_label = QLabel("Backup Frequency:", self.frame)
        freq_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        frame_layout.addWidget(freq_label)
        
        self.frequency_dropdown = QComboBox(self.frame)
        self.frequency_dropdown.addItems(["Minutes", "Hours", "Days", "Weeks", "Months", "Years"])
        self.frequency_dropdown.setStyleSheet("background-color: #1abc9c; color: white; padding: 5px; border-radius: 5px;")
        frame_layout.addWidget(self.frequency_dropdown)
        
        # Time Entry
        time_label = QLabel("Specify Time (e.g., 30 for 30 minutes):", self.frame)
        time_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        frame_layout.addWidget(time_label)
        
        self.time_entry = QLineEdit(self.frame)
        self.time_entry.setStyleSheet("background-color: #1abc9c; color: white; padding: 5px; border-radius: 5px;")
        frame_layout.addWidget(self.time_entry)
        
        # Type of Backup Dropdown
        type_label = QLabel("Backup Type:", self.frame)
        type_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        frame_layout.addWidget(type_label)
        
        self.type_dropdown = QComboBox(self.frame)
        self.type_dropdown.addItems(["Incremental", "Overwrite", "Full"])
        self.type_dropdown.setStyleSheet("background-color: #1abc9c; color: white; padding: 5px; border-radius: 5px;")
        frame_layout.addWidget(self.type_dropdown)
        
        # Backup Location Dropdown
        location_label = QLabel("Backup Location:", self.frame)
        location_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        frame_layout.addWidget(location_label)
        
        self.location_dropdown = QComboBox(self.frame)
        self.location_dropdown.addItems(["USB", "External Drive", "Server", "Internal Location"])
        self.location_dropdown.setStyleSheet("background-color: #1abc9c; color: white; padding: 5px; border-radius: 5px;")
        self.location_dropdown.currentIndexChanged.connect(self.select_backup_path)
        frame_layout.addWidget(self.location_dropdown)
        
        # Path Entry
        path_layout = QHBoxLayout()
        self.path_entry = QLineEdit(self.frame)
        self.path_entry.setReadOnly(True)
        self.path_entry.setStyleSheet("background-color: #1abc9c; color: white; padding: 5px; border-radius: 5px;")
        path_layout.addWidget(self.path_entry)
        
        # Browse Button
        self.browse_button = QPushButton("Browse", self.frame)
        self.browse_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px; border-radius: 5px;")
        self.browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.browse_button)
        
        frame_layout.addLayout(path_layout)
        
        # File Selection
        file_label = QLabel("Select Files to Backup:", self.frame)
        file_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        frame_layout.addWidget(file_label)
        
        self.files_listbox = QListWidget(self.frame)
        self.files_listbox.setStyleSheet("background-color: #1abc9c; color: white; padding: 5px; border-radius: 5px;")
        frame_layout.addWidget(self.files_listbox)
        
        self.add_file_button = QPushButton("Add Files", self.frame)
        self.add_file_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px; border-radius: 5px;")
        self.add_file_button.clicked.connect(self.add_files)
        frame_layout.addWidget(self.add_file_button)
        
        # Redundant Backup Option
        self.redundant_backup_check = QCheckBox("Enable Redundant Backup", self.frame)
        self.redundant_backup_check.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.redundant_backup_check.stateChanged.connect(self.toggle_redundant_backup)
        frame_layout.addWidget(self.redundant_backup_check)
        
        self.redundant_frame = QFrame(self.frame)
        self.redundant_frame.setStyleSheet("background-color: #444444; border: 2px solid #1abc9c; border-radius: 5px;")
        redundant_layout = QVBoxLayout(self.redundant_frame)
        
        redundant_location_label = QLabel("Redundant Backup Location:", self.redundant_frame)
        redundant_location_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        redundant_layout.addWidget(redundant_location_label)
        
        self.redundant_location_dropdown = QComboBox(self.redundant_frame)
        self.redundant_location_dropdown.addItems(["USB", "External Drive", "Server", "Internal Location"])
        self.redundant_location_dropdown.setStyleSheet("background-color: #1abc9c; color: white; padding: 5px; border-radius: 5px;")
        redundant_layout.addWidget(self.redundant_location_dropdown)
        
        redundant_path_layout = QHBoxLayout()
        self.redundant_path_entry = QLineEdit(self.redundant_frame)
        self.redundant_path_entry.setReadOnly(True)
        self.redundant_path_entry.setStyleSheet("background-color: #1abc9c; color: white; padding: 5px; border-radius: 5px;")
        redundant_path_layout.addWidget(self.redundant_path_entry)
        
        self.redundant_browse_button = QPushButton("Browse", self.redundant_frame)
        self.redundant_browse_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px; border-radius: 5px;")
        self.redundant_browse_button.clicked.connect(self.browse_redundant_path)
        redundant_path_layout.addWidget(self.redundant_browse_button)
        
        redundant_layout.addLayout(redundant_path_layout)
        
        frame_layout.addWidget(self.redundant_frame)
        self.redundant_frame.hide()
        
        # Start Backup Button
        self.start_button = QPushButton("Start Backup", self.frame)
        self.start_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.start_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px;")
        self.start_button.clicked.connect(self.start_backup)
        frame_layout.addWidget(self.start_button)
        
        # Footer Label
        footer_label = QLabel("Fivety-Five Technologies 2025", self.frame)
        footer_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(footer_label)
        
        self.setLayout(layout)
    
    def select_backup_path(self):
        location = self.location_dropdown.currentText()
        if location in ["USB", "External Drive", "Server", "Internal Location"]:
            self.browse_path()
    
    def browse_path(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_selected:
            self.path_entry.setText(folder_selected)
    
    def browse_redundant_path(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_selected:
            self.redundant_path_entry.setText(folder_selected)
    
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        for file in files:
            self.files_listbox.addItem(file)
    
    def toggle_redundant_backup(self):
        if self.redundant_backup_check.isChecked():
            self.redundant_frame.show()
        else:
            self.redundant_frame.hide()
    
    def start_backup(self):
        QMessageBox.information(self, "Backup Running", "Backup process started!")
        # Backup logic to be implemented...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SafVaultER()
    window.show()
    sys.exit(app.exec())
#backupperer

import os
import shutil
import time
import schedule
import logging
from datetime import datetime
import platform
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backup_log.txt"),
        logging.StreamHandler()
    ]
)

class BackupManager:
    def __init__(self, source_paths, backup_destination, interval_hours=24, is_usb=True):
        """
        Initialize the backup manager
        
        Args:
            source_paths (list): List of file/folder paths to backup
            backup_destination (str): Path to backup destination
            interval_hours (int): Backup interval in hours
            is_usb (bool): Whether the destination is a USB drive
        """
        self.source_paths = source_paths
        self.backup_destination = backup_destination
        self.interval_hours = interval_hours
        self.is_usb = is_usb
        
    def is_destination_available(self):
        """Check if backup destination is available"""
        # First check if path exists
        if not os.path.exists(self.backup_destination):
            return False
            
        # If USB drive check is enabled, verify it's a removable drive
        if self.is_usb:
            # Different methods depending on the operating system
            if platform.system() == "Windows":
                try:
                    drive_letter = os.path.splitdrive(self.backup_destination)[0]
                    if drive_letter:
                        for part in psutil.disk_partitions():
                            if part.device.startswith(drive_letter) and "removable" in part.opts.lower():
                                return True
                        return False
                    return False
                except:
                    return False
            elif platform.system() == "Linux":
                # Get mount point containing the backup destination
                backup_path = os.path.abspath(self.backup_destination)
                try:
                    for part in psutil.disk_partitions():
                        if backup_path.startswith(part.mountpoint):
                            # Check if it's a USB drive (typically /dev/sd*)
                            return "/dev/sd" in part.device
                    return False
                except:
                    return False
            elif platform.system() == "Darwin":  # macOS
                # Basic check for external volumes on macOS
                return "/Volumes/" in os.path.abspath(self.backup_destination)
        
        # If not checking for USB or on unsupported OS, just verify we can write to it
        try:
            test_file = os.path.join(self.backup_destination, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except:
            return False
    
    def perform_backup(self):
        """Perform the backup operation"""
        if not self.is_destination_available():
            logging.warning(f"Backup destination {self.backup_destination} is not available")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(self.backup_destination, f"backup_{timestamp}")
        
        try:
            # Create backup directory
            os.makedirs(backup_folder, exist_ok=True)
            
            # Copy each source to the backup folder
            for source_path in self.source_paths:
                if not os.path.exists(source_path):
                    logging.warning(f"Source path {source_path} does not exist, skipping")
                    continue
                
                filename = os.path.basename(source_path)
                destination = os.path.join(backup_folder, filename)
                
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, destination)
                    logging.info(f"Backed up directory {source_path} to {destination}")
                else:
                    shutil.copy2(source_path, destination)
                    logging.info(f"Backed up file {source_path} to {destination}")
            
            logging.info(f"Backup completed successfully to {backup_folder}")
            return True
        except Exception as e:
            logging.error(f"Backup failed: {str(e)}")
            return False
    
    def start_scheduled_backup(self):
        """Start the scheduled backup process"""
        logging.info(f"Scheduled backup every {self.interval_hours} hours")
        
        # Schedule the backup job
        schedule.every(self.interval_hours).hours.do(self.perform_backup)
        
        # Run backup immediately on start
        self.perform_backup()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for pending tasks

def main():
    # Example configuration - customize these values
    source_paths = [
        "C:/path/to/important/file.txt",  # Update this path
        "C:/path/to/important/folder"     # Update this path
    ]
    
    backup_destination = "E:/backups"  # Update this path for Windows
    # backup_destination = "/media/usb_drive/backups"  # For Linux
    # backup_destination = "/Volumes/MY_USB/backups"  # For macOS
    
    interval_hours = 24  # Backup every 24 hours
    is_usb = True  # Set to False if backing up to a network or local drive
    
    # Log the configuration
    logging.info(f"Source paths: {source_paths}")
    logging.info(f"Backup destination: {backup_destination}")
    logging.info(f"Interval hours: {interval_hours}")
    logging.info(f"Is USB: {is_usb}")
    
    # Create and start the backup manager
    try:
        backup_manager = BackupManager(
            source_paths=source_paths,
            backup_destination=backup_destination,
            interval_hours=interval_hours,
            is_usb=is_usb
        )
        logging.info("BackupManager initialized successfully")
        
        backup_manager.start_scheduled_backup()
    except Exception as e:
        logging.error(f"Failed to initialize BackupManager: {str(e)}")

if __name__ == "__main__":
    main()
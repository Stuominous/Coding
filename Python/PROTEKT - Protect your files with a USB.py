#PROTEKT - Protect your files with a USB key    
#PROTEKT is a simple Python script that allows you to protect your files by granting or denying access to specific folders based on the presence of an authorized USB drive. If the authorized USB is plugged in, the script will grant access to the secure folders. If the USB is not detected, access will be denied. This is a great way to secure your files and prevent unauthorized access to sensitive data.


import os
import platform
import subprocess

# CONFIGURATION
AUTHORIZED_USB_ID = "1234-ABCD"  # Replace with your USB drive's UUID or Volume Serial Number
SECURE_FOLDERS = [  
    r"C:\SecureFolder1",  
    r"C:\SecureFolder2",  
    r"D:\AnotherSecureFolder"  # Add as many folders as needed  
]

def get_usb_id():
    """Check if the authorized USB is plugged in."""
    system = platform.system()
    
    if system == "Windows":
        try:
            output = subprocess.check_output("wmic logicaldisk get volumename,serialnumber", shell=True).decode()
            for line in output.split("\n"):
                if AUTHORIZED_USB_ID in line:
                    return True
        except Exception:
            return False

    elif system == "Linux":
        try:
            output = subprocess.check_output("lsblk -o UUID,MOUNTPOINT", shell=True).decode()
            for line in output.split("\n"):
                if AUTHORIZED_USB_ID in line:
                    return True
        except Exception:
            return False

    return False

def set_folder_permissions(allow_access):
    """Grant or deny access to all secure folders."""
    for folder in SECURE_FOLDERS:
        if os.path.exists(folder):
            if platform.system() == "Windows":
                acl_command = f'icacls "{folder}" /deny Everyone:(OI)(CI)F' if not allow_access else f'icacls "{folder}" /grant Everyone:(OI)(CI)F'
            else:
                chmod_command = f"chmod 000 '{folder}'" if not allow_access else f"chmod 700 '{folder}'"
                acl_command = chmod_command
            
            os.system(acl_command)

def main():
    if get_usb_id():
        print("Authorized USB detected! Granting access to folders...")
        set_folder_permissions(True)
    else:
        print("No authorized USB found. Denying access to folders...")
        set_folder_permissions(False)

if __name__ == "__main__":
    main()

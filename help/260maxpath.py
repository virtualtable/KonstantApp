import os
import winreg

def enable_long_paths():
    try:
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r'SYSTEM\CurrentControlSet\Control\FileSystem',
            0,
            winreg.KEY_SET_VALUE
        )
        
        # Set the LongPathsEnabled value to 1
        winreg.SetValueEx(reg_key, 'LongPathsEnabled', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(reg_key)
        
        print("Successfully enabled long path support. Please restart your computer for the changes to take effect.")
    except PermissionError:
        print("Permission denied. Please run this script as an administrator.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    enable_long_paths()

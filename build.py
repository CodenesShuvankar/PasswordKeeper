"""
Build script for creating Windows executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def get_folder_size(folder_path):
    """Calculate folder size in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
    return total_size / (1024 * 1024)  # Convert to MB

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    print("Cleanup complete.\n")

def build_executable():
    """Build executable using PyInstaller for portable deployment"""
    print("Building portable executable with PyInstaller...")
    
    # PyInstaller command for portable application
    cmd = [
        'python', '-m', 'PyInstaller',
        '--onedir',                     # Create directory (not single file for better portability)
        '--windowed',                   # No console window
        '--name=PasswordKeeper',        # Executable name
        '--distpath=dist',              # Output directory
        '--workpath=build',             # Work directory
        '--specpath=build',             # Spec file location
        '--clean',                      # Clean cache
        '--noconfirm',                  # Overwrite without asking
        '--noupx',                      # Don't use UPX (better compatibility)
        '--console',                    # Enable console for debugging (remove for final)
        # Optional icon (uncomment if you have an icon)
        # '--icon=resources/icon.ico',
        'main.py'                       # Main script
    ]
    
    # Add data files (if any exist)
    # data_files = [
    #     '--add-data=resources;resources',  # Include resources folder
    # ]
    # if os.path.exists('resources') and os.listdir('resources'):
    #     cmd.extend(data_files)
    
    # Hidden imports for all required modules
    hidden_imports = [
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui', 
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.sip',
        '--hidden-import=cryptography',
        '--hidden-import=cryptography.hazmat',
        '--hidden-import=cryptography.hazmat.primitives',
        '--hidden-import=cryptography.hazmat.primitives.ciphers',
        '--hidden-import=cryptography.hazmat.primitives.kdf',
        '--hidden-import=cryptography.hazmat.backends',
        '--hidden-import=sqlite3',
        '--hidden-import=json',
        '--hidden-import=base64',
        '--hidden-import=secrets',
        '--hidden-import=hashlib'
    ]
    cmd.extend(hidden_imports)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable created: dist/PasswordKeeper/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_portable_package():
    """Create complete portable package with all dependencies"""
    print("\nCreating portable package...")
    
    portable_dir = "dist/PasswordKeeper_Portable"
    
    # Remove existing portable directory
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    # Create portable directory structure
    os.makedirs(portable_dir, exist_ok=True)
    
    # Copy the entire PyInstaller output directory
    pyinstaller_dir = "dist/PasswordKeeper"
    if os.path.exists(pyinstaller_dir):
        # Copy all files from PyInstaller output
        for item in os.listdir(pyinstaller_dir):
            src = os.path.join(pyinstaller_dir, item)
            dst = os.path.join(portable_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
    else:
        print("Error: PyInstaller output directory not found!")
        return False
    
    # Copy the launcher batch file
    launcher_src = "launcher.bat"
    if os.path.exists(launcher_src):
        shutil.copy2(launcher_src, f"{portable_dir}/Start_PasswordKeeper.bat")
    
    # Create portable marker file
    with open(f"{portable_dir}/portable.txt", 'w') as f:
        f.write("PORTABLE MODE ENABLED\n")
        f.write("This file enables portable mode.\n")
        f.write("All application data will be stored in this directory.\n")
        f.write("You can copy this entire folder to any Windows computer.\n")
    
    # Create data directories for portable mode
    data_dirs = ["data", "logs", "backups"]
    for dir_name in data_dirs:
        os.makedirs(f"{portable_dir}/{dir_name}", exist_ok=True)
    
    # Create comprehensive README for portable version
    readme_content = """
==============================================
Password Keeper - Portable Version
==============================================

This is a completely portable version of Password Keeper that requires NO INSTALLATION.

QUICK START:
-----------
1. Double-click "PasswordKeeper.exe" to start the application
   OR
   Double-click "Start_PasswordKeeper.bat" for better error handling

2. On first run, you'll be asked to create a master password
3. All your data will be stored in this folder

PORTABLE FEATURES:
-----------------
✓ No installation required
✓ Runs on any Windows 10/11 computer
✓ All data stored locally in this folder
✓ Copy entire folder to move to another computer
✓ No registry entries or system modifications
✓ Self-contained with all dependencies

FOLDER STRUCTURE:
----------------
PasswordKeeper.exe       - Main application
portable.txt            - Portable mode marker (DO NOT DELETE)
Start_PasswordKeeper.bat - Alternative launcher with error handling
data/                   - Your password database will be here
logs/                   - Application logs
backups/                - Automatic backups (if enabled)
_internal/              - Application files (DO NOT MODIFY)

USAGE TIPS:
----------
• Keep this entire folder together
• Create backups of the whole folder regularly
• The "data/" folder contains your encrypted passwords
• You can rename the main folder but keep contents intact
• Works on USB drives, network drives, cloud storage

SYSTEM REQUIREMENTS:
-------------------
• Windows 10 or Windows 11
• No additional software required
• About 100MB disk space
• Administrator rights NOT required

SECURITY NOTES:
--------------
• Your passwords are encrypted with AES-256
• Master password is never stored
• Database is encrypted even when application is closed
• Use a strong master password you'll remember

TROUBLESHOOTING:
---------------
If the application doesn't start:
1. Make sure you're on Windows 10/11
2. Try running "Start_PasswordKeeper.bat"
3. Check that all files are present
4. Ensure antivirus isn't blocking the application
5. Try running as administrator (right-click → "Run as administrator")

BACKUP STRATEGY:
---------------
IMPORTANT: Backup this entire folder regularly!
• Copy to external drive
• Upload to cloud storage (it's encrypted anyway)
• Create multiple backups in different locations
• Test that backups work by trying to run from backup location

If you lose your master password, your data CANNOT be recovered!

MOVING TO ANOTHER COMPUTER:
--------------------------
1. Close Password Keeper completely
2. Copy this ENTIRE folder to new computer
3. Run PasswordKeeper.exe on new computer
4. Enter your master password
5. All your data will be available immediately

VERSION: 1.0.0
SUPPORT: Check README.md for more information
"""
    
    with open(f"{portable_dir}/PORTABLE_README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create version info file
    version_info = f"""Password Keeper Portable v1.0.0
Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Platform: Windows 10/11
Mode: Fully Portable
Dependencies: Self-contained
"""
    
    with open(f"{portable_dir}/version.txt", 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("✓ Portable package created successfully!")
    print(f"✓ Location: {portable_dir}")
    print(f"✓ Size: {get_folder_size(portable_dir):.1f} MB")
    print("✓ Ready to copy to any Windows computer!")
    
    return True

def create_installer():
    """Create installer using Inno Setup (if available)"""
    print("\nCreating installer...")
    
    # Check if Inno Setup is available
    inno_setup_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if not os.path.exists(inno_setup_path):
        print("Inno Setup not found. Skipping installer creation.")
        print("You can download Inno Setup from: https://jrsoftware.org/isinfo.php")
        return False
    
    # Create Inno Setup script for portable app
    iss_content = """
[Setup]
AppName=Password Keeper
AppVersion=1.0.0
AppPublisher=Your Organization
AppPublisherURL=https://yourwebsite.com
DefaultDirName={autopf}\\PasswordKeeper
DefaultGroupName=Password Keeper
OutputDir=dist
OutputBaseFilename=PasswordKeeperSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
CreateUninstallRegKey=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\PasswordKeeper_Portable\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\Password Keeper"; Filename: "{app}\\PasswordKeeper.exe"
Name: "{autodesktop}\\Password Keeper"; Filename: "{app}\\PasswordKeeper.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\PasswordKeeper.exe"; Description: "{cm:LaunchProgram,Password Keeper}"; Flags: nowait postinstall skipifsilent
"""
    
    # Write ISS file
    os.makedirs('build', exist_ok=True)
    with open('build/setup.iss', 'w') as f:
        f.write(iss_content)
    
    # Run Inno Setup
    try:
        subprocess.run([inno_setup_path, 'build/setup.iss'], check=True)
        print("Installer created successfully!")
        print("Installer location: dist/PasswordKeeperSetup.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Installer creation failed: {e}")
        return False

def create_zip_package():
    """Create ZIP package for easy distribution"""
    print("\nCreating ZIP package...")
    
    portable_dir = "dist/PasswordKeeper_Portable"
    if not os.path.exists(portable_dir):
        print("Error: Portable directory not found!")
        return False
    
    # Create ZIP archive
    zip_path = "dist/PasswordKeeper_Portable_v1.0.0"
    shutil.make_archive(zip_path, 'zip', portable_dir)
    
    zip_size = os.path.getsize(f"{zip_path}.zip") / (1024 * 1024)
    print(f"✓ ZIP package created: {zip_path}.zip")
    print(f"✓ ZIP size: {zip_size:.1f} MB")
    print("✓ Ready for distribution!")
    
    return True

def verify_requirements():
    """Verify build requirements"""
    print("Checking build requirements...")
    
    required_packages = ['PyInstaller', 'PyQt6', 'cryptography']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PyInstaller':
                # Check PyInstaller via subprocess
                result = subprocess.run(['python', '-m', 'PyInstaller', '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✓ {package}")
                else:
                    missing_packages.append(package)
                    print(f"  ✗ {package} - MISSING")
            else:
                __import__(package)
                print(f"  ✓ {package}")
        except (ImportError, subprocess.SubprocessError):
            missing_packages.append(package)
            print(f"  ✗ {package} - MISSING")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("All requirements satisfied.\n")
    return True

def main():
    """Main build process for portable application"""
    print("Password Keeper Portable Build Script")
    print("=" * 50)
    
    # Verify requirements
    if not verify_requirements():
        sys.exit(1)
    
    # Clean previous builds
    clean_build()
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    # Create portable package
    if not create_portable_package():
        sys.exit(1)
    
    # Create ZIP distribution
    create_zip_package()
    
    # Optional: Create installer
    create_installer()
    
    # Get final sizes and info
    portable_dir = "dist/PasswordKeeper_Portable"
    if os.path.exists(portable_dir):
        folder_size = get_folder_size(portable_dir)
        file_count = sum(len(files) for _, _, files in os.walk(portable_dir))
        
        print("\n" + "=" * 50)
        print("🎉 PORTABLE BUILD COMPLETE! 🎉")
        print("=" * 50)
        print(f"📁 Portable folder: {portable_dir}")
        print(f"📦 Size: {folder_size:.1f} MB")
        print(f"📄 Files: {file_count}")
        print(f"🖥️  Platform: Windows 10/11")
        print("\n🚀 WHAT YOU GET:")
        print("  ✓ Complete portable application")
        print("  ✓ No installation required")
        print("  ✓ Copy & paste to any Windows computer")
        print("  ✓ All dependencies included")
        print("  ✓ Data travels with the app")
        print("\n📋 DISTRIBUTION FILES:")
        print("  • PasswordKeeper_Portable/ - Ready to use folder")
        print("  • PasswordKeeper_Portable_v1.0.0.zip - Compressed package")
        
        if os.path.exists("dist/PasswordKeeperSetup.exe"):
            installer_size = os.path.getsize("dist/PasswordKeeperSetup.exe") / (1024 * 1024)
            print(f"  • PasswordKeeperSetup.exe - Installer ({installer_size:.1f} MB)")
        
        print("\n🎯 USAGE:")
        print("  1. Copy 'PasswordKeeper_Portable' folder anywhere")
        print("  2. Double-click 'PasswordKeeper.exe' to run")
        print("  3. Create master password on first run")
        print("  4. Your data stays in the folder!")
        
        print("\n💡 TIPS:")
        print("  • Keep the entire folder together")
        print("  • Backup the whole folder regularly") 
        print("  • Works on USB drives, cloud storage, etc.")
        print("  • No admin rights needed")
        
    else:
        print("❌ Build failed - portable directory not found")
        sys.exit(1)

if __name__ == "__main__":
    main()
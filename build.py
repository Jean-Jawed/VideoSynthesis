"""
Build script for VideoSynthesis
Creates a standalone .exe using PyInstaller
"""

import os
import sys
import subprocess
import shutil


def main():
    print("=" * 60)
    print("VideoSynthesis - Build Script")
    print("Copyright © Jawed Tahir 2025")
    print("=" * 60)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller not found!")
        print("Please install it: pip install pyinstaller")
        sys.exit(1)
    
    print("✓ PyInstaller found")
    
    # Clean previous builds
    if os.path.exists('build'):
        print("Cleaning build directory...")
        shutil.rmtree('build')
    
    if os.path.exists('dist'):
        print("Cleaning dist directory...")
        shutil.rmtree('dist')
    
    if os.path.exists('VideoSynthesis.spec'):
        print("Removing old spec file...")
        os.remove('VideoSynthesis.spec')
    
    print()
    print("Building executable...")
    print("This may take several minutes...")
    print()
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',              # Single executable
        '--noconsole',            # No console window
        '--name', 'VideoSynthesis',
        '--clean',                # Clean cache
        'main.py'
    ]
    
    # Add icon if exists
    if os.path.exists('assets/icon.ico'):
        cmd.extend(['--icon', 'assets/icon.ico'])
    
    # Run PyInstaller
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print()
        print("=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        print()
        print(f"Executable location: dist/VideoSynthesis.exe")
        print(f"Size: ~300-500 MB")
        print()
        print("IMPORTANT NOTES:")
        print("- The .exe is self-contained but requires internet for:")
        print("  * First-time download of FFmpeg (~120 MB)")
        print("  * First-time download of Whisper model (150 MB - 3 GB)")
        print("  * AI synthesis API calls")
        print()
        print("- FFmpeg and Whisper will be downloaded to:")
        print("  %APPDATA%/VideoSynthesis/ and %USERPROFILE%/.cache/whisper/")
        print()
        print("- Test the .exe before distribution!")
        print()
    else:
        print()
        print("=" * 60)
        print("✗ Build failed!")
        print("=" * 60)
        print()
        print("Check the error messages above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

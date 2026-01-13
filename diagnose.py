"""
Comprehensive Diagnostic Tool for VideoSynthesis
Run this to check if everything is properly set up
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("VideoSynthesis - Complete Diagnostic Tool")
print("=" * 70)
print()

# 1. Check Python version
print("1. PYTHON VERSION")
print("-" * 70)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

# 2. Check required packages
print("2. REQUIRED PACKAGES")
print("-" * 70)

packages = [
    'customtkinter',
    'whisper',
    'yt_dlp',
    'requests',
    'anthropic',
    'openai',
    'google.generativeai',
    'PIL',
    'torch'
]

missing_packages = []
for package in packages:
    try:
        if package == 'whisper':
            import whisper
            print(f"✓ whisper: {whisper.__version__ if hasattr(whisper, '__version__') else 'installed'}")
        elif package == 'yt_dlp':
            import yt_dlp
            print(f"✓ yt-dlp: {yt_dlp.version.__version__}")
        elif package == 'PIL':
            from PIL import Image
            print(f"✓ Pillow: installed")
        elif package == 'google.generativeai':
            import google.generativeai as genai
            print(f"✓ google-generativeai: installed")
        else:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'installed')
            print(f"✓ {package}: {version}")
    except ImportError:
        print(f"✗ {package}: NOT INSTALLED")
        missing_packages.append(package)

print()

if missing_packages:
    print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
    print(f"Install with: pip install {' '.join(missing_packages)}")
    print()

# 3. Check FFmpeg
print("3. FFMPEG")
print("-" * 70)

if os.name == 'nt':  # Windows
    ffmpeg_dir = Path(os.getenv('APPDATA')) / 'VideoSynthesis'
else:
    ffmpeg_dir = Path.home() / '.VideoSynthesis'

ffmpeg_path = ffmpeg_dir / 'ffmpeg.exe'

if ffmpeg_path.exists():
    print(f"✓ FFmpeg found: {ffmpeg_path}")
    print(f"  Size: {ffmpeg_path.stat().st_size / 1024 / 1024:.1f} MB")
else:
    print(f"✗ FFmpeg NOT found at: {ffmpeg_path}")
    print(f"  Please download it in the Settings tab")

print()

# 4. Check Whisper models
print("4. WHISPER MODELS")
print("-" * 70)

whisper_cache = Path.home() / ".cache" / "whisper"

if whisper_cache.exists():
    print(f"Whisper cache directory: {whisper_cache}")
    
    models = {
        'tiny': 'tiny.pt',
        'base': 'base.pt',
        'small': 'small.pt',
        'medium': 'medium.pt',
        'large': 'large-v3.pt',
        'large-v2': 'large-v2.pt',
        'large-v1': 'large-v1.pt'
    }
    
    found_models = []
    for model_name, filename in models.items():
        model_path = whisper_cache / filename
        if model_path.exists():
            size_mb = model_path.stat().st_size / 1024 / 1024
            print(f"✓ {model_name}: {size_mb:.1f} MB")
            found_models.append(model_name)
    
    if not found_models:
        print("✗ No Whisper models found")
        print("  Please download a model in the Settings tab")
    else:
        print(f"\nInstalled models: {', '.join(found_models)}")
else:
    print(f"✗ Whisper cache directory not found: {whisper_cache}")
    print("  Please download a Whisper model in the Settings tab")

print()

# 5. Check application directories
print("5. APPLICATION DIRECTORIES")
print("-" * 70)

if os.name == 'nt':
    app_dir = Path(os.getenv('APPDATA')) / 'VideoSynthesis'
else:
    app_dir = Path.home() / '.VideoSynthesis'

print(f"App directory: {app_dir}")
if app_dir.exists():
    print(f"✓ Directory exists")
    
    log_file = app_dir / 'app.log'
    if log_file.exists():
        print(f"✓ Log file exists: {log_file}")
        print(f"  Size: {log_file.stat().st_size / 1024:.1f} KB")
        
        # Show last few lines of log
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print("\n  Last 5 log entries:")
                    for line in lines[-5:]:
                        print(f"    {line.strip()}")
        except:
            pass
    else:
        print(f"  Log file not created yet: {log_file}")
else:
    print(f"✗ Directory doesn't exist yet")

print()

# 6. Test file path functionality
print("6. FILE PATH TEST")
print("-" * 70)

test_file = input("Enter a file path to test (or press Enter to skip): ").strip()

if test_file:
    test_file = test_file.strip('"').strip("'")
    normalized = os.path.normpath(test_file)
    
    print(f"Original: {test_file}")
    print(f"Normalized: {normalized}")
    print(f"Exists: {os.path.exists(normalized)}")
    
    if os.path.exists(normalized):
        print(f"✓ File found!")
        print(f"  Size: {os.path.getsize(normalized) / 1024 / 1024:.1f} MB")
        
        # Try to check if it's a valid audio file
        ext = os.path.splitext(normalized)[1].lower()
        audio_extensions = ['.mp3', '.mp4', '.wav', '.m4a', '.avi', '.mkv', '.flac']
        if ext in audio_extensions:
            print(f"  Extension: {ext} (valid audio/video format)")
        else:
            print(f"  Extension: {ext} (might not be supported)")
    else:
        print(f"✗ File not found")
else:
    print("Skipped")

print()

# 7. Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)

issues = []

if missing_packages:
    issues.append(f"Missing Python packages: {', '.join(missing_packages)}")

if not ffmpeg_path.exists():
    issues.append("FFmpeg not installed")

if not whisper_cache.exists() or not any(
    (whisper_cache / f).exists() 
    for f in ['tiny.pt', 'base.pt', 'small.pt', 'medium.pt', 'large-v3.pt']
):
    issues.append("No Whisper model installed")

if issues:
    print("\n⚠️ ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    print("\n📋 RECOMMENDED ACTIONS:")
    print("  1. Install missing packages: pip install -r requirements.txt")
    print("  2. Run the application: python main.py")
    print("  3. Go to Settings tab")
    print("  4. Download FFmpeg and Whisper model")
else:
    print("\n✅ ALL CHECKS PASSED!")
    print("\nYour VideoSynthesis installation appears to be complete.")
    print("You should be able to:")
    print("  • Download videos")
    print("  • Transcribe audio")
    print("  • Generate summaries")

print()
print("=" * 70)
print("To view detailed logs, check: " + str(app_dir / 'app.log'))
print("=" * 70)

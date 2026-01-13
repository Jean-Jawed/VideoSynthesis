"""
Debug utility to test file path handling
Run this to verify file paths work correctly
"""

import os

def test_file_path(path):
    """Test if a file path is valid"""
    print("=" * 60)
    print(f"Testing path: {path}")
    print("=" * 60)
    
    # Original path
    print(f"\nOriginal path: {path}")
    print(f"Type: {type(path)}")
    
    # Normalized path
    normalized = os.path.normpath(path)
    print(f"\nNormalized path: {normalized}")
    
    # Exists check
    exists = os.path.exists(normalized)
    print(f"\nFile exists: {exists}")
    
    if exists:
        print(f"File size: {os.path.getsize(normalized)} bytes")
        print(f"Is file: {os.path.isfile(normalized)}")
        print(f"Absolute path: {os.path.abspath(normalized)}")
    else:
        print("\n⚠️ FILE NOT FOUND!")
        
        # Try to find similar files
        if os.path.dirname(normalized):
            dir_path = os.path.dirname(normalized)
            if os.path.exists(dir_path):
                print(f"\nDirectory exists: {dir_path}")
                print("Files in directory:")
                try:
                    for f in os.listdir(dir_path)[:10]:  # Show first 10 files
                        print(f"  - {f}")
                except Exception as e:
                    print(f"  Error listing directory: {e}")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    print("FILE PATH DEBUGGER")
    print("=" * 60)
    
    # Test some common path formats
    test_paths = [
        r"C:/Users/Javed/Music/test.mp3",
        r"C:\Users\Javed\Music\test.mp3",
        "C:/Users/Javed/Music/Claude Code détesté par les devs du jour au lendemain.mp3",
        r"C:\Users\Javed\Music\Claude Code détesté par les devs du jour au lendemain.mp3",
    ]
    
    print("Testing common path formats...\n")
    for path in test_paths:
        test_file_path(path)
    
    # Interactive mode
    print("\nINTERACTIVE MODE")
    print("Paste your file path below (or press Enter to quit)")
    
    while True:
        user_path = input("\nFile path: ").strip()
        if not user_path:
            break
        
        # Remove quotes if present
        user_path = user_path.strip('"').strip("'")
        
        test_file_path(user_path)

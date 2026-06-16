#!/usr/bin/env python3
"""
Automated PyInstaller build script for pdf-booklet-maker standalone executable.
"""
import os
import sys
import platform
import subprocess

def main():
    print("==================================================================")
    print(" 🛠️ Standalone Binary Builder (PyInstaller)")
    print("==================================================================")
    
    # 1. Ensure pyinstaller is installed in the active environment
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed.")
    except ImportError:
        print("! PyInstaller not found. Installing now...")
        try:
            # Run pip install pyinstaller
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✓ PyInstaller installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install PyInstaller: {e}")
            sys.exit(1)

    # 2. Determine operating system and set correct data path separator
    current_os = platform.system()
    separator = ";" if current_os == "Windows" else ":"
    print(f"✓ Target OS detected: {current_os} (Separator: '{separator}')")

    # 3. Resolve the path of the pyinstaller executable inside the active environment
    bin_dir = os.path.dirname(sys.executable)
    pyinstaller_bin = os.path.join(bin_dir, "pyinstaller")
    if current_os == "Windows":
        pyinstaller_bin += ".exe"

    if not os.path.exists(pyinstaller_bin):
        print(f"! Local pyinstaller executable not found at '{pyinstaller_bin}'. Falling back to system 'pyinstaller'.")
        pyinstaller_bin = "pyinstaller"
    else:
        print(f"✓ Found local PyInstaller binary: {pyinstaller_bin}")

    # 4. Construct PyInstaller command arguments
    static_src = os.path.join("pdf_booklet", "web", "static")
    static_dest = os.path.join("pdf_booklet", "web", "static")
    add_data_arg = f"{static_src}{separator}{static_dest}"

    pyinstaller_cmd = [
        pyinstaller_bin,
        "--onefile",
        "--name", "pdf-booklet-maker",
        "--add-data", add_data_arg,
        "make_booklet.py"
    ]

    # 5. Run PyInstaller
    print(f"✓ Running PyInstaller command:\n  {' '.join(pyinstaller_cmd)}\n")
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("\n==================================================================")
        print(" 🎉 Standalone Binary Built Successfully!")
        
        # Output binary path
        ext = ".exe" if current_os == "Windows" else ""
        binary_path = os.path.abspath(os.path.join("dist", f"pdf-booklet-maker{ext}"))
        
        print(f" 👉 Standalone executable path:\n    {binary_path}")
        print(" 💡 You can move this single file anywhere and execute it directly!")
        print("==================================================================")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ PyInstaller compilation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

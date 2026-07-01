import PyInstaller.__main__
import sys
import os
import shutil

def build():
    print("Building hanif-finance standalone executable...")
    
    # Clean previous build artifacts
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            
    # Run PyInstaller
    args = [
        "hanif_finance/cli.py",
        "--name=hanif-finance",
        "--onefile",
        "--clean",
        "--console",
    ]
    
    PyInstaller.__main__.run(args)
    print("\nBuild complete! Standalone binary is located in `./dist/hanif-finance` (or `hanif-finance.exe` on Windows).")

if __name__ == "__main__":
    build()

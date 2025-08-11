import subprocess
import sys

def install_requirements():
    requirements = [
        'streamlit',
        'pandas',
        'numpy',
        'openpyxl',
        'streamlit-autorefresh'
    ]
    
    print("Installing required packages...")
    
    for package in requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
    
    print("\nInstallation complete!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    install_requirements()
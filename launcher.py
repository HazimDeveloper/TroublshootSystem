import subprocess
import webbrowser
import time
import os
import sys

def launch_streamlit():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tgs_file = os.path.join(script_dir, 'tgs_system.py')
    
    # Check if tgs_system.py exists
    if not os.path.exists(tgs_file):
        print("Error: tgs_system.py not found!")
        input("Press Enter to exit...")
        return
    
    # Start Streamlit
    try:
        print("Starting Troubleshooting Guide System...")
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', tgs_file,
            '--server.headless', 'true',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ])
        
        # Wait a moment and open browser
        time.sleep(3)
        webbrowser.open('http://localhost:8501')
        
        print("System is running! Close this window to stop the application.")
        print("Access the system at: http://localhost:8501")
        
        # Keep the launcher running
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            print("\nShutting down...")
            
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    launch_streamlit()
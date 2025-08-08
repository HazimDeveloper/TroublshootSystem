@echo off
cd /d "%~dp0"
python -m streamlit run tgs_system.py --server.headless true --server.port 8501 --browser.gatherUsageStats false
pause
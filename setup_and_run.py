#!/usr/bin/env python3
"""
Quick setup and run script for ODCV app
"""
import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Ensure Python 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print("✅ Python version OK")


def create_directories():
    """Create necessary directories"""
    dirs = [
        "data",
        "data/pluto",
        "cache",
        "static"
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(exist_ok=True)
    print("✅ Directories created")


def check_env_file():
    """Check if .env file exists"""
    if not Path(".env").exists():
        if Path(".env.template").exists():
            print("⚠️  No .env file found. Creating from template...")
            import shutil
            shutil.copy(".env.template", ".env")
            print("📝 Please edit .env with your NYC Geoclient API credentials")
            print("   Get them from: https://developer.cityofnewyork.us/")
        else:
            print("⚠️  No .env file found. Creating basic one...")
            with open(".env", "w") as f:
                f.write("GEOCLIENT_APP_ID=\n")
                f.write("GEOCLIENT_APP_KEY=\n")
                f.write("LOG_LEVEL=INFO\n")
    else:
        print("✅ Environment file exists")


def check_data_files():
    """Check if data files are present"""
    required_files = {
        "PLUTO (Manhattan)": "data/pluto/MN.csv",
        "PLUTO (Brooklyn)": "data/pluto/BK.csv",
        "PLUTO (Bronx)": "data/pluto/BX.csv",
        "PLUTO (Queens)": "data/pluto/QN.csv",
        "PLUTO (Staten Island)": "data/pluto/SI.csv",
        "LL84 Energy Data": "data/ll84_monthly.csv",
        "LL87 Audit Data": "data/ll87_2019_2024.csv",
        "LL33 Energy Grades": "data/ll33_grades.csv"
    }
    
    missing = []
    for name, path in required_files.items():
        if not Path(path).exists():
            missing.append((name, path))
    
    if missing:
        print("\n⚠️  Missing data files:")
        for name, path in missing:
            print(f"   - {name}: {path}")
        print("\n📥 Download instructions:")
        print("   PLUTO: https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page")
        print("   LL84: https://www.nyc.gov/site/buildings/codes/benchmarking.page")
        print("   LL87: https://data.cityofnewyork.us/Environment/LL87-Energy-Audit-Data/au6c-jqvf")
        print("   LL33: https://www.nyc.gov/site/buildings/codes/energy-grades.page")
        print("\n💡 The app will work with limited functionality using mock data.")
    else:
        print("✅ All data files present")
    
    return len(missing) == 0


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Try running: pip install -r requirements.txt")
        sys.exit(1)


def ensure_index_html():
    """Ensure index.html exists"""
    if not Path("index.html").exists():
        print("⚠️  index.html not found. Creating minimal version...")
        with open("index.html", "w") as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>ODCV Building Intelligence</title>
</head>
<body>
    <h1>ODCV Building Intelligence</h1>
    <p>The web interface file is missing.</p>
    <p>API is running at: <a href="/docs">API Documentation</a></p>
</body>
</html>
""")


def run_app():
    """Run the application"""
    print("\n🚀 Starting ODCV Building Intelligence App...")
    print("   Local URL: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n   Press Ctrl+C to stop\n")
    
    try:
        # Try to use uvicorn directly for better development experience
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        # Fallback to running the script directly
        subprocess.call([sys.executable, "main.py"])


def main():
    """Main setup and run function"""
    print("🏢 ODCV Building Intelligence App Setup")
    print("=" * 40)
    
    # Check environment
    check_python_version()
    create_directories()
    check_env_file()
    
    # Install dependencies
    install_dependencies()
    
    # Check data files
    has_all_data = check_data_files()
    
    # Ensure web interface exists
    ensure_index_html()
    
    # Prompt to continue
    if not has_all_data:
        response = input("\n▶️  Continue without all data files? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Run the app
    run_app()


if __name__ == "__main__":
    main()

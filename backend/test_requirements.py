#!/usr/bin/env python3
"""
Test script to validate requirements.txt installation
"""

import subprocess
import sys
import os

def test_requirements_installation():
    """Test if all packages in requirements.txt can be resolved"""
    print("🔍 Testing requirements.txt package resolution...")
    
    try:
        # Test if pip can resolve all dependencies without installing
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--dry-run", "--no-deps", "-r", "requirements.txt"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ All packages in requirements.txt are resolvable")
            return True
        else:
            print("❌ Package resolution failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error testing requirements: {e}")
        return False

def test_critical_imports():
    """Test if critical packages can be imported"""
    critical_packages = [
        'fastapi',
        'uvicorn', 
        'sqlalchemy',
        'pandas',
        'numpy',
        'sklearn',
        'google.auth',
        'jose',
        'passlib',
        'aiofiles',
        'PIL'
    ]
    
    print("\n🧪 Testing critical package imports...")
    failed_imports = []
    
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All critical packages imported successfully")
        return True

def main():
    """Main test function"""
    print("🚀 Testing Updated Requirements.txt")
    print("=" * 50)
    
    # Test package resolution
    resolution_ok = test_requirements_installation()
    
    # Test imports
    imports_ok = test_critical_imports()
    
    if resolution_ok and imports_ok:
        print("\n🎉 Requirements.txt is ready for production!")
        print("\n📋 To install in a fresh environment:")
        print("1. Create virtual environment: python -m venv venv")
        print("2. Activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
        print("3. Install: pip install -r requirements.txt")
        return True
    else:
        print("\n❌ Requirements.txt needs fixes")
        return False

if __name__ == "__main__":
    main()
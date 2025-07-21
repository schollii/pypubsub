#!/usr/bin/env python3
"""
This script demonstrates how to verify that MyPy correctly recognizes
the type information in the pypubsub package.
"""

import subprocess
import sys
import os

def main():
    print("Verifying MyPy integration with pypubsub")
    
    # Step 1: Create a simple test file that uses pypubsub
    test_file = "mypy_test_script.py"
    with open(test_file, "w") as f:
        f.write("""
from pubsub import pub

# Use some typed functions from the package
pub.subscribe(lambda msg: print(msg), "test.topic")
pub.sendMessage("test.topic", message="Hello")

# Intentional type error to verify MyPy is checking
x: str = 42  # This should trigger a MyPy error if working
""")
    
    print(f"Created test file: {test_file}")
    
    # Step 2: Check if MyPy is installed
    try:
        subprocess.run(["mypy", "--version"], check=True, capture_output=True)
        print("MyPy is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("MyPy is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "mypy"], check=True)
    
    # Step 3: Run MyPy on the test file
    print("\nRunning MyPy on the test file...")
    result = subprocess.run(["mypy", test_file], capture_output=True, text=True)
    
    # Step 4: Analyze the results
    print("\nMyPy output:")
    print(result.stdout)
    
    if "Library stub not installed for 'pubsub'" in result.stdout or "found module but no type hints" in result.stdout:
        print("\nResult: MyPy is NOT recognizing the type information in pypubsub")
        print("This suggests the py.typed file is not being properly included or found.")
    elif "error: Incompatible types in assignment" in result.stdout and "variable has type \"str\"" in result.stdout:
        print("\nResult: MyPy is successfully recognizing the type information in pypubsub!")
        print("The intentional type error was caught, and no errors about missing stubs were reported.")
    else:
        print("\nResult: Unclear. Please review the MyPy output above.")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\nRemoved test file: {test_file}")

if __name__ == "__main__":
    main()
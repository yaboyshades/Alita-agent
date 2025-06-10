"""
Cross-platform installer for the Alita Agent Framework.
Creates a virtual environment, installs dependencies, and sets up the .env file.
"""
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
VENV_DIR = ROOT_DIR / ".venv"

def run_command(command, error_message):
    """Executes a command and handles errors."""
    try:
        print(f"Executing: {' '.join(command)}")
        subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error: {error_message}")
        print(f"Details: {e}")
        sys.exit(1)

def main():
    """Main setup function."""
    print("--- Setting up Alita Agent Framework ---")

    # 1. Create virtual environment
    if not VENV_DIR.exists():
        print(f"1. Creating virtual environment at: {VENV_DIR}")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)], "Failed to create virtual environment.")
    else:
        print("1. Virtual environment already exists.")

    # 2. Determine Python and Pip executables
    if sys.platform == "win32":
        python_executable = VENV_DIR / "Scripts" / "python.exe"
        pip_executable = VENV_DIR / "Scripts" / "pip.exe"
    else:
        python_executable = VENV_DIR / "bin" / "python"
        pip_executable = VENV_DIR / "bin" / "pip"

    # 3. Install dependencies
    requirements_file = (ROOT_DIR / "requirements.txt").resolve()
    if requirements_file.exists():
        print(f"2. Installing dependencies from {requirements_file}...")
        run_command([str(pip_executable), "install", "-r", str(requirements_file)], "Failed to install dependencies.")
    else:
        print("Warning: requirements.txt not found. Skipping dependency installation.")

    # 4. Create .env file from example
    env_example_file = ROOT_DIR / ".env.example"
    env_file = ROOT_DIR / ".env"
    if env_example_file.exists() and not env_file.exists():
        print("3. Creating .env file for configuration...")
        env_file.write_text(env_example_file.read_text())
        print("   -> Please edit the .env file to add your API keys.")
    elif env_file.exists():
        print("3. .env file already exists.")
    
    # 5. Create workspace directories
    print("4. Creating workspace directories...")
    (ROOT_DIR / "workspace" / "logs").mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / "workspace" / "tools").mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / "workspace" / "memory").mkdir(parents=True, exist_ok=True)


    print("\n--- Setup Complete! ---")
    print("To activate the environment, run:")
    if sys.platform == "win32":
        print(f"  > {VENV_DIR}\\Scripts\\activate")
    else:
        print(f"  $ source {VENV_DIR}/bin/activate")

if __name__ == "__main__":
    main()

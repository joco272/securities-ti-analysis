import subprocess
import sys

def run_command(command, wait=True):
    """
    Runs a command in the shell and prints it to the console.
    If the command fails, it prints an error message and exits the script.
    """
    print(f"Executing command: {command}")
    try:
        if wait:
            subprocess.run(command, check=True, shell=True)
        else:
            subprocess.Popen(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(e)
        sys.exit(1)

def main():
    """
    Installs dependencies, initializes the database, and runs the application.
    """
    print("--- Setting up and running the Securities Analysis and Backtesting App ---")

    # 1. Install Dependencies
    run_command("pip install -r requirements.txt")

    # 2. Initialize the Database
    run_command("python src/database.py")

    # 3. Run the Application
    print("Starting the Streamlit application...")
    run_command("streamlit run src/app.py", wait=False)

    print("--- Application has been started ---")

if __name__ == "__main__":
    main()

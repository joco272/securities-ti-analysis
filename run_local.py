import subprocess
import sys
import platform

def run_command(command, wait=True):
    """
    Runs a command in the shell, printing it to the console.
    Handles different operating systems for detaching the final process.
    If a command fails, it prints an error and exits.
    """
    print(f"Executing command: {command}")
    try:
        if wait:
            # For commands that need to finish before the next step
            subprocess.run(command, check=True, shell=True)
        else:
            # For the final, long-running command (Streamlit)
            if platform.system() == "Windows":
                # Use CREATE_NEW_CONSOLE to run in a new window, detached from the parent
                subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # On Unix-like systems, Popen is sufficient to run in the background
                subprocess.Popen(command, shell=True)

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e}")
        sys.exit(1)

def main():
    """
    Installs dependencies, initializes the database, and runs the application.
    """
    print("--- Setting up and running the Securities Analysis and Backtesting App ---")

    # Step 1: Install Dependencies
    run_command("pip install -r requirements.txt")

    # Step 2: Initialize the Database
    run_command("python src/database.py")

    # Step 3: Run the Application
    print("\\nStarting the Streamlit application...")
    print("A new window will open with the application running.")
    print("You can close this window; the application will keep running in the new window.")
    run_command("streamlit run src/app.py", wait=False)

    print("\\n--- Setup complete. The application is starting. ---")

if __name__ == "__main__":
    main()

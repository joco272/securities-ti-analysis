def print_instructions():
    """
    Prints the instructions for running the application locally.
    """
    instructions = """
    To run the Securities Analysis and Backtesting App locally, please follow these steps:

    1. Install Dependencies:
       Open a terminal in the project's root directory and run the following command to install all the necessary Python packages:

       pip install -r requirements.txt

    2. Initialize the Database:
       After the installation is complete, run this command to create and set up the local SQLite database file:

       python src/database.py

    3. Run the Application:
       Finally, start the Streamlit application with this command:

       streamlit run src/app.py

    After running the last command, the application should open automatically in your default web browser.
    """
    print(instructions)

if __name__ == "__main__":
    print_instructions()

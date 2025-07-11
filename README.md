# PyFinder

PyFinder is a client-server application for searching security department databases.

## How to Set Up and Run the Application

### 1. Setup

To get started, run the setup script for your operating system. This will install all the necessary dependencies for both the backend and frontend.

-   **For Windows:**
    ```cmd
    setup.bat
    ```
-   **For Linux/macOS:**
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```


### 2. Configure .env

Then, it is necessary to configure the .env file with: 
-   **Dabatase Directory**
    ```bash
    DB_DIR=C:\Users\danie\Documents\gerson\db
    ```

### 3. Start the Application

After the setup is complete, run the start script for your operating system. This will launch the backend and frontend servers in separate terminal windows.

-   **For Windows:**
    ```cmd
    start.bat
    ```
-   **For Linux/macOS:**
    ```bash
    chmod +x start.sh
    ./start.sh
    ```

### 4. Access the Application

Once the servers are running, you can access the PyFinder application in your web browser by navigating to:

[**http://localhost:5173**](http://localhost:5173)

---

## How to Use the Application

### CPF Search

You can search for an individual's information in two ways:

1.  **By CPF:** Enter the full CPF number into the search field.
2.  **By Name:** Enter the person's full or partial name. The search will return all matching records.

### CNPJ Search

To search for a company's information, enter the full CNPJ number into the designated search field. The application will retrieve and display the company's details.
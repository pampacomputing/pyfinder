# pyfinder
Multiprocessing client-server python application to find people inside security department database.

## Prerequisites
- Python 3.x
- Node.js and npm

## Backend Installation
1. Navigate to the `pyfinder_django` directory:
   ```bash
   cd pyfinder_django
   ```
2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install the backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Frontend Installation
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install the frontend dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Backend (Django)
1. Navigate to the `pyfinder_django` directory.
2. Activate your virtual environment (if not already active).
3. Run the Django development server:
   ```bash
   python manage.py runserver
   ```

### Frontend (Vue.js)
1. Navigate to the `frontend` directory.
2. Start the Vue.js development server:
   ```bash
   npm run dev
   ```
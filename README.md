# pyfinder

This project now includes a simple Django API for searching user records in two SQLite databases.

## Running

Install the requirements and run the development server:

```bash
pip install -r requirements.txt
cd django_api
python manage.py runserver
```

The API exposes `/api/search?query=<name>` returning JSON results merged from both databases.

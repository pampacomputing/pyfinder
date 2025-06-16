# pyfinder

This project exposes a Django API for searching user records stored in two SQLite databases. The search logic mirrors the original application while using Django views.

## Running

Install the requirements and run the development server:

```bash
pip install -r requirements.txt
cd django_api
python manage.py runserver
```

The API exposes `/api/search` and accepts the query parameters `name`, `cpf` and `date`. At least one of these parameters must be provided. Results from both databases are merged and returned as JSON.

# pyfinder
Multiprocessing client-server python application to find people inside security department database.

## Django API Service

A lightweight Django project provides a REST endpoint for searching across two SQLite databases. To start the development server:

```bash
cd searchservice
python manage.py runserver
```

Send requests to `http://localhost:8000/api/search?query=value`.

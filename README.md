# pyfinder

This project exposes a Django API for searching user records stored in two SQLite databases. The search logic mirrors the original application while using Django views.

## Running

Install the requirements and run the development server:

```bash
./install.sh
cd django_api
python manage.py runserver
```

The API exposes `/api/search` and expects a POST request with the following JSON structure:

```json
{
  "request_id": 1,
  "user_data": {
    "name": "John",
    "cpf": "12345678901",
    "gender": "M",
    "date": "1990-01-01"
  }
}
```

At least one of `name`, `cpf` or `date` must be provided. The response includes the `response_id` and a list of matching users:

```json
{
  "response_id": 1,
  "user_data": [
    {
      "name": "John",
      "cpf": "12345678901",
      "gender": "Male",
      "date": "1990-01-01"
    }
  ]
}
```

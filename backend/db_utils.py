import sqlite3
from django.conf import settings

def get_cnpj_db_connection():
    db_path = settings.DATABASES["cnpj_db"]["NAME"]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_basecpf_db_connection():
    db_path = settings.DATABASES["basecpf_db"]["NAME"]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

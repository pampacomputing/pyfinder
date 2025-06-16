"""Helper utilities for query normalization and execution."""

from dataclasses import dataclass
from unidecode import unidecode

@dataclass
class User:
    name: str = ""
    cpf: str = ""
    gender: str = ""
    date: str = ""

    def normalized(self) -> "User":
        return User(
            name=unidecode(self.name.upper()) if self.name else "",
            cpf=self.cpf.replace(".", "").replace("-", "") if self.cpf else "",
            gender="Female" if self.gender in ("F", "Female") else (
                "Male" if self.gender in ("M", "Male") else ""
            ),
            date=self.date or "",
        )

def execute_query(cursor, user: User):
    user = user.normalized()
    conditions = []
    params = []

    if user.name:
        conditions.append("nome LIKE ?")
        params.append(f"%{user.name}%")
    if user.cpf:
        conditions.append("cpf = ?")
        params.append(user.cpf)
    if user.date:
        conditions.append("nasc = ?")
        params.append(user.date)

    if not conditions:
        return []

    query = "SELECT cpf, nome, gender, nasc FROM cpf WHERE " + " AND ".join(conditions) + " LIMIT 1000"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [
        {"name": row[1], "cpf": row[0], "gender": row[2], "date": row[3]}
        for row in rows
    ]

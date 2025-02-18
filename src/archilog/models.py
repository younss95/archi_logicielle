import sqlalchemy
import uuid

from dataclasses import dataclass
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID



engine = create_engine("sqlite:///data.db", echo=True)
metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("amount", Integer, nullable=False),
    Column("category", String, nullable=False)
)

metadata.create_all(engine)  # Créer les tables SQLAlchemy






def init_db():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS entries"))  # Supprimez la table si elle existe déjà
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT
            )
        """))
        conn.commit()




@dataclass
class Entry:
    id: int
    name: str
    amount: float
    category: str | None

    @classmethod
    def from_db(cls, id: int, name: str, amount: float, category: str | None):
        return cls(
            id,
            name,
            amount,
            category,
        )


def create_entry(name: str, amount: float, category: str | None = None) -> None:
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO entries (name, amount, category) VALUES (:name, :amount, :category)"
        ), {"name": name, "amount": amount, "category": category})

        conn.commit()







def get_entry(id: int) -> Entry:  # id doit être un entier maintenant
    with engine.connect() as conn:
        result = conn.execute(text("select * from entries where id = ?"), (id,)).fetchone()
        if result:
            return Entry.from_db(*result)
        else:
            raise Exception("Entry not found")



def get_all_entries() -> list[Entry]:
    with engine.connect() as conn:
        results = conn.execute(text("select * from entries")).fetchall()
        return [Entry.from_db(*r) for r in results]


def update_entry(id: int, name: str, amount: float, category: str | None) -> None:  # id est un entier maintenant
    with engine.connect() as conn:
        conn.execute(text(
            "UPDATE entries SET name = :name, amount = :amount, category = :category WHERE id = :id"
        ), {"name": name, "amount": amount, "category": category, "id": id})
        conn.commit()




def delete_entry(id: int) -> None:  # id est un entier maintenant
    with engine.connect() as conn:
        conn.execute(text("delete from entries where id = ?"), (id,))
        conn.commit()

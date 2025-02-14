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
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),  # UUID en String pour SQLite
    Column("name", String, nullable=False),
    Column("amount", Integer, nullable=False),
    Column("category", String, nullable=False)
)

metadata.create_all(engine)  # Créer les tables SQLAlchemy






def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT
            )
        """))
        conn.commit()


@dataclass
class Entry:
    id: uuid.UUID
    name: str
    amount: float
    category: str | None

    @classmethod
    def from_db(cls, id: str, name: str, amount: float, category: str | None):
        return cls(
            uuid.UUID(id),
            name,
            amount,
            category,
        )


def create_entry(name: str, amount: float, category: str | None = None) -> None:
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO entries (id, name, amount, category) VALUES (:id, :name, :amount, :category)"
        ), {"id": str(uuid.uuid4()), "name": name, "amount": amount, "category": category})

        conn.commit()



def get_entry(id: uuid.UUID) -> Entry:
    with engine.connect() as conn:
        result = conn.execute("select * from entries where id = ?", (id.hex,)).fetchone()
        if result:
            return Entry.from_db(*result)
        else:
            raise Exception("Entry not found")


def get_all_entries() -> list[Entry]:
    with engine.connect() as conn:
        results = conn.execute("select * from entries").fetchall()
        return [Entry.from_db(*r) for r in results]


def update_entry(id: uuid.UUID, name: str, amount: float, category: str | None) -> None:
    with engine.connect() as conn:
        conn.execute(text(
            "UPDATE entries SET name = :name, amount = :amount, category = :category WHERE id = :id"
        ), {"name": name, "amount": amount, "category": category, "id": id.hex})
        conn.commit()



def delete_entry(id: uuid.UUID) -> None:
    with engine.connect() as conn:
        conn.execute("delete from entries where id = ?", (id.hex,))

import sqlalchemy
import uuid

from dataclasses import dataclass
from sqlalchemy import *




engine = create_engine("sqlite:///data.db")
metadata = MetaData()


# Définition de la table entries
entries_table = Table(
    "entries",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("category", String, nullable=True)
)





def init_db():
    metadata.create_all(engine)  # Créer les tables SQLAlchemy




@dataclass
class Entry:
    id: int
    name: str
    amount: float
    category: str

    @classmethod
    def from_db(cls, id: int, name: str, amount: float, category: str | None):
        return cls(
            id,
            name,
            amount,
            category,
        )


# Fonction pour insérer une entrée dans la table entries
def create_entry(name: str, amount: float, category: str | None = None):
    stmt = insert(entries_table).values(name=name, amount=amount, category=category)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

# Fonction pour obtenir une entrée par son ID
def get_entry(id: int):
    stmt = select(entries_table.c.id, entries_table.c.name, entries_table.c.amount, entries_table.c.category).where(entries_table.c.id == id)
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchone()
        if result:
            return result  # Retourne la ligne sous forme de tuple
        else:
            raise Exception("Entry not found")


# Fonction pour obtenir toutes les entrées
def get_all_entries():
    stmt = select(entries_table.c.id, entries_table.c.name, entries_table.c.amount, entries_table.c.category)
    with engine.connect() as conn:
        results = conn.execute(stmt).fetchall()
        return results  # Liste de tuples


# Fonction pour mettre à jour une entrée
def update_entry(id: int, name: str, amount: float, category: str | None):
    stmt = update(entries_table).where(entries_table.c.id == id).values(name=name, amount=amount, category=category)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

# Fonction pour supprimer une entrée
def delete_entry(id: int):
    stmt = delete(entries_table).where(entries_table.c.id == id)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


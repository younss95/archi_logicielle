from dataclasses import dataclass
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, insert, select, update, delete
from archilog import config

# Configuration de la base de données
engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)
metadata = MetaData()

# Définition de la table 'entries'
entries_table = Table(
    "entries",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("category", String, nullable=True)
)

# Fonction d'initialisation de la base de données
def init_db():
    metadata.create_all(engine)  # Créer les tables SQLAlchemy

# Classe 'Entry' représentant une entrée dans la table
@dataclass
class Entry:
    id: int
    name: str
    amount: float
    category: str | None

    @classmethod
    def from_db(cls, _id: int, name: str, amount: float, category: str | None):
        return cls(
            id=_id,  # Utilisation de 'id' pour la correspondance avec la base de données
            name=name,
            amount=amount,
            category=category,
        )

# Fonction pour insérer une entrée dans la table 'entries'
def create_entry(name: str, amount: float, category: str | None = None):
    stmt = insert(entries_table).values(name=name, amount=amount, category=category)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

# Fonction pour obtenir une entrée par son ID
def get_entry(_id: int):
    stmt = select(entries_table.c.id, entries_table.c.name, entries_table.c.amount, entries_table.c.category).where(entries_table.c.id == _id)
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchone()
        if result:
            return Entry.from_db(*result)  # Retourne la ligne sous forme de tuple
        else:
            return None  # Au lieu de lever une exception


# Fonction pour obtenir toutes les entrées
def get_all_entries():
    stmt = select(entries_table.c.id, entries_table.c.name, entries_table.c.amount, entries_table.c.category)
    with engine.connect() as conn:
        results = conn.execute(stmt).fetchall()
        return [Entry.from_db(*row) for row in results]  # Liste de tuples

# Fonction pour mettre à jour une entrée
def update_entry(_id: int, name: str, amount: float, category: str | None):
    stmt = update(entries_table).where(entries_table.c.id == _id).values(name=name, amount=amount, category=category)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

# Fonction pour supprimer une entrée
def delete_entry(_id: int):
    stmt = delete(entries_table).where(entries_table.c.id == _id)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

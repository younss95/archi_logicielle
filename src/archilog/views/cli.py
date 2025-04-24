import click
import archilog.services as services
import archilog.models as models

from tabulate import tabulate


@click.group()
def cli():
    """CLI pour gérer les entrées de données."""
    pass


@cli.command()
@click.option("-n", "--name", prompt="Name")
@click.option("-a", "--amount", type=float, prompt="Amount")
@click.option("-c", "--category", prompt="Category", default=None)
def create(name: str, amount: float, category: str):
    """Créer une nouvelle entrée."""
    try:
        models.create_entry(name, amount, category)
        click.echo(f"Entry for {name} created successfully!")
    except Exception as e:
        click.echo(f"Error creating entry: {e}")


@cli.command()
@click.option("--id","id_", required=True, type=int)
def get(id_: int):
    """Récupérer une entrée par ID."""
    entry = models.get_entry(id_)
    click.echo(entry)


@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    """Importer des données depuis un fichier CSV."""
    services.import_from_csv(csv_file)


@cli.command()
@click.argument("csv_file", type=click.Path(writable=True))
def export_csv(csv_file):
    """Exporter les entrées vers un fichier CSV."""
    csv_data = services.export_to_csv()
    with open(csv_file, "w", newline="") as file:
        file.write(csv_data.getvalue())
    click.echo(f"Fichier exporté : {csv_file}")


@cli.command()
@click.option("--id", "id_",type=int, required=True)
@click.option("-n", "--name", required=True)
@click.option("-a", "--amount", type=float, required=True)
@click.option("-c", "--category", default=None)
def update(id_: int, name: str, amount: float, category: str):
    """Mettre à jour une entrée."""
    models.update_entry(id_, name, amount, category)


@cli.command()
@click.option("--id", "id_", required=True, type=int)
def delete(id_: int):
    """Supprimer une entrée."""
    models.delete_entry(id_)


@cli.command()
@click.option("--as-csv", is_flag=True, help="Export entries to CSV")
def get_entries(as_csv: bool):
    """Afficher toutes les entrées."""
    entries = models.get_all_entries()

    if not entries:
        click.echo("Aucune entrée trouvée.")
        return

    if as_csv:
        click.echo(tabulate(entries, headers="keys"))
    else:
        table = [[entry.id, entry.name, entry.amount, entry.category] for entry in entries]
        headers = ["ID", "Name", "Amount", "Category"]
        click.echo(tabulate(table, headers=headers, tablefmt="grid"))


@cli.command()
def init_db():
    """Initialiser la base de données."""
    models.init_db()
    click.echo("Base de données initialisée avec succès.")


if __name__ == "__main__":
    cli()

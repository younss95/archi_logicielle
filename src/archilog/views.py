import click
import uuid

import archilog.models as models
import archilog.services as services

from tabulate import tabulate


@click.group()
def cli():
    pass


@cli.command()
def init_db():
    models.init_db()


@cli.command()
@click.option("-n", "--name", prompt="Name")
@click.option("-a", "--amount", type=float, prompt="Amount")
@click.option("-c", "--category", prompt="Category")
def create(name: str, amount: float, category: str | None):
    try:
        models.create_entry(name, amount, category)
        click.echo(f"Entry for {name} created successfully!")
    except Exception as e:
        click.echo(f"Error creating entry: {e}")



@cli.command()
@click.option("--id", required=True, type=click.UUID)
def get(id: uuid.UUID):
    click.echo(models.get_entry(id))


@cli.command()
@click.option("--as-csv", is_flag=True, help="Ouput a CSV string.")
def get_all(as_csv: bool):
    if as_csv:
        click.echo(services.export_to_csv().getvalue())
    else:
        click.echo(models.get_all_entries())


@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    services.import_from_csv(csv_file)


@cli.command()
@click.option("--id", type=click.UUID, required=True)
@click.option("-n", "--name", required=True)
@click.option("-a", "--amount", type=float, required=True)
@click.option("-c", "--category", default=None)
def update(id: uuid.UUID, name: str, amount: float, category: str | None):
    models.update_entry(id, name, amount, category)


@cli.command()
@click.option("--id", required=True, type=click.UUID)
def delete(id: uuid.UUID):
    models.delete_entry(id)

@cli.command()
def get_entries():
    entries = models.get_all_entries()

    table = [
        [entry.id, entry.name, entry.amount, entry.category]for entry in entries
    ]

    # Affichage sous forme de tableau
    headers = ["ID", "Name", "Amount", "Category"]
    click.echo(tabulate(table, headers=headers, tablefmt="grid"))


@cli.command()
def init_db():
    models.init_db()


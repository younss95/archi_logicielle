import click
import csv

import archilog.models as models
import archilog.services as services

from tabulate import tabulate
from flask import render_template, Flask


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
@click.option("--id", required=True, type=int)
def get(id: int):
    click.echo(models.get_entry(id))



@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    services.import_from_csv(csv_file)


@cli.command()
@click.option("--id", type=int, required=True)
@click.option("-n", "--name", required=True)
@click.option("-a", "--amount", type=float, required=True)
@click.option("-c", "--category", default=None)
def update(id: int, name: str, amount: float, category: str | None):
    models.update_entry(id, name, amount, category)


@cli.command()
@click.option("--id", required=True, type=int)
def delete(id: int):
    models.delete_entry(id)


@cli.command()
@click.option("--as-csv", is_flag=True, help="Export entries to CSV")
def get_entries(as_csv: bool):
    entries = models.get_all_entries()

    if as_csv:
        click.echo(tabulate(entries, headers="keys"))
    else:
        # Display the entries in a table format
        table = [
            [entry.id, entry.name, entry.amount, entry.category] for entry in entries
        ]
        headers = ["ID", "Name", "Amount", "Category"]
        click.echo(tabulate(table, headers=headers, tablefmt="grid"))

@cli.command()
def init_db():
    models.init_db()





app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("home.html")

@app.route("/hello/")
@app.route("/hello/<name>")
def hello(name=None):
    return render_template("home.html", name=name)



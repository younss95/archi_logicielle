import click
import csv

import archilog.models as models
import archilog.services as services

from tabulate import tabulate
from flask import Flask, render_template, request, redirect, url_for, flash, Response
import archilog.models as models
from archilog.services import import_from_csv, export_to_csv



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
app.secret_key = 'test'


@app.route("/")
def hello_world():
    return render_template("home.html")

@app.route("/hello/")
@app.route("/hello/<name>")
def hello(name=None):
    return render_template("home.html", name=name)

@app.route("/")
def home():
    return render_template("home.html")


#CREATION DES ROUTES POUR LES DIFFERENTES FONCTIONS

@app.route("/create", methods=["GET", "POST"])
def create_product():
    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"] or None

        models.create_entry(name, amount, category)
        return redirect(url_for("home"))
    return render_template("create.html")

@app.route("/delete", methods=["GET", "POST"])
def delete_product():
    products = models.get_all_entries()

    if request.method == "POST":
        product_id = request.form.get("id")
        if product_id:
            models.delete_entry(int(product_id))
            return redirect(url_for("delete_product"))

    return render_template("delete.html", products=products)


@app.route("/get", methods=["GET", "POST"])
def get_product():
    product = None
    if request.method == "POST":
        product_id = request.form["id"]
        product = models.get_entry(product_id)
    return render_template("get.html", product=product)

@app.route("/get_all")
def get_all_products():
    products = models.get_all_entries()
    return render_template("get_all.html", products=products)

@app.route("/update", methods=["GET", "POST"])
def update_product():
    if request.method == "POST":
        product_id = request.form["id"]
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"] or None

        models.update_entry(product_id, name, amount, category)
        return redirect(url_for("home"))
    return render_template("update.html")


@app.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    if request.method == "POST":
        file = request.files.get("csv_file")

        if file and file.filename.endswith('.csv'):
            import_from_csv(file)
            flash("Fichier CSV importé avec succès!")
            return redirect(url_for('import_csv'))
        else:
            flash("Le fichier doit être au format CSV.")
    return render_template("import_export_csv.html")


@app.route("/export_csv", methods=["GET"])
def export_csv():
    csv_data = export_to_csv()
    response = Response(csv_data.getvalue(), content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response

if __name__ == "__main__":
    app.run(debug=True)

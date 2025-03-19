from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, abort
import archilog.models as models
from archilog.services import import_from_csv, export_to_csv


# Création du Blueprint
web_ui = Blueprint("web_ui", __name__, url_prefix="/")

@web_ui.route("/")
def home():
    return render_template("home.html")

@web_ui.route("/create", methods=["GET", "POST"])
def create_product():
    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"] or None

        models.create_entry(name, amount, category)
        return redirect(url_for("web_ui.home"))  # Correction du nom de l'endpoint
    return render_template("create.html")

@web_ui.route("/delete", methods=["GET", "POST"])
def delete_product():
    products = models.get_all_entries()

    if request.method == "POST":
        product_id = request.form.get("id")
        if product_id:
            models.delete_entry(int(product_id))
            return redirect(url_for("web_ui.delete_product"))  # Correction

    return render_template("delete.html", products=products)

@web_ui.route("/get", methods=["GET", "POST"])
def get_product():
    product = None
    if request.method == "POST":
        product_id = request.form["id"]
        product = models.get_entry(product_id)
    return render_template("get.html", product=product)

@web_ui.route("/get_all")
def get_all_products():
    products = models.get_all_entries()
    return render_template("get_all.html", products=products)

@web_ui.route("/update", methods=["GET", "POST"])
def update_product():
    if request.method == "POST":
        product_id = request.form["id"]
        name = request.form["name"]
        amount = float(request.form["amount"])
        category = request.form["category"] or None

        models.update_entry(product_id, name, amount, category)
        return redirect(url_for("web_ui.home"))
    return render_template("update.html")

@web_ui.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    if request.method == "POST":
        file = request.files.get("csv_file")

        if file and file.filename.endswith('.csv'):
            import_from_csv(file)
            flash("Fichier CSV importé avec succès!")
            return redirect(url_for('web_ui.import_csv'))  # Correction
        else:
            flash("Le fichier doit être au format CSV.")
    return render_template("import_export_csv.html")

@web_ui.route("/export_csv", methods=["GET"])
def export_csv():
    csv_data = export_to_csv()
    response = Response(csv_data.getvalue(), content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response


@web_ui.get("/users/create")
def users_create_form():
    abort(500)  # Provoque l'erreur 500
    return render_template("users_create_form.html")

@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    return redirect(url_for("web_ui.home"))
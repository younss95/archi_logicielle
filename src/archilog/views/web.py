from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, abort
from wtforms.fields.numeric import DecimalField
from wtforms.widgets.core import HiddenInput

import archilog.models as models
from archilog.services import import_from_csv, export_to_csv
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional
from wtforms import SubmitField

# Création du Blueprint
web_ui = Blueprint("web_ui", __name__, url_prefix="/")

@web_ui.route("/")
def home():
    return render_template("home.html")

@web_ui.route("/create", methods=["GET", "POST"])
def create_product():
    form = CreateProductForm()

    if form.validate_on_submit():  # Si le formulaire est validé
        name = form.name.data
        amount = form.amount.data
        category = form.category.data or None  # Si category est vide, on le met à None

        # Création de l'entrée dans la base de données
        models.create_entry(name, amount, category)

        flash(f"Produit '{name}' créé avec succès!", "success")
        return redirect(url_for("web_ui.home"))  # Redirige après création

    return render_template("create.html", form=form)


@web_ui.route("/delete", methods=["GET", "POST"])
def delete_product():
    form = DeleteProductForm()
    products = models.get_all_entries()

    if form.validate_on_submit():
        product_id = form.product_id.data
        if product_id:
            # Suppression du produit par son ID
            models.delete_entry(int(product_id))
            flash("Produit supprimé avec succès!", "success")
            return redirect(url_for("web_ui.delete_product"))

    return render_template("delete.html", form=form, products=products)


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
    form = UpdateProductForm()
    product = None

    if request.method == "POST" and form.validate_on_submit():
        product_id = form.product_id.data
        name = form.name.data
        amount = form.amount.data
        category = form.category.data or None

        # Mise à jour du produit dans la base de données
        models.update_entry(product_id, name, amount, category)

        flash(f"Produit '{name}' mis à jour avec succès!", "success")
        return redirect(url_for("web_ui.home"))

    # Si on est en GET, on récupère l'ID du produit à mettre à jour
    product_id = request.args.get("id")
    if product_id:
        product = models.get_entry(product_id)
        form.product_id.data = product.id  # Récupérer l'ID du produit et le mettre dans le formulaire
        form.name.data = product.name
        form.amount.data = product.amount
        form.category.data = product.category

    return render_template("update.html", form=form, product=product)


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

@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    return redirect(url_for("web_ui.home"))

# PARTIE VALIDATION ET TRACABILITE

class CreateProductForm(FlaskForm):
    name = StringField("Nom du produit", validators=[DataRequired()], id="name-id")
    amount = DecimalField("Montant", places=2, validators=[DataRequired()], id="amount-id")
    category = StringField("Catégorie", validators=[Optional()], id="category-id")
    submit = SubmitField("Soumettre")  # Ajout du bouton de soumission


class DeleteProductForm(FlaskForm):
    product_id = StringField("ID du produit", validators=[DataRequired()])
    submit = SubmitField("Supprimer")



class UpdateProductForm(FlaskForm):
    product_id = StringField("ID du produit", validators=[DataRequired(), Optional()])
    name = StringField("Nom du produit", validators=[DataRequired()])
    amount = DecimalField("Montant", places=2, validators=[DataRequired()])
    category = StringField("Catégorie", validators=[Optional()])
    submit = SubmitField("Mettre à jour")

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, abort
from wtforms.fields.choices import SelectField

import archilog.models as models
from archilog.services import import_from_csv, export_to_csv
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Optional
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

# Utilisateurs avec leurs mots de passe hachés
users = {
    "john": generate_password_hash("hello"),
    "admin": generate_password_hash("admin")
}

# Exemple de fonction pour obtenir les rôles d'un utilisateur
def get_roles(username):
    roles = {
        "john": ["user"],  # John a le rôle 'user'
        "admin": ["admin"]  # Susan a le rôle 'admin'
    }
    return roles.get(username, [])

# Vérification de l'utilisateur et du mot de passe
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# Récupération des rôles de l'utilisateur
@auth.get_user_roles
def get_user_roles(username):
    return get_roles(username)




# Création du Blueprint
web_ui = Blueprint("web_ui", __name__, url_prefix="/")

@web_ui.route("/")
def home():
    logging.info("Page d'accueil demandée.")
    return render_template("home.html")

@web_ui.route("/create", methods=["GET", "POST"])
@auth.login_required(role="admin")  # Seuls les admins peuvent créer un produit
def create_product():
    form = CreateProductForm()

    if form.validate_on_submit():
        name = form.name.data
        amount = form.amount.data
        category = form.category.data or None

        models.create_entry(name, amount, category)

        flash(f"Produit '{name}' créé avec succès!", "success")
        logging.info(f"Produit '{name}' créé par {auth.current_user()}.")
        return redirect(url_for("web_ui.home"))

    return render_template("create.html", form=form)

@web_ui.route("/delete", methods=["GET", "POST"])
@auth.login_required(role="admin")  # Seuls les admins peuvent supprimer un produit
def delete_product():
    form = DeleteProductForm()
    products = models.get_all_entries()
    form.product_id.choices = [(p.id, p.name) for p in products]



    if form.validate_on_submit():
        product_id = form.product_id.data
        product = models.get_entry(product_id)

        if product is None:
            flash("Produit non trouvé.", "error")
            return redirect(url_for("web_ui.delete_product"))

        models.delete_entry(product_id)
        flash("Produit supprimé avec succès.", "success")
        logging.info(f"Produit {product_id} supprimé par {auth.current_user()}.")
        return redirect(url_for("web_ui.delete_product"))

    return render_template("delete.html", form=form)

@web_ui.route("/get", methods=["GET", "POST"])
def get_product():
    product = None
    if request.method == "POST":
        product_id = request.form["id"]
        try:
            product = models.get_entry(product_id)
            logging.info(f"Produit avec ID {product_id} recherché.")
        except Exception as e:
            flash("Produit non trouvé. Veuillez vérifier l'ID.", "error")
            logging.warning(f"Tentative d'accès à un produit inexistant (ID: {product_id}).")

    return render_template("get.html", product=product)

@web_ui.route("/get_all")
def get_all_products():
    products = models.get_all_entries()
    logging.info(f"Demande de tous les produits. Nombre de produits: {len(products)}.")
    return render_template("get_all.html", products=products)

@web_ui.route("/update", methods=["GET", "POST"])
@auth.login_required(role="admin")  # Seuls les admins peuvent mettre à jour un produit
def update_product():
    form = UpdateProductForm()
    product = None

    if request.method == "POST" and form.validate_on_submit():
        product_id = form.product_id.data
        name = form.name.data
        amount = form.amount.data
        category = form.category.data or None

        try:
            product = models.get_entry(product_id)
        except Exception:
            flash("Produit non trouvé.", "error")
            return redirect(url_for("web_ui.update_product"))

        models.update_entry(product_id, name, amount, category)
        flash(f"Produit '{name}' mis à jour!", "success")
        logging.info(f"Produit {product_id} mis à jour par {auth.current_user()}.")
        return redirect(url_for("web_ui.home"))

    return render_template("update.html", form=form, product=product)


@web_ui.route("/import_csv", methods=["GET", "POST"])
@auth.login_required(role="admin")  # Seuls les admins peuvent créer un produit
def import_csv():
    if request.method == "POST":
        file = request.files.get("csv_file")

        if file and file.filename.endswith('.csv'):
            import_from_csv(file)
            flash("Fichier CSV importé avec succès!")
            logging.info(f"Fichier CSV importé: {file.filename}.")
            return redirect(url_for('web_ui.import_csv'))
        else:
            flash("Le fichier doit être au format CSV.")
            logging.warning("Le fichier importé n'est pas au format CSV.")

    return render_template("import_export_csv.html")

@web_ui.route("/export_csv", methods=["GET"])
def export_csv():
    csv_data = export_to_csv()
    response = Response(csv_data.getvalue(), content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    logging.info("Export des données en CSV demandé.")
    return response

@web_ui.get("/users/create")
def users_create_form():
    abort(500)  # Provoque l'erreur 500

@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    logging.error(f"Erreur interne du serveur: {error}")
    return redirect(url_for("web_ui.home"))


# PARTIE VALIDATION ET TRACABILITE

class CreateProductForm(FlaskForm):
    name = StringField("Nom du produit", validators=[DataRequired()], id="name-id")
    amount = FloatField("Montant", places=2, validators=[DataRequired()], id="amount-id")
    category = StringField("Catégorie", validators=[Optional()], id="category-id")
    submit = SubmitField("Soumettre")  # Ajout du bouton de soumission



class DeleteProductForm(FlaskForm):
    product_id = SelectField("Sélectionnez un produit à supprimer", coerce=int)
    submit = SubmitField("Supprimer")



class UpdateProductForm(FlaskForm):
    product_id = IntegerField("ID du produit", validators=[DataRequired(), Optional()])
    name = StringField("Nom du produit", validators=[DataRequired()])
    amount = DecimalField("Montant", places=2, validators=[DataRequired()])
    category = StringField("Catégorie", validators=[Optional()])
    submit = SubmitField("Mettre à jour")

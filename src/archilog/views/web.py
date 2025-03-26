import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, abort
import archilog.models as models
from archilog.services import import_from_csv, export_to_csv
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

# Utilisateurs avec leurs mots de passe hachés
users = {
    "john": generate_password_hash("hello"),
    "susan": generate_password_hash("bye")
}

# Exemple de fonction pour obtenir les rôles d'un utilisateur
def get_roles(username):
    roles = {
        "john": ["user"],  # John a le rôle 'user'
        "susan": ["admin"]  # Susan a le rôle 'admin'
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
def create_product():
    form = CreateProductForm()

    if form.validate_on_submit():  # Si le formulaire est validé
        name = form.name.data
        amount = form.amount.data
        category = form.category.data or None  # Si category est vide, on le met à None

        # Création de l'entrée dans la base de données
        models.create_entry(name, amount, category)

        flash(f"Produit '{name}' créé avec succès!", "success")
        logging.info(f"Produit '{name}' créé avec montant {amount} et catégorie {category}.")
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
            logging.info(f"Produit avec ID {product_id} supprimé.")
            return redirect(url_for("web_ui.delete_product"))

    return render_template("delete.html", form=form, products=products)

@web_ui.route("/get", methods=["GET", "POST"])
def get_product():
    product = None
    if request.method == "POST":
        product_id = request.form["id"]
        product = models.get_entry(product_id)
        logging.info(f"Produit avec ID {product_id} recherché.")
    return render_template("get.html", product=product)

@web_ui.route("/get_all")
def get_all_products():
    products = models.get_all_entries()
    logging.info(f"Demande de tous les produits. Nombre de produits: {len(products)}.")
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
        logging.info(f"Produit avec ID {product_id} mis à jour avec nouveau nom '{name}', montant {amount}, catégorie {category}.")
        return redirect(url_for("web_ui.home"))

    # Si on est en GET, on récupère l'ID du produit à mettre à jour
    product_id = request.args.get("id")
    if product_id:
        product = models.get_entry(product_id)
        form.product_id.data = product.id
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

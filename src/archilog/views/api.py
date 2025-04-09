from flask import Blueprint, jsonify, Response, request
from spectree import SpecTree, SecurityScheme
from pydantic import BaseModel, Field
from archilog import models
from archilog.services import export_to_csv
from flask_httpauth import HTTPTokenAuth
import csv
import io


# Authentification token
auth_token = HTTPTokenAuth(scheme="Bearer")

TOKENS = {
    "admin": "admin",
    "user": "user"
}

@auth_token.verify_token
def verify_token(token):
    if token in TOKENS:
        return TOKENS[token]
    return None

# Blueprint API
api_ui = Blueprint("api_ui", __name__, url_prefix="/api")

# Spectree pour validation et Swagger
spec = SpecTree(
    "flask",
    security_schemes=[
        SecurityScheme(name="bearer_token", data={"type": "http", "scheme": "bearer"})
    ],
    security=[{"bearer_token": []}]
)
spec.register(api_ui)

# Schémas Pydantic
class Product(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    amount: float = Field(gt=0)
    category: str | None = None

class DeleteRequest(BaseModel):
    product_id: int

# Routes API

@api_ui.route("/products", methods=["POST"])
@spec.validate(json=Product, tags=["api"])
@auth_token.login_required
def create_product_api(json: Product):
    models.create_entry(json.name, json.amount, json.category)
    return jsonify({"message": f"Produit '{json.name}' créé"}), 201

@api_ui.route("/products", methods=["GET"])
@spec.validate(tags=["api"])
@auth_token.login_required
def get_all_products_api():
    products = models.get_all_entries()
    return jsonify(products)

@api_ui.route("/products/delete", methods=["POST"])
@spec.validate(json=DeleteRequest, tags=["api"])
@auth_token.login_required
def delete_product_api(json: DeleteRequest):
    models.delete_entry(json.product_id)
    return jsonify({"message": f"Produit {json.product_id} supprimé"}), 200

@api_ui.route("/products/export", methods=["GET"])
@spec.validate(tags=["api"])
@auth_token.login_required
def export_csv_api():
    csv_data = export_to_csv()
    return Response(csv_data.getvalue(), content_type="text/csv")


@api_ui.route("/products/<int:product_id>", methods=["DELETE"])
@spec.validate(tags=["api"])
@auth_token.login_required
def delete_product_by_id_api(product_id: int):
    product = models.get_entry(product_id)
    if product is None:
        return jsonify({"error": "Produit non trouvé"}), 404
    models.delete_entry(product_id)
    return jsonify({"message": f"Produit {product_id} supprimé"}), 200


@api_ui.route("/products/<int:product_id>", methods=["GET"])
@spec.validate(tags=["api"])
@auth_token.login_required
def get_product_api(product_id: int):
    product = models.get_entry(product_id)
    if product is None:
        return jsonify({"error": "Produit non trouvé"}), 404
    return jsonify(product)


@api_ui.route("/products/<int:product_id>", methods=["PUT"])
@spec.validate(json=Product, tags=["api"])
@auth_token.login_required
def update_product_by_id_api(product_id: int, json: Product):
    try:
        models.get_entry(product_id)  # Vérifie l'existence
    except Exception:
        return jsonify({"error": "Produit non trouvé"}), 404

    models.update_entry(product_id, json.name, json.amount, json.category)
    return jsonify({
        "message": f"Produit {product_id} mis à jour",
        "product": {
            "id": product_id,
            "name": json.name,
            "amount": json.amount,
            "category": json.category
        }
    }), 200



# Correction pour l'importation du fichier CSV
@api_ui.route("/products/import", methods=["POST"])
@auth_token.login_required
def import_csv_api():
    # Vérifie qu'un fichier a bien été envoyé dans la requête
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400

    file = request.files['file']

    # Vérifie que le fichier a bien un nom
    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400

    # Vérifie que le fichier est bien au format CSV
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Format non supporté. Veuillez envoyer un fichier CSV."}), 400

    try:
        # Lis le contenu du fichier CSV
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        count = 0
        for row in reader:
            name = row.get("name")
            amount = float(row.get("amount", 0))
            category = row.get("category") or None

            # Si le nom et le montant sont valides, ajoute l'entrée
            if name and amount > 0:
                models.create_entry(name, amount, category)
                count += 1

        return jsonify({"message": f"{count} produits importés avec succès."}), 201

    except Exception as e:
        # En cas d'erreur, renvoie un message d'erreur
        return jsonify({"error": f"Erreur lors de l'importation : {str(e)}"}), 500
from flask import Blueprint, jsonify, Response, request
from spectree import SpecTree, SecurityScheme, BaseFile
from pydantic import BaseModel, Field
from archilog import models
from archilog.services import export_to_csv, import_from_csv
from flask_httpauth import HTTPTokenAuth
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
        return {"role": TOKENS[token]}  # <- dictionnaire attendu
    return None


@auth_token.get_user_roles
def get_user_roles(user):
    return user.get("role", [])

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

class FileUploadForm(BaseModel):
    file: str = Field(..., description="Nom du fichier CSV à importer")

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
        models.get_entry(product_id)
    except KeyError:  # ou une autre exception selon ton modèle
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


class File(BaseModel):
    file : BaseFile




@api_ui.route("import/files", methods=["POST"])
@spec.validate(tags=["api"])
@auth_token.login_required(role="admin")
def import_file_api():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"error": "Fichier manquant"}), 400

    filestream = io.StringIO(uploaded_file.read().decode("utf-8"))
    import_from_csv(filestream)
    return jsonify({"message": "Import du fichier"}), 200

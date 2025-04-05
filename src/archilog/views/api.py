from flask import Blueprint, jsonify, Response
from spectree import SpecTree, SecurityScheme
from pydantic import BaseModel, Field
from archilog import models
from archilog.services import export_to_csv
from flask_httpauth import HTTPTokenAuth

# Authentification token
auth_token = HTTPTokenAuth(scheme="Bearer")

TOKENS = {
    "secret-token-admin": "admin",
    "secret-token-user": "user"
}

@auth_token.verify_token
def verify_token(token):
    return TOKENS.get(token)

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

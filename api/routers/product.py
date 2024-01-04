from datetime import datetime
from typing import List
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from api.endpoints.exception_handler import exception_handler
from api.models.financial_product import FinancialProduct
from api.models.user import User
from api.security.authentication import get_user_disabled_current
from api.db.database import database as db


router = APIRouter()
products = db.products
now = datetime.now()


@router.get("/financial-products/")
def get_all_products(user: User = Depends(get_user_disabled_current)):
    all_records = [x for x in products.find()]
    product_ids = [str(product["_id"]) for product in all_records]
    cleaned_products = [
        {**product, "_id": str(product["_id"])} for product in all_records
    ]

    return {
        "message": "List of products",
        "products_ids": product_ids,
        "result": cleaned_products,
    }


@router.get("/financial-products/{product_id}", response_model=FinancialProduct)
def get_user_by_id(
    product_id: str, current_user: User = Depends(get_user_disabled_current)
):
    product = products.find_one({"_id": ObjectId(product_id)})

    if product:
        product["_id"] = str(product["_id"])
        return product
    else:
        raise exception_handler("404_NOT_FOUND")


@router.post("/financial-products/", response_model=dict)
def create_financial_product(
    financial_product: FinancialProduct,
    current_user: User = Depends(get_user_disabled_current),
):
    product_data = financial_product.__dict__
    product_data["created_by"] = current_user.username
    product_data["created_at"] = datetime.timestamp(now)

    if current_user.role == "admin":
        result = products.insert_one(product_data)
        product_data["_id"] = str(product_data["_id"])
        if result.inserted_id:
            return {
                "message": "Financial product created successfully",
                "financial_product": product_data,
            }
        else:
            raise exception_handler("500_CREATE")

    else:
        raise exception_handler("403_NOT_ALLOWED")


@router.put("/financial-products/{product_id}", response_model=dict)
def update_financial_product(
    product_id: str,
    product_data: FinancialProduct,
    current_user: User = Depends(get_user_disabled_current),
):
    obj_id = ObjectId(product_id)
    existing_product = products.find_one({"_id": obj_id})

    if existing_product is None:
        raise exception_handler("404_NOT_FOUND")

    for field, value in product_data.dict(exclude_unset=True).items():
        existing_product[field] = value

    existing_product.update(
        {"updated_by": current_user.username, "updated_at": datetime.timestamp(now)}
    )

    result = products.update_one({"_id": obj_id}, {"$set": existing_product})
    existing_product["_id"] = str(existing_product["_id"])

    if result.modified_count == 1:
        return {
            "message": "Financial product updated successfully",
            "data": existing_product,
        }
    elif result.modified_count == 0:
        raise exception_handler("422_UNPROCESSABLE_ENTITY")
    else:
        raise exception_handler("500_UPDATE")


@router.delete("/financial-products/{product_id}")
def delete_product_by_id(
    product_id: str, current_user: User = Depends(get_user_disabled_current)
):
    result = products.delete_one({"_id": ObjectId(product_id)})

    if result.deleted_count == 1:
        return {"message": f"Product with ID {product_id} deleted successfully"}
    else:
        raise exception_handler("404_NOT_FOUND")


@router.delete("/financial-products/")
def delete_products(
    user: User = Depends(get_user_disabled_current),
    ids: List[str] = Body(..., required=True),
):
    if not ids:
        raise exception_handler("422_NO_ID")

    object_ids = [ObjectId(id) for id in ids]
    deleted_count = products.delete_many({"_id": {"$in": object_ids}})

    if deleted_count.deleted_count == 0:
        raise exception_handler("404_NOT_FOUND")

    return {
        "message": "Products deleted",
        "deleted_count": deleted_count.deleted_count,
    }

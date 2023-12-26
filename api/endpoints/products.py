from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from api.models.products import FinancialProduct
from api.models.user import User
from api.security.authentication import get_user_disabled_current
from api.db.database import database as db


router = APIRouter()
products = db.products
now = datetime.now()


@router.get("/financial-products/")
def get_all_products(user: User = Depends(get_user_disabled_current)):
    all_records = [x for x in products.find()]
    cleaned_products = [
        {**product, "_id": str(product["_id"])} for product in all_records
    ]

    return {
        "message": "List of products",
        "result": cleaned_products,
        "author": user,
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
        raise HTTPException(status_code=404, detail="Financial product not found")


@router.post("/financial-products/", response_model=FinancialProduct)
def create_financial_product(
    financial_product: FinancialProduct,
    current_user: User = Depends(get_user_disabled_current),
):
    product_data = financial_product.__dict__
    product_data["created_by"] = current_user.username
    product_data["created_at"] = datetime.timestamp(now)

    if current_user.role == "admin":
        result = products.insert_one(product_data)
        if result.inserted_id:
            return {
                "message": "Financial product created successfully",
                "product_id": str(result.inserted_id),
            }
        else:
            raise HTTPException(
                status_code=500, detail="Error creating financial product"
            )
    else:
        raise HTTPException(
            status_code=401, detail="You do not have permissions for this action"
        )


@router.put("/financial-products/{product_id}", response_model=dict)
def update_financial_product(
    product_id: str,
    product_data: FinancialProduct,
    current_user: User = Depends(get_user_disabled_current),
):
    obj_id = ObjectId(product_id)
    existing_product = products.find_one({"_id": obj_id})

    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

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
            "product_id": product_id,
            "data": existing_product,
        }
    else:
        raise HTTPException(status_code=500, detail="Error updating financial product")


@router.delete("/financial-products/{product_id}")
def delete_product_by_id(
    product_id: str, current_user: User = Depends(get_user_disabled_current)
):
    result = products.delete_one({"_id": ObjectId(product_id)})

    if result.deleted_count == 1:
        return {"message": f"Product with ID {product_id} deleted successfully"}
    else:
        raise HTTPException(
            status_code=404, detail=f"Product with ID {product_id} not found"
        )

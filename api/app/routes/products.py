from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.app.database import get_db

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products(limit: int = 20, category: str | None = None, db: Session = Depends(get_db)):
    if category:
        query = text("""
            SELECT
                product_id,
                product_name,
                category,
                subcategory,
                brand,
                color,
                price_incl_tax,
                stock_quantity,
                image_code,
                is_active
            FROM core.products
            WHERE is_active = TRUE
              AND category = :category
            ORDER BY product_id
            LIMIT :limit
        """)
        params = {"limit": limit, "category": category}
    else:
        query = text("""
            SELECT
                product_id,
                product_name,
                category,
                subcategory,
                brand,
                color,
                price_incl_tax,
                stock_quantity,
                image_code,
                is_active
            FROM core.products
            WHERE is_active = TRUE
            ORDER BY product_id
            LIMIT :limit
        """)
        params = {"limit": limit}

    result = db.execute(query, params).mappings().all()
    return [dict(row) for row in result]


@router.get("/{product_id}")
def get_product(product_id: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            product_id,
            product_name,
            category,
            subcategory,
            brand,
            color,
            size,
            material,
            manufacturing_country,
            price_excl_tax,
            tax_rate,
            price_incl_tax,
            stock_quantity,
            supplier_id,
            image_code,
            is_active
        FROM core.products
        WHERE product_id = :product_id
    """)

    result = db.execute(query, {"product_id": product_id}).mappings().first()

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    return dict(result)

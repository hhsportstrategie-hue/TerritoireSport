"""
Helper pagination
"""
from fastapi import Query

def pagination_params(
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(50, ge=1, le=500, description="Taille de page")
):
    return {"offset": (page - 1) * page_size, "limit": page_size, "page": page, "page_size": page_size}

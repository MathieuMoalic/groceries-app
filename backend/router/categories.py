from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.crud.categories import (
    create_category,
    delete_category,
    read_categories,
    update_category,
)
from backend.database import get_session
from backend.schemas.categories import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryRead, operation_id="createCategory")
def create_category_endpoint(
    category_data: CategoryCreate, session: Session = Depends(get_session)
):
    """
    Create a new category.
    """
    try:
        category = create_category(session, category_data.model_dump())
        return category
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[CategoryRead], operation_id="readAllCategory")
def read_categories_endpoint(session: Session = Depends(get_session)):
    """
    Read all categories.
    """
    categories = read_categories(session)
    return categories


@router.put("/{category_id}", response_model=CategoryRead, operation_id="readCategory")
def update_category_endpoint(
    category_id: int,
    update_data: CategoryUpdate,
    session: Session = Depends(get_session),
):
    """
    Update an existing category by ID.
    """
    category = update_category(
        session, category_id, update_data.model_dump(exclude_unset=True)
    )
    return category


@router.delete(
    "/{category_id}", response_model=CategoryRead, operation_id="deleteCategory"
)
def delete_category_endpoint(category_id: int, session: Session = Depends(get_session)):
    """
    Delete an category by ID.
    """
    category = delete_category(session, category_id)
    return category
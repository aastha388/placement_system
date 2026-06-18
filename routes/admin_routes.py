from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.models import User, College
from schemas.schemas import UserOut, CollegeCreate, CollegeOut
from auth.auth import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


# ─── User Management ─────────────────────────────────────
@router.get("/users", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    return db.query(User).all()


@router.put("/users/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/activate", response_model=UserOut)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    db.delete(user)
    db.commit()


# ─── College Management ───────────────────────────────────
@router.post("/colleges", response_model=CollegeOut, status_code=201)
def create_college(
    data: CollegeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    college = College(**data.model_dump())
    db.add(college)
    db.commit()
    db.refresh(college)
    return college


@router.get("/colleges", response_model=List[CollegeOut])
def get_colleges(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    return db.query(College).all()


@router.delete("/colleges/{college_id}", status_code=204)
def delete_college(
    college_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    db.delete(college)
    db.commit()

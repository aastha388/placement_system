from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.models import Student, User
from schemas.schemas import StudentCreate, StudentUpdate, StudentOut
from auth.auth import get_current_user, require_role

router = APIRouter(prefix="/students", tags=["Students"])


# Create student profile
@router.post("/", response_model=StudentOut, status_code=201)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    existing = db.query(Student).filter(Student.user_id == current_user.id).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Student profile already exists"
        )

    student = Student(
        **data.model_dump(),
        user_id=current_user.id
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


# Student creates own profile
@router.post("/register-profile", response_model=StudentOut, status_code=201)
def register_own_profile(
    data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Student).filter(Student.user_id == current_user.id).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    student = Student(
        **data.model_dump(),
        user_id=current_user.id
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


# Get all students
@router.get("/", response_model=List[StudentOut])
def get_all_students(
    college_id: Optional[int] = None,
    batch: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    query = db.query(Student)

    if college_id:
        query = query.filter(Student.college_id == college_id)

    if batch:
        query = query.filter(Student.batch == batch)

    return query.all()


# Get logged in student's profile
@router.get("/me", response_model=StudentOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    return student


# Get student by ID
@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


# Update student
@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if current_user.role == "student" and student.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot update another student's profile"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return student


# Delete student
@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()


# ----------------------
# FastAPI app
# ----------------------

app = FastAPI(
    title="Student API",
    version="1.0.0"
)

app.include_router(router)
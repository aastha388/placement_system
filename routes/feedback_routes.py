from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.models import InterviewFeedback, Student, User
from schemas.schemas import FeedbackCreate, FeedbackOut
from auth.auth import get_current_user, require_role

router = APIRouter(prefix="/feedback", tags=["Interview Feedback"])


@router.post("/", response_model=FeedbackOut, status_code=201)
def submit_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    feedback = InterviewFeedback(**data.model_dump(), trainer_id=current_user.id)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/student/{student_id}", response_model=List[FeedbackOut])
def get_student_feedback(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(InterviewFeedback).filter(
        InterviewFeedback.student_id == student_id
    ).order_by(InterviewFeedback.created_at.desc()).all()


@router.get("/drive/{drive_id}", response_model=List[FeedbackOut])
def get_drive_feedback(
    drive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    return db.query(InterviewFeedback).filter(
        InterviewFeedback.drive_id == drive_id
    ).all()


@router.delete("/{feedback_id}", status_code=204)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    feedback = db.query(InterviewFeedback).filter(InterviewFeedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(feedback)
    db.commit()

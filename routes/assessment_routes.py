from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.models import Assessment, AssessmentResult, Student, User
from schemas.schemas import AssessmentCreate, AssessmentOut, ResultCreate, ResultOut
from auth.auth import get_current_user, require_role

router = APIRouter(prefix="/assessments", tags=["Assessments"])


@router.post("/", response_model=AssessmentOut, status_code=201)
def create_assessment(
    data: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    assessment = Assessment(**data.model_dump(), created_by=current_user.id)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/", response_model=List[AssessmentOut])
def get_assessments(
    college_id: Optional[int] = None,
    batch: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Assessment)
    if college_id:
        query = query.filter(Assessment.college_id == college_id)
    if batch:
        query = query.filter(Assessment.batch == batch)
    return query.order_by(Assessment.scheduled_date.desc()).all()


@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.put("/{assessment_id}", response_model=AssessmentOut)
def update_assessment(
    assessment_id: int,
    data: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(assessment, field, value)

    db.commit()
    db.refresh(assessment)
    return assessment


@router.delete("/{assessment_id}", status_code=204)
def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    db.delete(assessment)
    db.commit()


# ─── Results ─────────────────────────────────────────────
@router.post("/results", response_model=ResultOut, status_code=201)
def submit_result(
    data: ResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    assessment = db.query(Assessment).filter(Assessment.id == data.assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if data.score > assessment.max_score:
        raise HTTPException(status_code=400, detail=f"Score cannot exceed max score {assessment.max_score}")

    existing = db.query(AssessmentResult).filter(
        AssessmentResult.student_id == data.student_id,
        AssessmentResult.assessment_id == data.assessment_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Result already submitted for this student")

    result = AssessmentResult(**data.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/results/assessment/{assessment_id}", response_model=List[ResultOut])
def get_results_by_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    return db.query(AssessmentResult).filter(
        AssessmentResult.assessment_id == assessment_id
    ).all()


@router.get("/results/student/{student_id}", response_model=List[ResultOut])
def get_results_by_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(AssessmentResult).filter(
        AssessmentResult.student_id == student_id
    ).all()

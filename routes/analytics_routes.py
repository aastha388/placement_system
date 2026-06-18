from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.models import Student, Attendance, AssessmentResult, DriveApplication, User, College
from schemas.schemas import StudentAnalytics
from auth.auth import get_current_user, require_role

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def compute_student_analytics(student: Student, db: Session) -> StudentAnalytics:
    attendance_records = db.query(Attendance).filter(Attendance.student_id == student.id).all()
    total = len(attendance_records)
    present = sum(1 for a in attendance_records if a.status == "present")
    attendance_pct = round((present / total) * 100, 2) if total > 0 else 0.0

    results = db.query(AssessmentResult).filter(AssessmentResult.student_id == student.id).all()
    avg_score = round(sum(r.score for r in results) / len(results), 2) if results else 0.0

    drives_applied = db.query(DriveApplication).filter(
        DriveApplication.student_id == student.id
    ).count()

    return StudentAnalytics(
        student_id=student.id,
        name=student.user.name if student.user else "Unknown",
        attendance_percentage=attendance_pct,
        average_score=avg_score,
        assessments_taken=len(results),
        drives_applied=drives_applied,
        placement_status=student.placement_status
    )


@router.get("/student/{student_id}", response_model=StudentAnalytics)
def get_student_analytics(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")
    return compute_student_analytics(student, db)


@router.get("/college/{college_id}", response_model=List[StudentAnalytics])
def get_college_analytics(
    college_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    students = db.query(Student).filter(Student.college_id == college_id).all()
    return [compute_student_analytics(s, db) for s in students]


@router.get("/batch/{batch}", response_model=List[StudentAnalytics])
def get_batch_analytics(
    batch: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    students = db.query(Student).filter(Student.batch == batch).all()
    return [compute_student_analytics(s, db) for s in students]


@router.get("/placement-summary")
def placement_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    colleges = db.query(College).all()
    summary = []

    for college in colleges:
        students = db.query(Student).filter(Student.college_id == college.id).all()
        total = len(students)
        placed = sum(1 for s in students if s.placement_status == "placed")
        summary.append({
            "college_id": college.id,
            "college_name": college.name,
            "total_students": total,
            "placed": placed,
            "unplaced": total - placed,
            "placement_rate": round((placed / total) * 100, 2) if total > 0 else 0.0
        })

    return summary

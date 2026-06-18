from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from database import get_db
from models.models import Attendance, Student
from schemas.schemas import AttendanceCreate, AttendanceOut, AttendanceSummary
from auth.auth import get_current_user, require_role
from models.models import User

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/", response_model=AttendanceOut, status_code=201)
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    attendance = Attendance(**data.model_dump(), marked_by=current_user.id)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.post("/bulk", response_model=List[AttendanceOut], status_code=201)
def mark_bulk_attendance(
    records: List[AttendanceCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    attendances = []
    for record in records:
        student = db.query(Student).filter(Student.id == record.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {record.student_id} not found")
        attendance = Attendance(**record.model_dump(), marked_by=current_user.id)
        db.add(attendance)
        attendances.append(attendance)

    db.commit()
    for a in attendances:
        db.refresh(a)
    return attendances


@router.get("/student/{student_id}", response_model=List[AttendanceOut])
def get_student_attendance(
    student_id: int,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    if from_date:
        query = query.filter(Attendance.date >= from_date)
    if to_date:
        query = query.filter(Attendance.date <= to_date)
    return query.order_by(Attendance.date.desc()).all()


@router.get("/summary/{student_id}", response_model=AttendanceSummary)
def get_attendance_summary(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    if not records:
        return AttendanceSummary(
            student_id=student_id, total=0, present=0,
            absent=0, late=0, percentage=0.0
        )

    total = len(records)
    present = sum(1 for r in records if r.status == "present")
    absent = sum(1 for r in records if r.status == "absent")
    late = sum(1 for r in records if r.status == "late")
    percentage = round((present / total) * 100, 2)

    return AttendanceSummary(
        student_id=student_id,
        total=total,
        present=present,
        absent=absent,
        late=late,
        percentage=percentage
    )


@router.get("/batch/{batch}", response_model=List[AttendanceOut])
def get_batch_attendance(
    batch: str,
    date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    students = db.query(Student).filter(Student.batch == batch).all()
    student_ids = [s.id for s in students]

    query = db.query(Attendance).filter(Attendance.student_id.in_(student_ids))
    if date:
        query = query.filter(func.date(Attendance.date) == date.date())
    return query.all()

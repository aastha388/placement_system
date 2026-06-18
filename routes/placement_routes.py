from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.models import PlacementDrive, DriveApplication, Student, Attendance, AssessmentResult, User
from schemas.schemas import DriveCreate, DriveOut, ApplicationCreate, ApplicationUpdate, ApplicationOut
from auth.auth import get_current_user, require_role

router = APIRouter(prefix="/placements", tags=["Placement Drives"])


@router.post("/drives", response_model=DriveOut, status_code=201)
def create_drive(
    data: DriveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    drive = PlacementDrive(**data.model_dump(), created_by=current_user.id)
    db.add(drive)
    db.commit()
    db.refresh(drive)
    return drive


@router.get("/drives", response_model=List[DriveOut])
def get_drives(
    college_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(PlacementDrive)
    if college_id:
        query = query.filter(PlacementDrive.college_id == college_id)
    return query.order_by(PlacementDrive.drive_date.desc()).all()


@router.get("/drives/{drive_id}", response_model=DriveOut)
def get_drive(
    drive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    drive = db.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Placement drive not found")
    return drive


@router.delete("/drives/{drive_id}", status_code=204)
def delete_drive(
    drive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    drive = db.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")
    db.delete(drive)
    db.commit()


# ─── Applications ─────────────────────────────────────────
@router.post("/apply", response_model=ApplicationOut, status_code=201)
def apply_to_drive(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    drive = db.query(PlacementDrive).filter(PlacementDrive.id == data.drive_id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    # Check eligibility - attendance
    attendance_records = db.query(Attendance).filter(Attendance.student_id == student.id).all()
    if attendance_records:
        present = sum(1 for a in attendance_records if a.status == "present")
        attendance_pct = (present / len(attendance_records)) * 100
        if attendance_pct < drive.min_attendance:
            raise HTTPException(
                status_code=400,
                detail=f"Attendance {attendance_pct:.1f}% is below required {drive.min_attendance}%"
            )

    # Check eligibility - average score
    results = db.query(AssessmentResult).filter(AssessmentResult.student_id == student.id).all()
    if results:
        avg_score = sum(r.score for r in results) / len(results)
        if avg_score < drive.min_score:
            raise HTTPException(
                status_code=400,
                detail=f"Average score {avg_score:.1f} is below required {drive.min_score}"
            )

    existing = db.query(DriveApplication).filter(
        DriveApplication.student_id == student.id,
        DriveApplication.drive_id == data.drive_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this drive")

    application = DriveApplication(student_id=student.id, drive_id=data.drive_id)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/applications/drive/{drive_id}", response_model=List[ApplicationOut])
def get_drive_applications(
    drive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    return db.query(DriveApplication).filter(DriveApplication.drive_id == drive_id).all()


@router.get("/applications/student/{student_id}", response_model=List[ApplicationOut])
def get_student_applications(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(DriveApplication).filter(DriveApplication.student_id == student_id).all()


@router.put("/applications/{application_id}", response_model=ApplicationOut)
def update_application_status(
    application_id: int,
    data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "trainer"))
):
    application = db.query(DriveApplication).filter(DriveApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = data.status

    if data.status == "selected":
        student = db.query(Student).filter(Student.id == application.student_id).first()
        if student:
            student.placement_status = "placed"

    db.commit()
    db.refresh(application)
    return application

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    trainer = "trainer"
    student = "student"


class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"
    late = "late"


class DriveStatus(str, Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    selected = "selected"
    rejected = "rejected"


# ─── Auth ───────────────────────────────────────────────
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.student


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── College ─────────────────────────────────────────────
class CollegeCreate(BaseModel):
    name: str
    location: Optional[str] = None


class CollegeOut(BaseModel):
    id: int
    name: str
    location: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Student ─────────────────────────────────────────────
class StudentCreate(BaseModel):
    college_id: int
    batch: str
    phone: Optional[str] = None
    skills: Optional[str] = None
    resume_url: Optional[str] = None


class StudentUpdate(BaseModel):
    batch: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[str] = None
    resume_url: Optional[str] = None
    placement_status: Optional[str] = None


class StudentOut(BaseModel):
    id: int
    user_id: int
    college_id: int
    batch: str
    phone: Optional[str]
    skills: Optional[str]
    resume_url: Optional[str]
    placement_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Attendance ──────────────────────────────────────────
class AttendanceCreate(BaseModel):
    student_id: int
    date: datetime
    status: AttendanceStatus
    remarks: Optional[str] = None


class AttendanceOut(BaseModel):
    id: int
    student_id: int
    date: datetime
    status: AttendanceStatus
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    student_id: int
    total: int
    present: int
    absent: int
    late: int
    percentage: float


# ─── Assessment ──────────────────────────────────────────
class AssessmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    batch: Optional[str] = None
    college_id: int
    max_score: float = 100
    scheduled_date: Optional[datetime] = None


class AssessmentOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    batch: Optional[str]
    college_id: int
    max_score: float
    scheduled_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ResultCreate(BaseModel):
    student_id: int
    assessment_id: int
    score: float
    remarks: Optional[str] = None


class ResultOut(BaseModel):
    id: int
    student_id: int
    assessment_id: int
    score: float
    remarks: Optional[str]
    submitted_at: datetime

    class Config:
        from_attributes = True


# ─── Placement Drive ─────────────────────────────────────
class DriveCreate(BaseModel):
    company_name: str
    job_role: Optional[str] = None
    package: Optional[str] = None
    college_id: int
    drive_date: Optional[datetime] = None
    min_attendance: float = 75.0
    min_score: float = 50.0
    description: Optional[str] = None


class DriveOut(BaseModel):
    id: int
    company_name: str
    job_role: Optional[str]
    package: Optional[str]
    college_id: int
    drive_date: Optional[datetime]
    min_attendance: float
    min_score: float
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    drive_id: int


class ApplicationUpdate(BaseModel):
    status: DriveStatus


class ApplicationOut(BaseModel):
    id: int
    student_id: int
    drive_id: int
    status: DriveStatus
    applied_at: datetime

    class Config:
        from_attributes = True


# ─── Feedback ────────────────────────────────────────────
class FeedbackCreate(BaseModel):
    student_id: int
    drive_id: int
    round_name: str
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    remarks: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    student_id: int
    drive_id: int
    trainer_id: int
    round_name: str
    technical_score: Optional[float]
    communication_score: Optional[float]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Analytics ───────────────────────────────────────────
class StudentAnalytics(BaseModel):
    student_id: int
    name: str
    attendance_percentage: float
    average_score: float
    assessments_taken: int
    drives_applied: int
    placement_status: str

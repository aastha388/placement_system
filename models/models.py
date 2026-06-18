from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class RoleEnum(str, enum.Enum):
    admin = "admin"
    trainer = "trainer"
    student = "student"


class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"
    late = "late"


class DriveStatus(str, enum.Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    selected = "selected"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.student)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="user", uselist=False)


class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    students = relationship("Student", back_populates="college")
    placement_drives = relationship("PlacementDrive", back_populates="college")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    college_id = Column(Integer, ForeignKey("colleges.id"))
    batch = Column(String)
    phone = Column(String)
    skills = Column(Text)
    resume_url = Column(String)
    placement_status = Column(String, default="unplaced")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="student")
    college = relationship("College", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")
    results = relationship("AssessmentResult", back_populates="student")
    drive_applications = relationship("DriveApplication", back_populates="student")
    feedbacks = relationship("InterviewFeedback", back_populates="student")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    marked_by = Column(Integer, ForeignKey("users.id"))
    remarks = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="attendances")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    batch = Column(String)
    college_id = Column(Integer, ForeignKey("colleges.id"))
    max_score = Column(Float, default=100)
    scheduled_date = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    results = relationship("AssessmentResult", back_populates="assessment")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    score = Column(Float)
    remarks = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="results")
    assessment = relationship("Assessment", back_populates="results")


class PlacementDrive(Base):
    __tablename__ = "placement_drives"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    job_role = Column(String)
    package = Column(String)
    college_id = Column(Integer, ForeignKey("colleges.id"))
    drive_date = Column(DateTime(timezone=True))
    min_attendance = Column(Float, default=75.0)
    min_score = Column(Float, default=50.0)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    college = relationship("College", back_populates="placement_drives")
    applications = relationship("DriveApplication", back_populates="drive")


class DriveApplication(Base):
    __tablename__ = "drive_applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    drive_id = Column(Integer, ForeignKey("placement_drives.id"))
    status = Column(Enum(DriveStatus), default=DriveStatus.applied)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student", back_populates="drive_applications")
    drive = relationship("PlacementDrive", back_populates="applications")


class InterviewFeedback(Base):
    __tablename__ = "interview_feedback"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    drive_id = Column(Integer, ForeignKey("placement_drives.id"))
    trainer_id = Column(Integer, ForeignKey("users.id"))
    round_name = Column(String)
    technical_score = Column(Float)
    communication_score = Column(Float)
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="feedbacks")

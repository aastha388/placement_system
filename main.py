from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import (
    auth_routes,
    student_routes,
    attendance_routes,
    assessment_routes,
    placement_routes,
    feedback_routes,
    analytics_routes,
    admin_routes
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Placement Management System",
    description="A FastAPI backend for managing student profiles, attendance, assessments, placement drives, and analytics across multiple colleges.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(student_routes.router)
app.include_router(attendance_routes.router)
app.include_router(assessment_routes.router)
app.include_router(placement_routes.router)
app.include_router(feedback_routes.router)
app.include_router(analytics_routes.router)
app.include_router(admin_routes.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Student Placement Management System API",
        "docs": "/docs",
        "status": "running"
    }

# Student Placement Management System — Backend

A FastAPI backend with JWT authentication and Supabase (PostgreSQL) database.

---

## Project Structure

```
placement_system/
├── main.py               # App entry point
├── database.py           # Supabase DB connection
├── requirements.txt
├── .env.example
├── models/
│   └── models.py         # SQLAlchemy table models
├── schemas/
│   └── schemas.py        # Pydantic request/response schemas
├── auth/
│   └── auth.py           # JWT logic & role guards
└── routes/
    ├── auth_routes.py     # /auth
    ├── student_routes.py  # /students
    ├── attendance_routes.py # /attendance
    ├── assessment_routes.py # /assessments
    ├── placement_routes.py  # /placements
    ├── feedback_routes.py   # /feedback
    ├── analytics_routes.py  # /analytics
    └── admin_routes.py      # /admin
```

---

## Setup Steps

### 1. Clone & Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Supabase
- Go to https://supabase.com → New Project
- Settings → Database → Copy connection string
- Create `.env` file from `.env.example`:
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Run the Server
```bash
uvicorn main:app --reload
```

### 5. Test APIs
Open: http://127.0.0.1:8000/docs

---

## API Endpoints

| Module | Method | Endpoint | Role |
|---|---|---|---|
| Auth | POST | /auth/register | Public |
| Auth | POST | /auth/login | Public |
| Auth | GET | /auth/me | All |
| Students | GET/POST | /students | Admin/Trainer |
| Students | GET/PUT | /students/{id} | All |
| Attendance | POST | /attendance | Trainer |
| Attendance | POST | /attendance/bulk | Trainer |
| Attendance | GET | /attendance/summary/{id} | All |
| Assessments | GET/POST | /assessments | All |
| Assessments | POST | /assessments/results | Trainer |
| Placements | POST | /placements/drives | Trainer |
| Placements | POST | /placements/apply | Student |
| Placements | PUT | /placements/applications/{id} | Trainer |
| Feedback | POST | /feedback | Trainer |
| Feedback | GET | /feedback/student/{id} | All |
| Analytics | GET | /analytics/student/{id} | All |
| Analytics | GET | /analytics/college/{id} | Admin/Trainer |
| Analytics | GET | /analytics/placement-summary | Admin |
| Admin | GET | /admin/users | Admin |
| Admin | POST | /admin/colleges | Admin |

---

## Roles
- **admin** — Full access
- **trainer** — Manage students, assessments, drives, feedback
- **student** — View own data, apply for drives

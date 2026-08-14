import sys
import os
import time
import logging
from typing import Optional, List

# Ensure backend directory is in sys.path when running from root folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Base, engine

from models import User, Project, Task
from schemas import (
    UserCreate,
    UserResponse,
    ProjectCreate,
    ProjectResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from deps import get_db
from algorithms import insertion_sort, binary_search, linear_search
from parser import parse_task_description

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskflow")

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="Full-stack task management system with integrated algorithms engine and AI quick-add parser",
    version="1.0.0",
)

# --- Task 8: Explicit CORS Setup ---
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)


# --- Task 7: Custom Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} completed in {duration_ms:.2f}ms")
    return response


# --- Section 1: User Endpoints ---
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered",
        )
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# --- Section 1: Project Endpoints ---
@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    owner = db.query(User).filter(User.id == project.owner_id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {project.owner_id} not found",
        )
    db_project = Project(
        title=project.title,
        description=project.description,
        owner_id=project.owner_id,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@app.get("/projects", response_model=List[ProjectResponse], status_code=status.HTTP_200_OK)
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@app.get("/projects/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    return project


# --- Section 1 Task 5: SQL Aggregation Statistics Endpoint ---
@app.get("/projects/{project_id}/stats", status_code=status.HTTP_200_OK)
def get_project_stats(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Compute aggregate counts directly in SQL query across join of Project and Task
    total_count = (
        db.query(func.count(Task.id))
        .select_from(Project)
        .join(Task, Project.id == Task.project_id)
        .filter(Project.id == project_id)
        .scalar()
    ) or 0

    status_counts = (
        db.query(Task.status, func.count(Task.id))
        .select_from(Project)
        .join(Task, Project.id == Task.project_id)
        .filter(Project.id == project_id)
        .group_by(Task.status)
        .all()
    )

    priority_counts = (
        db.query(Task.priority, func.count(Task.id))
        .select_from(Project)
        .join(Task, Project.id == Task.project_id)
        .filter(Project.id == project_id)
        .group_by(Task.priority)
        .all()
    )

    return {
        "project_id": project_id,
        "project_title": project.title,
        "total_tasks": total_count,
        "by_status": dict(status_counts),
        "by_priority": dict(priority_counts),
    }


# --- Section 1 CRUD Tasks & Section 2 Algorithms Integration ---

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {task.project_id} not found",
        )
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        due_date=task.due_date,
        project_id=task.project_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks/search", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def search_tasks(
    title: str = Query(..., description="Exact title text to search for"),
    algo: str = Query("binary", description="Search algorithm: binary or linear"),
    db: Session = Depends(get_db),
):
    """
    Section 2 Task 4: In-memory search using hand-rolled binary_search or linear_search over an index built from DB rows.
    """
    all_tasks = db.query(Task).all()
    if not all_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with exact title '{title}' not found",
        )

    # Build in-memory index
    task_index = [{"id": t.id, "title": t.title, "task_obj": t} for t in all_tasks]

    matched_index = -1
    if algo.lower() == "binary":
        # Sort index by title using insertion_sort
        insertion_sort(task_index, key="title")
        matched_index = binary_search(task_index, target_value=title, key="title")
    else:
        matched_index = linear_search(task_index, target_value=title, key="title")

    if matched_index != -1:
        return task_index[matched_index]["task_obj"]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with exact title '{title}' not found",
    )


@app.get("/tasks", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def list_tasks(
    project_id: Optional[int] = None,
    sort: Optional[str] = None,
    priority: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """
    Section 1 List Tasks + Section 2 Task 4 Sorting via hand-rolled insertion_sort algorithm.
    """
    query = db.query(Task)
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    if priority:
        query = query.filter(Task.priority == priority)
    if status_filter:
        query = query.filter(Task.status == status_filter)

    tasks_from_db = query.all()

    if sort:
        # Convert ORM objects to list of dicts for insertion_sort
        priority_rank_map = {"low": 1, "medium": 2, "high": 3}
        task_dicts = []
        for t in tasks_from_db:
            td = {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "priority_rank": priority_rank_map.get(t.priority, 2),
                "status": t.status,
                "due_date": t.due_date or "",
                "project_id": t.project_id,
                "orm_obj": t,
            }
            task_dicts.append(td)

        if sort == "priority":
            insertion_sort(task_dicts, key="priority_rank")
        elif sort == "due_date":
            insertion_sort(task_dicts, key="due_date")

        # Extract sorted list of ORM objects
        return [td["orm_obj"] for td in task_dicts]

    return tasks_from_db


@app.get("/tasks/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    update_data = task_update.model_dump(exclude_unset=True)
    if "project_id" in update_data and update_data["project_id"] is not None:
        project = db.query(Project).filter(Project.id == update_data["project_id"]).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {update_data['project_id']} not found",
            )

    for field, val in update_data.items():
        if val is not None:
            setattr(task, field, val)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    db.delete(task)
    db.commit()
    return {"detail": f"Task {task_id} deleted successfully"}


# --- Section 3: AI Quick-Add Endpoint ---
class QuickAddRequest(BaseModel):
    description: str
    project_id: int


@app.post("/tasks/quick-add", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def quick_add_task(payload: QuickAddRequest, db: Session = Depends(get_db)):
    """
    Accepts free text description and project_id, parses using the AI parser,
    validates using TaskCreate model, and creates a database task record.
    """
    # Check if project exists
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Project with id {payload.project_id} does not exist",
        )

    # Parse description using parser logic
    parsed_data = parse_task_description(payload.description)

    # Validate parsed data against Pydantic TaskCreate model
    try:
        task_create = TaskCreate(
            title=parsed_data["title"],
            priority=parsed_data["priority"],
            due_date=parsed_data["due_date_hint"],
            project_id=payload.project_id,
            status="todo",
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Parsed task validation failed: {str(err)}",
        )

    # Save to database
    db_task = Task(
        title=task_create.title,
        priority=task_create.priority,
        status=task_create.status,
        due_date=task_create.due_date,
        project_id=task_create.project_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


# --- Single-Process Frontend Mount ---
import os
from fastapi.responses import FileResponse

frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if not os.path.exists(frontend_path):
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend")

if os.path.exists(frontend_path):
    app.mount("/dashboard", StaticFiles(directory=frontend_path, html=True), name="dashboard")
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")



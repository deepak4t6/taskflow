import sys
import os
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from main import app, Base, engine

client = TestClient(app)


def test_full_suite():
    print("=== Running Complete Backend Test Suite ===")

    # 1. Reset Database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 2. Test User Endpoints
    resp = client.post("/users", json={"name": "Alice Smith", "email": "alice@blinkit.com"})
    assert resp.status_code == 201, f"User create failed: {resp.text}"
    user1 = resp.json()
    assert user1["id"] == 1
    assert user1["email"] == "alice@blinkit.com"
    print("PASS: User creation (201)")

    resp = client.get("/users")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    print("PASS: List users (200)")

    # 3. Test Project Endpoints
    resp = client.post("/projects", json={"title": "Darkstore Operations", "owner_id": 1, "description": "Pod 1 ops"})
    assert resp.status_code == 201
    proj1 = resp.json()
    assert proj1["id"] == 1
    print("PASS: Project creation (201)")

    resp = client.post("/projects", json={"title": "Cold Chain Tech", "owner_id": 1})
    assert resp.status_code == 201
    proj2 = resp.json()
    assert proj2["id"] == 2

    resp = client.get("/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    print("PASS: List projects (200)")

    # 4. Test Task Endpoints & Pydantic Validation (Section 1)
    # Valid Task Creation
    resp = client.post("/tasks", json={
        "title": "Calibrate temperature sensors",
        "priority": "high",
        "status": "todo",
        "due_date": "next friday",
        "project_id": 1
    })
    assert resp.status_code == 201
    task1 = resp.json()
    assert task1["title"] == "Calibrate temperature sensors"
    assert task1["priority"] == "high"
    print("PASS: Task creation (201)")

    # Blank title validation error (422)
    resp = client.post("/tasks", json={
        "title": "   ",
        "priority": "medium",
        "project_id": 1
    })
    assert resp.status_code == 422
    print("PASS: Blank title validation rejection (422)")

    # Invalid priority validation error (422)
    resp = client.post("/tasks", json={
        "title": "Fix scanner",
        "priority": "ultra-high",
        "project_id": 1
    })
    assert resp.status_code == 422
    print("PASS: Invalid priority validation rejection (422)")

    # Non-existent project task creation (404)
    resp = client.post("/tasks", json={
        "title": "Orphan task",
        "project_id": 9999
    })
    assert resp.status_code == 404
    print("PASS: Task creation for non-existent project (404)")

    # 5. Add more tasks for sorting and stats testing
    client.post("/tasks", json={"title": "Inventory Audit", "priority": "low", "status": "in_progress", "project_id": 1})
    client.post("/tasks", json={"title": "Restock Freezer", "priority": "medium", "status": "done", "project_id": 1})

    # 6. Test SQL Aggregation Stats Endpoint
    resp = client.get("/projects/1/stats")
    assert resp.status_code == 200
    stats = resp.json()
    assert stats["total_tasks"] == 3
    assert stats["by_status"]["todo"] == 1
    assert stats["by_status"]["in_progress"] == 1
    assert stats["by_status"]["done"] == 1
    assert stats["by_priority"]["high"] == 1
    assert stats["by_priority"]["medium"] == 1
    assert stats["by_priority"]["low"] == 1
    print("PASS: SQL aggregate project statistics endpoint")

    # Non-existent project stats (404)
    resp = client.get("/projects/999/stats")
    assert resp.status_code == 404
    print("PASS: Non-existent project statistics (404)")

    # 7. Test Section 2 Algorithm Integration (Sorting & Searching)
    # Sort by priority using hand-rolled insertion_sort
    resp = client.get("/tasks?sort=priority")
    assert resp.status_code == 200
    sorted_tasks = resp.json()
    priorities = [t["priority"] for t in sorted_tasks]
    assert priorities == ["low", "medium", "high"], f"Priority sort order incorrect: {priorities}"
    print("PASS: Hand-rolled insertion_sort endpoint (GET /tasks?sort=priority)")

    # Binary Search
    resp = client.get("/tasks/search?title=Inventory Audit&algo=binary")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Inventory Audit"
    print("PASS: Hand-rolled binary search endpoint (GET /tasks/search?algo=binary)")

    # Linear Search
    resp = client.get("/tasks/search?title=Restock Freezer&algo=linear")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Restock Freezer"
    print("PASS: Hand-rolled linear search endpoint (GET /tasks/search?algo=linear)")

    # Search absent task (404)
    resp = client.get("/tasks/search?title=NonExistentTask&algo=binary")
    assert resp.status_code == 404
    print("PASS: Binary search absent task (404)")

    # 8. Test Section 3 AI Quick-Add Endpoint
    resp = client.post("/tasks/quick-add", json={
        "description": "Fix darkstore conveyor belt ASAP, deadline is tomorrow",
        "project_id": 1
    })
    assert resp.status_code == 201
    qa_task = resp.json()
    assert qa_task["title"] == "Fix darkstore conveyor belt , deadline is"
    assert qa_task["priority"] == "high"
    assert qa_task["due_date"] == "tomorrow"
    print("PASS: Section 3 AI Quick-Add endpoint (POST /tasks/quick-add)")

    # Quick-add for non-existent project (422)
    resp = client.post("/tasks/quick-add", json={
        "description": "Fix scanner urgent",
        "project_id": 9999
    })
    assert resp.status_code == 422
    print("PASS: Quick-Add non-existent project rejection (422)")

    # 9. Test CRUD Update & Delete
    resp = client.put(f"/tasks/{task1['id']}", json={"status": "done"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"
    print("PASS: Task update (200)")

    resp = client.delete(f"/tasks/{task1['id']}")
    assert resp.status_code == 200
    print("PASS: Task deletion (200)")

    resp = client.get(f"/tasks/{task1['id']}")
    assert resp.status_code == 404
    print("PASS: Get deleted task returns 404")

    print("\nALL BACKEND TEST SUITE CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_full_suite()

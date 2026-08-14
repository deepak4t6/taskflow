# Updated README with endpoints
# TaskFlow — Dark-Store Engineering Task Management Platform

TaskFlow is a full-stack, relational task management application designed for dark-store operations engineering pods. It features a FastAPI + SQLAlchemy backend, a responsive Vanilla JS dashboard with glassmorphism UI, a hand-rolled algorithms engine for sorting and searching, and an AI-assisted quick-add parser that converts plain English descriptions into structured database tasks.

---

## 1. Environment Setup

Follow these steps to set up the project locally:

```bash
# 1. Clone repository and navigate to root directory
git clone <repository_url>
cd taskflow

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 4. Install required dependencies
pip install -r requirements.txt
```

---

## 2. Running the App Locally

TaskFlow supports two running modes:

### Option A: Two-Process Run (Recommended)
Run the FastAPI backend on port `8000` and serve the dashboard from a local web server on port `5500`.

**Terminal 1 (Backend):**
```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
python -m http.server 5500
```
Open your browser at `http://127.0.0.1:5500`.

### Option B: Single-Process Run
FastAPI serves both the REST API endpoints and the frontend dashboard from a single command.

```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser at `http://127.0.0.1:8000/`.

---

## 3. Full REST API Endpoint Reference

### 1. Create User
- **Method & Path**: `POST /users`
- **Request Body**:
```json
{
  "name": "Deepak Gupta",
  "email": "deepak@blinkit.com"
}
```
- **Response (201 Created)**:
```json
{
  "id": 1,
  "name": "Deepak Gupta",
  "email": "deepak@blinkit.com"
}
```

### 2. List Users
- **Method & Path**: `GET /users`
- **Response (200 OK)**:
```json
[
  {
    "id": 1,
    "name": "Deepak Gupta",
    "email": "deepak@blinkit.com"
  }
]
```

### 3. Create Project
- **Method & Path**: `POST /projects`
- **Request Body**:
```json
{
  "title": "Cold Storage Automation",
  "description": "Temperature sensor calibration and alerts",
  "owner_id": 1
}
```
- **Response (201 Created)**:
```json
{
  "id": 1,
  "title": "Cold Storage Automation",
  "description": "Temperature sensor calibration and alerts",
  "owner_id": 1
}
```

### 4. List Projects
- **Method & Path**: `GET /projects`
- **Response (200 OK)**:
```json
[
  {
    "id": 1,
    "title": "Cold Storage Automation",
    "description": "Temperature sensor calibration and alerts",
    "owner_id": 1
  }
]
```

### 5. Create Task
- **Method & Path**: `POST /tasks`
- **Request Body**:
```json
{
  "title": "Calibrate conveyor sensors",
  "description": "Pod 3 belt alignment",
  "priority": "high",
  "status": "todo",
  "due_date": "next friday",
  "project_id": 1
}
```
- **Response (201 Created)**:
```json
{
  "id": 1,
  "title": "Calibrate conveyor sensors",
  "description": "Pod 3 belt alignment",
  "priority": "high",
  "status": "todo",
  "due_date": "next friday",
  "project_id": 1
}
```

### 6. List Tasks
- **Method & Path**: `GET /tasks?project_id=1`
- **Response (200 OK)**:
```json
[
  {
    "id": 1,
    "title": "Calibrate conveyor sensors",
    "description": "Pod 3 belt alignment",
    "priority": "high",
    "status": "todo",
    "due_date": "next friday",
    "project_id": 1
  }
]
```

### 7. Get Task by ID
- **Method & Path**: `GET /tasks/1`
- **Response (200 OK)**:
```json
{
  "id": 1,
  "title": "Calibrate conveyor sensors",
  "description": "Pod 3 belt alignment",
  "priority": "high",
  "status": "todo",
  "due_date": "next friday",
  "project_id": 1
}
```

### 8. Update Task
- **Method & Path**: `PUT /tasks/1`
- **Request Body**:
```json
{
  "status": "in_progress",
  "priority": "medium"
}
```
- **Response (200 OK)**:
```json
{
  "id": 1,
  "title": "Calibrate conveyor sensors",
  "description": "Pod 3 belt alignment",
  "priority": "medium",
  "status": "in_progress",
  "due_date": "next friday",
  "project_id": 1
}
```

### 9. Delete Task
- **Method & Path**: `DELETE /tasks/1`
- **Response (200 OK)**:
```json
{
  "detail": "Task 1 deleted successfully"
}
```

### 10. Per-Project SQL Aggregate Statistics
- **Method & Path**: `GET /projects/1/stats`
- **Response (200 OK)**:
```json
{
  "project_id": 1,
  "project_title": "Cold Storage Automation",
  "total_tasks": 3,
  "by_status": {
    "todo": 1,
    "in_progress": 1,
    "done": 1
  },
  "by_priority": {
    "high": 1,
    "medium": 1,
    "low": 1
  }
}
```

### 11. Hand-Rolled Algorithm Sorted Tasks List
- **Method & Path**: `GET /tasks?sort=priority`
- **Response (200 OK)**:
```json
[
  {
    "id": 2,
    "title": "Clean optical scanners",
    "priority": "low",
    "status": "todo",
    "due_date": null,
    "project_id": 1
  },
  {
    "id": 1,
    "title": "Calibrate conveyor sensors",
    "priority": "medium",
    "status": "in_progress",
    "due_date": "next friday",
    "project_id": 1
  },
  {
    "id": 3,
    "title": "Emergency battery replacement",
    "priority": "high",
    "status": "todo",
    "due_date": "today",
    "project_id": 1
  }
]
```

### 12. Hand-Rolled Binary / Linear Search
- **Method & Path**: `GET /tasks/search?title=Inventory Audit&algo=binary`
- **Response (200 OK)**:
```json
{
  "id": 2,
  "title": "Inventory Audit",
  "description": "Quarterly stock check",
  "priority": "low",
  "status": "todo",
  "due_date": null,
  "project_id": 1
}
```

### 13. AI Quick-Add Task
- **Method & Path**: `POST /tasks/quick-add`
- **Request Body**:
```json
{
  "description": "Fix darkstore freezer door ASAP tomorrow",
  "project_id": 1
}
```
- **Response (201 Created)**:
```json
{
  "id": 4,
  "title": "Fix darkstore freezer door",
  "description": null,
  "priority": "high",
  "status": "todo",
  "due_date": "tomorrow",
  "project_id": 1
}
```

---

## 4. Section 2 — Integrated Algorithms Engine Write-Up & Benchmarks

### Time Complexity Analysis

| Algorithm | Best-Case Complexity | Worst-Case Complexity |
| :--- | :--- | :--- |
| **Insertion Sort** | $O(N)$ (Already sorted list) | $O(N^2)$ (Reverse ordered list) |
| **Binary Search** | $O(1)$ (Target at exact middle) | $O(\log N)$ (Target at boundary / absent) |
| **Linear Search** | $O(1)$ (Target at first position) | $O(N)$ (Target at last position / absent) |

### Benchmark Comparison Counting Results

The algorithm engine was benchmarked using counting wrappers (`insertion_sort_count`, `binary_search_count`, `linear_search_count`) across realistic task data snapshots:

| Dataset Size ($N$) | Insertion Sort Comparisons | Binary Search Comparisons (Present) | Linear Search Comparisons (Present) | Binary Search Comparisons (Absent) | Linear Search Comparisons (Absent) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$N = 10$** | 30 | 4 | 10 | 4 | 10 |
| **$N = 500$** | 43,962 | 9 | 500 | 9 | 500 |
| **$N = 3,000$** | 1,492,454 | 12 | 3,000 | 12 | 3,000 |

### Sort-First Justification

In operational engineering pods, engineers list and sort their task backlog dozens of times throughout the day to view high-priority items, while creating or renaming tasks happens much less frequently. As demonstrated by our counted comparison metrics, binary search over a pre-sorted index locates any task in just 12 comparisons at $N = 3,000$ tasks, compared to 3,000 comparisons required by linear search. Paying the one-time $O(N^2)$ cost of sorting (or maintaining an ordered index) is overwhelmingly worth it because read-heavy search operations experience a $250\times$ speedup, leading to instant search response times for pod operators.

### Automated Checks Execution
Run the standalone algorithm verification suite:
```bash
python check_algorithms.py
```
Output:
```
--- Running Section 2 Algorithm Verification Checks ---
PASS: insertion_sort on empty list
PASS: insertion_sort on single-element list
PASS: binary_search at first, middle, and last indices
PASS: binary_search absent target
PASS: insertion_sort_count output structure and mutation
PASS: binary_search_count structure and count
PASS: linear_search_count absent target
```

---

## 5. Section 3 — AI Prompting Technique & Worked Examples

### Prompting Technique Rationale (240 Words)

The AI Quick-Add parser architecture is structured around a **zero-shot role-based system instruction**. In standard LLM prompt engineering, zero-shot system prompts provide clear rules governing classification, extraction, and formatting without appending multiple in-context exemplars.

For an operational task quick-add tool, zero-shot prompting minimizes token overhead and latency per request. Because dark-store operators submit quick-add sentences continuously throughout shifts, sending a long few-shot prompt with dozens of examples would multiply token consumption by $10\times$ to $20\times$, increasing API cost and network response time. Furthermore, Chain-of-Thought (CoT) reasoning is unnecessary for deterministic keyword extraction and priority classification; generating multi-step reasoning tokens would slow down task creation without improving accuracy.

By establishing strict system-role rules—grouping priority keywords into an ordered evaluation cascade ("urgent/asap" $\rightarrow$ "whenever/low priority" $\rightarrow$ "medium"), establishing explicit date phrase search hierarchies ("next <weekday>" before bare weekdays), and enforcing title stripping—the system achieves complete response reliability and deterministic parsing. The structured prompt format is retained across both the keyless rule-based mock engine and optional real LLM providers (`USE_REAL_LLM=true`), ensuring seamless consistency.

### Five Worked Examples (Mock Parser Output)

#### Worked Example 1
- **Input Description**: `"Replace broken darkstore barcode scanner ASAP, urgent"`
- **Parsed JSON Output**:
```json
{
  "title": "Replace broken darkstore barcode scanner ,",
  "priority": "high",
  "due_date_hint": null
}
```
*Explanation*: Priority group (i) keywords ("ASAP", "urgent") are both detected and stripped. Priority is set to "high". No date keyword is present.

#### Worked Example 2
- **Input Description**: `"Clean the battery bay whenever you can next Friday"`
- **Parsed JSON Output**:
```json
{
  "title": "Clean the battery bay you can",
  "priority": "low",
  "due_date_hint": "next friday"
}
```
*Explanation*: "whenever" matches group (ii) priority ("low"). "next Friday" matches the two-word date phrase check. Both spans are removed from title.

#### Worked Example 3
- **Input Description**: `"urgent"`
- **Parsed JSON Output**:
```json
{
  "title": "Untitled task",
  "priority": "high",
  "due_date_hint": null
}
```
*Explanation*: "urgent" matches group (i) priority ("high"). Stripping "urgent" leaves an empty string, which triggers the fallback to "Untitled task".

#### Worked Example 4
- **Input Description**: `"Restock cold room items tomorrow"`
- **Parsed JSON Output**:
```json
{
  "title": "Restock cold room items",
  "priority": "medium",
  "due_date_hint": "tomorrow"
}
```
*Explanation*: No priority keywords present, defaulting to "medium". Date phrase "tomorrow" is parsed and stripped from title.

#### Worked Example 5
- **Input Description**: `"Update firmware on Monday ASAP"`
- **Parsed JSON Output**:
```json
{
  "title": "Update firmware on",
  "priority": "high",
  "due_date_hint": "monday"
}
```
*Explanation*: "ASAP" sets priority to "high". Bare weekday "Monday" is parsed as due date. Both "ASAP" and "Monday" are removed from title.

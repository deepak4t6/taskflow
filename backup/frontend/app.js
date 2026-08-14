/**
 * TaskFlow Command Center JavaScript
 * Full-stack FastAPI integration with safe DOM updates, localStorage fallback cache,
 * client-side validation, prompt chips, and toast feedback system.
 */

const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.port === '5500'
  ? 'http://127.0.0.1:8000'
  : window.location.origin.includes('8000') ? window.location.origin : 'http://127.0.0.1:8000';

const LOCAL_STORAGE_KEY = 'taskflow_cached_tasks_v2';

// Application State
let currentUsers = [];
let currentProjects = [];
let selectedProjectId = null;
let currentTasks = [];

// DOM Element References
const userSelect = document.getElementById('user-select');
const newUserBtn = document.getElementById('new-user-btn');
const projectListEl = document.getElementById('project-list');
const newProjectBtn = document.getElementById('new-project-btn');
const statsContentEl = document.getElementById('stats-content');

const addTaskForm = document.getElementById('add-task-form');
const taskTitleInput = document.getElementById('task-title-input');
const titleErrorMsg = document.getElementById('title-error-msg');
const taskPrioritySelect = document.getElementById('task-priority-select');
const taskStatusSelect = document.getElementById('task-status-select');
const taskDueInput = document.getElementById('task-due-input');
const taskProjectSelect = document.getElementById('task-project-select');
const taskDescInput = document.getElementById('task-desc-input');

const quickAddForm = document.getElementById('quick-add-form');
const quickAddInput = document.getElementById('quick-add-input');

const sortSelect = document.getElementById('sort-select');
const filterStatusSelect = document.getElementById('filter-status');
const searchTitleInput = document.getElementById('search-title-input');
const searchAlgoSelect = document.getElementById('search-algo-select');
const searchBtn = document.getElementById('search-btn');
const clearSearchBtn = document.getElementById('clear-search-btn');

const taskListContainer = document.getElementById('task-list-container');
const taskCountBadge = document.getElementById('task-count-badge');

const userModal = document.getElementById('user-modal');
const closeUserModal = document.getElementById('close-user-modal');
const userForm = document.getElementById('user-form');

const projectModal = document.getElementById('project-modal');
const closeProjectModal = document.getElementById('close-project-modal');
const projectForm = document.getElementById('project-form');

const toastContainer = document.getElementById('toast-container');

// --- Application Lifecycle ---
document.addEventListener('DOMContentLoaded', () => {
  // 1. Render cached tasks first (prevents blank screen during network call)
  loadTasksFromCache();

  // 2. Fetch live data from backend
  initApp();

  // 3. Attach interactive handlers
  setupEventListeners();
});

// --- Toast System ---
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = 'toast';
  if (type === 'error') toast.style.borderLeftColor = 'var(--accent-rose)';
  if (type === 'success') toast.style.borderLeftColor = 'var(--accent-emerald)';
  toast.textContent = message;

  toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// --- LocalStorage Caching ---
function loadTasksFromCache() {
  try {
    const cachedData = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (cachedData) {
      const tasks = JSON.parse(cachedData);
      if (Array.isArray(tasks) && tasks.length > 0) {
        currentTasks = tasks;
        renderTaskList(currentTasks);
      }
    }
  } catch (err) {
    console.warn('LocalStorage load warning:', err);
  }
}

function updateTasksCache(tasks) {
  try {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(tasks));
  } catch (err) {
    console.warn('LocalStorage save warning:', err);
  }
}

// --- App Bootstrap ---
async function initApp() {
  await fetchUsers();
  await fetchProjects();

  if (currentProjects.length > 0) {
    selectProject(currentProjects[0].id);
  } else {
    fetchTasks();
  }
}

// --- API Service Layer ---
async function fetchUsers() {
  try {
    const res = await fetch(`${API_BASE_URL}/users`);
    if (res.ok) {
      currentUsers = await res.json();
      renderUserSelect();
    }
  } catch (err) {
    console.error('Error fetching users:', err);
  }
}

async function fetchProjects() {
  try {
    const res = await fetch(`${API_BASE_URL}/projects`);
    if (res.ok) {
      currentProjects = await res.json();
      renderProjectList();
      renderProjectDropdown();
    }
  } catch (err) {
    console.error('Error fetching projects:', err);
  }
}

async function fetchTasks() {
  try {
    let url = `${API_BASE_URL}/tasks?`;
    const params = new URLSearchParams();

    if (selectedProjectId) {
      params.append('project_id', selectedProjectId);
    }

    const sortVal = sortSelect.value;
    if (sortVal) {
      params.append('sort', sortVal);
    }

    const statusVal = filterStatusSelect.value;
    if (statusVal) {
      params.append('status', statusVal);
    }

    url += params.toString();

    const res = await fetch(url);
    if (res.ok) {
      currentTasks = await res.json();
      renderTaskList(currentTasks);
      updateTasksCache(currentTasks);
    }
  } catch (err) {
    console.error('Error fetching tasks:', err);
  }
}

async function fetchProjectStats(projectId) {
  if (!projectId) return;
  try {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/stats`);
    if (res.ok) {
      const stats = await res.json();
      renderStatsPanel(stats);
    }
  } catch (err) {
    console.error('Error fetching stats:', err);
  }
}

// --- Event Listeners Setup ---
function setupEventListeners() {
  // Real-time title validation feedback
  taskTitleInput.addEventListener('input', () => {
    if (taskTitleInput.value.trim().length > 0) {
      hideTitleError();
    }
  });

  // Prompt Chips auto-fill
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      quickAddInput.value = chip.getAttribute('data-text');
      quickAddInput.focus();
    });
  });

  // Add Structured Task Form Submission
  addTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = taskTitleInput.value.trim();
    if (!title) {
      showTitleError('Task title is required and cannot be blank');
      return;
    }
    hideTitleError();

    const projectId = parseInt(taskProjectSelect.value, 10);
    if (!projectId) {
      alert('Please create a project first!');
      return;
    }

    const payload = {
      title: title,
      description: taskDescInput.value.trim() || null,
      priority: taskPrioritySelect.value,
      status: taskStatusSelect.value,
      due_date: taskDueInput.value.trim() || null,
      project_id: projectId,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.status === 201) {
        taskTitleInput.value = '';
        taskDescInput.value = '';
        taskDueInput.value = '';
        showToast('Task created successfully!', 'success');
        await fetchTasks();
        if (selectedProjectId) fetchProjectStats(selectedProjectId);
      } else {
        const errorData = await res.json();
        showToast(`Error: ${errorData.detail || 'Validation error'}`, 'error');
      }
    } catch (err) {
      console.error('Task creation error:', err);
    }
  });

  // AI Quick-Add Form Submission
  quickAddForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const desc = quickAddInput.value.trim();
    if (!desc) return;

    const projectId = selectedProjectId || (currentProjects.length > 0 ? currentProjects[0].id : null);
    if (!projectId) {
      showToast('Please create a project first before quick-adding tasks!', 'error');
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/tasks/quick-add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: desc, project_id: projectId }),
      });

      if (res.status === 201) {
        quickAddInput.value = '';
        showToast('AI Quick-Add task created!', 'success');
        await fetchTasks();
        fetchProjectStats(projectId);
      } else {
        const errData = await res.json();
        showToast(`Quick-Add Error: ${JSON.stringify(errData.detail)}`, 'error');
      }
    } catch (err) {
      console.error('Quick add error:', err);
    }
  });

  // Sorting & Filtering
  sortSelect.addEventListener('change', fetchTasks);
  filterStatusSelect.addEventListener('change', fetchTasks);

  // Search Controls
  searchBtn.addEventListener('click', async () => {
    const title = searchTitleInput.value.trim();
    if (!title) return;
    const algo = searchAlgoSelect.value;

    try {
      const res = await fetch(`${API_BASE_URL}/tasks/search?title=${encodeURIComponent(title)}&algo=${algo}`);
      if (res.ok) {
        const task = await res.json();
        renderTaskList([task]);
        showToast(`Found exact match using ${algo} search!`, 'success');
      } else {
        renderTaskList([]);
        showToast(`No task found with title "${title}" (${algo} search)`, 'error');
      }
    } catch (err) {
      console.error('Search error:', err);
    }
  });

  clearSearchBtn.addEventListener('click', () => {
    searchTitleInput.value = '';
    fetchTasks();
  });

  // User Modal Management
  newUserBtn.addEventListener('click', () => userModal.style.display = 'block');
  closeUserModal.addEventListener('click', () => userModal.style.display = 'none');
  userForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('user-name-input').value.trim();
    const email = document.getElementById('user-email-input').value.trim();

    try {
      const res = await fetch(`${API_BASE_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email }),
      });

      if (res.status === 201) {
        userModal.style.display = 'none';
        userForm.reset();
        showToast('User created successfully!', 'success');
        await fetchUsers();
      } else {
        const errData = await res.json();
        alert(`Error: ${errData.detail}`);
      }
    } catch (err) {
      console.error('User creation failed:', err);
    }
  });

  // Project Modal Management
  newProjectBtn.addEventListener('click', () => projectModal.style.display = 'block');
  closeProjectModal.addEventListener('click', () => projectModal.style.display = 'none');
  projectForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('project-title-input').value.trim();
    const description = document.getElementById('project-desc-input').value.trim();
    const ownerId = parseInt(userSelect.value, 10);

    if (!ownerId) {
      alert('Please create and select a user first!');
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description, owner_id: ownerId }),
      });

      if (res.status === 201) {
        const newProj = await res.json();
        projectModal.style.display = 'none';
        projectForm.reset();
        showToast('Project created successfully!', 'success');
        await fetchProjects();
        selectProject(newProj.id);
      } else {
        const errData = await res.json();
        alert(`Error: ${errData.detail}`);
      }
    } catch (err) {
      console.error('Project creation failed:', err);
    }
  });
}

// --- Validation UI Helpers ---
function showTitleError(msg) {
  titleErrorMsg.textContent = msg;
  titleErrorMsg.classList.add('visible');
  taskTitleInput.style.borderColor = 'var(--accent-rose)';
}

function hideTitleError() {
  titleErrorMsg.textContent = '';
  titleErrorMsg.classList.remove('visible');
  taskTitleInput.style.borderColor = '';
}

// --- Safe DOM Rendering ---
function renderUserSelect() {
  userSelect.replaceChildren();
  if (currentUsers.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'No users found';
    userSelect.appendChild(opt);
    return;
  }

  currentUsers.forEach(u => {
    const opt = document.createElement('option');
    opt.value = u.id;
    opt.textContent = `${u.name} (${u.email})`;
    userSelect.appendChild(opt);
  });
}

function renderProjectList() {
  projectListEl.replaceChildren();
  currentProjects.forEach(p => {
    const li = document.createElement('li');
    li.className = `project-item ${p.id === selectedProjectId ? 'active' : ''}`;
    
    const titleSpan = document.createElement('span');
    titleSpan.textContent = p.title;

    li.appendChild(titleSpan);
    li.addEventListener('click', () => selectProject(p.id));
    projectListEl.appendChild(li);
  });
}

function renderProjectDropdown() {
  taskProjectSelect.replaceChildren();
  currentProjects.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = p.title;
    if (p.id === selectedProjectId) opt.selected = true;
    taskProjectSelect.appendChild(opt);
  });
}

function selectProject(projectId) {
  selectedProjectId = projectId;
  renderProjectList();
  renderProjectDropdown();
  fetchTasks();
  fetchProjectStats(projectId);
}

function renderStatsPanel(stats) {
  statsContentEl.replaceChildren();

  const projTitle = document.createElement('h3');
  projTitle.style.fontSize = '1.1rem';
  projTitle.style.fontWeight = '700';
  projTitle.textContent = stats.project_title;

  const totalHero = document.createElement('div');
  totalHero.className = 'stat-hero-number';
  totalHero.textContent = stats.total_tasks;

  const totalSub = document.createElement('div');
  totalSub.style.fontSize = '0.78rem';
  totalSub.style.color = 'var(--text-muted)';
  totalSub.style.marginBottom = '1rem';
  totalSub.textContent = 'Total Project Tasks (SQL Aggregate)';

  statsContentEl.appendChild(projTitle);
  statsContentEl.appendChild(totalHero);
  statsContentEl.appendChild(totalSub);

  // Status breakdown bars
  const byStatus = stats.by_status || {};
  Object.keys(byStatus).forEach(st => {
    const barWrapper = document.createElement('div');
    barWrapper.className = 'stat-bar-wrapper';

    const headerFlex = document.createElement('div');
    headerFlex.className = 'stat-header-flex';
    
    const labelSpan = document.createElement('span');
    labelSpan.textContent = st.replace('_', ' ').toUpperCase();

    const countSpan = document.createElement('span');
    countSpan.textContent = `${byStatus[st]} tasks`;

    headerFlex.appendChild(labelSpan);
    headerFlex.appendChild(countSpan);

    const track = document.createElement('div');
    track.className = 'progress-track';

    const fill = document.createElement('div');
    const pct = stats.total_tasks > 0 ? (byStatus[st] / stats.total_tasks) * 100 : 0;
    fill.className = `progress-fill ${st === 'done' ? 'fill-emerald' : st === 'in_progress' ? 'fill-indigo' : 'fill-amber'}`;
    fill.style.width = `${pct}%`;

    track.appendChild(fill);
    barWrapper.appendChild(headerFlex);
    barWrapper.appendChild(track);
    statsContentEl.appendChild(barWrapper);
  });
}

function renderTaskList(tasks) {
  taskListContainer.replaceChildren();
  taskCountBadge.textContent = `${tasks.length} tasks`;

  if (tasks.length === 0) {
    const emptyState = document.createElement('div');
    emptyState.style.padding = '2rem 1rem';
    emptyState.style.textAlign = 'center';
    emptyState.style.color = 'var(--text-muted)';
    emptyState.style.fontSize = '0.9rem';
    emptyState.textContent = 'No tasks in this backlog view.';
    taskListContainer.appendChild(emptyState);
    return;
  }

  tasks.forEach(task => {
    const card = document.createElement('div');
    card.className = 'task-item-card';

    // Content Side
    const content = document.createElement('div');
    content.className = 'task-content';

    const title = document.createElement('div');
    title.className = 'task-title-text';
    title.textContent = task.title; // Safe assignment

    content.appendChild(title);

    if (task.description) {
      const desc = document.createElement('div');
      desc.className = 'task-description-text';
      desc.textContent = task.description; // Safe assignment
      content.appendChild(desc);
    }

    const badgeRow = document.createElement('div');
    badgeRow.className = 'task-badge-row';

    const prioBadge = document.createElement('span');
    prioBadge.className = `badge badge-${task.priority}`;
    prioBadge.textContent = task.priority.toUpperCase();

    const statusBadge = document.createElement('span');
    statusBadge.className = `badge badge-${task.status}`;
    statusBadge.textContent = task.status.replace('_', ' ').toUpperCase();

    badgeRow.appendChild(prioBadge);
    badgeRow.appendChild(statusBadge);

    if (task.due_date) {
      const dueTag = document.createElement('span');
      dueTag.className = 'task-due-tag';
      dueTag.textContent = `📅 Due: ${task.due_date}`; // Safe assignment
      badgeRow.appendChild(dueTag);
    }

    content.appendChild(badgeRow);

    // Actions Side
    const actionsRow = document.createElement('div');
    actionsRow.className = 'task-actions-row';

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'btn btn-secondary btn-sm';
    toggleBtn.textContent = task.status === 'todo' ? 'Start' : task.status === 'in_progress' ? 'Complete' : 'Reopen';
    toggleBtn.addEventListener('click', async () => {
      const nextStatus = task.status === 'todo' ? 'in_progress' : task.status === 'in_progress' ? 'done' : 'todo';
      await updateTaskStatus(task.id, nextStatus);
    });

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn btn-danger btn-sm';
    deleteBtn.textContent = 'Delete';
    deleteBtn.addEventListener('click', async () => {
      if (confirm(`Delete task "${task.title}"?`)) {
        await deleteTask(task.id);
      }
    });

    actionsRow.appendChild(toggleBtn);
    actionsRow.appendChild(deleteBtn);

    card.appendChild(content);
    card.appendChild(actionsRow);

    taskListContainer.appendChild(card);
  });
}

// --- Task State Mutations ---
async function updateTaskStatus(taskId, newStatus) {
  try {
    const res = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });

    if (res.ok) {
      showToast('Task status updated', 'success');
      await fetchTasks();
      if (selectedProjectId) fetchProjectStats(selectedProjectId);
    }
  } catch (err) {
    console.error('Error updating task:', err);
  }
}

async function deleteTask(taskId) {
  try {
    const res = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
      method: 'DELETE',
    });

    if (res.ok) {
      showToast('Task deleted', 'success');
      await fetchTasks();
      if (selectedProjectId) fetchProjectStats(selectedProjectId);
    }
  } catch (err) {
    console.error('Error deleting task:', err);
  }
}

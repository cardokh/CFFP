/*
 * CCore PostgreSQL tasks page controller.
 *
 * Responsibilities:
 * - Load persisted CCore tasks from PostgreSQL through the backend API.
 * - Create, update, and delete rows in the ccore_tasks table.
 * - Keep frontend endpoint usage centralized through CCORE_API_ENDPOINTS.
 * - Provide compact CRUD UI behavior for the first CCore database slice.
 */

const CCORE_TASKS_LOADING_MESSAGE =
    "Loading CCore tasks...";

const CCORE_TASKS_EMPTY_MESSAGE =
    "No PostgreSQL tasks found.";

const CCORE_TASKS_ERROR_MESSAGE =
    "CCore tasks could not be loaded.";

const CCORE_TASKS_TABLE_COLUMN_COUNT = 4;

let ccoreTasks = [];
let ccoreTaskSearchTerm = "";


function getCCoreTasksTableBody() {
    return document.getElementById("ccoreTasksTableBody");
}


function getCCoreTasksMessage() {
    return document.getElementById("ccoreTasksMessage");
}


function escapeCCoreTaskValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function showCCoreTasksMessage(message, type = "info") {
    const messageElement = getCCoreTasksMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className = `form-message ${type}`;
    messageElement.textContent = message;
}


function hideCCoreTasksMessage() {
    const messageElement = getCCoreTasksMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className = "form-message info hidden";
    messageElement.textContent = "";
}


function renderCCoreTasksPlaceholder(message) {
    const tableBody = getCCoreTasksTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = `
        <tr>
            <td colspan="${CCORE_TASKS_TABLE_COLUMN_COUNT}" class="shared-table-empty-state">
                ${escapeCCoreTaskValue(message)}
            </td>
        </tr>
    `;
}


function normalizeCCoreTaskStatus(status) {
    return String(status || "PENDING")
        .trim()
        .toUpperCase();
}


function formatCCoreTaskDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}


function getCCoreTaskSearchableText(task) {
    return [
        task.id,
        task.taskId,
        task.name,
        task.taskName,
        task.status,
        task.createdAt
    ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
}


function getFilteredCCoreTasks() {
    const searchTerm = ccoreTaskSearchTerm.trim().toLowerCase();

    if (!searchTerm) {
        return ccoreTasks;
    }

    return ccoreTasks.filter((task) =>
        getCCoreTaskSearchableText(task).includes(searchTerm)
    );
}


function renderCCoreTaskRow(task) {
    const taskId = task.taskId || task.id;
    const taskName = task.taskName || task.name;
    const status = normalizeCCoreTaskStatus(task.status);

    return `
        <tr data-task-id="${escapeCCoreTaskValue(taskId)}">
            <td>
                <div class="ccore-task-name-cell">
                    <span class="ccore-task-name">${escapeCCoreTaskValue(taskName)}</span>
                    <span class="ccore-task-id">${escapeCCoreTaskValue(taskId)}</span>
                </div>
            </td>
            <td>
                <span class="ccore-task-status">${escapeCCoreTaskValue(status)}</span>
            </td>
            <td>${escapeCCoreTaskValue(formatCCoreTaskDate(task.createdAt))}</td>
            <td>
                <div class="ccore-task-row-actions">
                    <button class="shared-button secondary" type="button" data-action="edit" data-task-id="${escapeCCoreTaskValue(taskId)}">
                        Edit
                    </button>
                    <button class="shared-button secondary" type="button" data-action="delete" data-task-id="${escapeCCoreTaskValue(taskId)}">
                        Delete
                    </button>
                </div>
            </td>
        </tr>
    `;
}


function updateCCoreTasksCount(filteredTasks) {
    const countElement = document.getElementById("ccoreTasksCount");

    if (!countElement) {
        return;
    }

    const count = filteredTasks.length;
    countElement.textContent = `${count} ${count === 1 ? "task" : "tasks"}`;
}


function renderCCoreTasks() {
    const filteredTasks = getFilteredCCoreTasks();

    if (filteredTasks.length === 0) {
        renderCCoreTasksPlaceholder(CCORE_TASKS_EMPTY_MESSAGE);
        updateCCoreTasksCount(filteredTasks);
        return;
    }

    const tableBody = getCCoreTasksTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = filteredTasks
        .map(renderCCoreTaskRow)
        .join("");

    updateCCoreTasksCount(filteredTasks);
}


function parseCCoreTasksResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.tasks)) {
        throw new Error("The backend did not return a CCore task list.");
    }

    return responseData.tasks;
}


async function loadCCoreTasks() {
    hideCCoreTasksMessage();
    renderCCoreTasksPlaceholder(CCORE_TASKS_LOADING_MESSAGE);

    try {
        const responseData = await getJson(CCORE_API_ENDPOINTS.tasks.list);
        ccoreTasks = parseCCoreTasksResponse(responseData);

        enableCCoreTaskSearch();
        renderCCoreTasks();

        if (ccoreTasks.length === 0) {
            showCCoreTasksMessage(CCORE_TASKS_EMPTY_MESSAGE, "info");
        }

    } catch (error) {
        console.error("Failed to load CCore tasks:", error);
        ccoreTasks = [];
        renderCCoreTasksPlaceholder(CCORE_TASKS_ERROR_MESSAGE);
        showCCoreTasksMessage(error.message || CCORE_TASKS_ERROR_MESSAGE, "error");
    }
}


function getTaskFormData() {
    return {
        taskId: document.getElementById("ccoreTaskIdInput").value,
        taskName: document.getElementById("ccoreTaskNameInput").value.trim(),
        status: document.getElementById("ccoreTaskStatusInput").value
    };
}


function resetTaskForm() {
    document.getElementById("ccoreTaskIdInput").value = "";
    document.getElementById("ccoreTaskNameInput").value = "";
    document.getElementById("ccoreTaskStatusInput").value = "PENDING";
    document.getElementById("ccoreTaskFormLegend").textContent = "Create Task";
    document.getElementById("saveCCoreTaskButton").textContent = "Create Task";
}


function editTask(taskId) {
    const task = ccoreTasks.find((candidateTask) =>
        String(candidateTask.taskId || candidateTask.id) === String(taskId)
    );

    if (!task) {
        showCCoreTasksMessage("Task could not be found in the current list.", "error");
        return;
    }

    document.getElementById("ccoreTaskIdInput").value = task.taskId || task.id;
    document.getElementById("ccoreTaskNameInput").value = task.taskName || task.name || "";
    document.getElementById("ccoreTaskStatusInput").value = normalizeCCoreTaskStatus(task.status);
    document.getElementById("ccoreTaskFormLegend").textContent = "Edit Task";
    document.getElementById("saveCCoreTaskButton").textContent = "Update Task";
}


async function saveTask(event) {
    event.preventDefault();
    hideCCoreTasksMessage();

    const formData = getTaskFormData();

    if (!formData.taskName) {
        showCCoreTasksMessage("Task name is required.", "error");
        return;
    }

    try {
        if (formData.taskId) {
            await putJson(
                CCORE_API_ENDPOINTS.tasks.byId(formData.taskId),
                {
                    taskName: formData.taskName,
                    status: formData.status
                }
            );

            showCCoreTasksMessage("Task updated successfully.", "success");
        } else {
            await postJson(
                CCORE_API_ENDPOINTS.tasks.create,
                {
                    taskName: formData.taskName,
                    status: formData.status
                }
            );

            showCCoreTasksMessage("Task created successfully.", "success");
        }

        resetTaskForm();
        await loadCCoreTasks();

    } catch (error) {
        showCCoreTasksMessage(error.message || "Task could not be saved.", "error");
    }
}


async function deleteTask(taskId) {
    if (!window.confirm("Delete this CCore task?")) {
        return;
    }

    try {
        await deleteJson(CCORE_API_ENDPOINTS.tasks.byId(taskId));
        showCCoreTasksMessage("Task deleted successfully.", "success");
        resetTaskForm();
        await loadCCoreTasks();

    } catch (error) {
        showCCoreTasksMessage(error.message || "Task could not be deleted.", "error");
    }
}


function setupTaskTableActions() {
    const tableBody = getCCoreTasksTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.addEventListener("click", (event) => {
        const actionButton = event.target.closest("button[data-action]");

        if (!actionButton) {
            return;
        }

        const taskId = actionButton.dataset.taskId;
        const action = actionButton.dataset.action;

        if (action === "edit") {
            editTask(taskId);
            return;
        }

        if (action === "delete") {
            deleteTask(taskId);
        }
    });
}


function enableCCoreTaskSearch() {
    const searchInput = document.getElementById("ccoreTasksSearchInput");

    if (!searchInput) {
        return;
    }

    searchInput.disabled = false;
}


function setupCCoreTaskSearch() {
    const searchInput = document.getElementById("ccoreTasksSearchInput");

    if (!searchInput) {
        return;
    }

    searchInput.addEventListener("input", () => {
        ccoreTaskSearchTerm = searchInput.value;
        renderCCoreTasks();
    });
}


function setupCCoreTasksPage() {
    document.getElementById("ccoreTaskForm").addEventListener("submit", saveTask);
    document.getElementById("resetCCoreTaskFormButton").addEventListener("click", resetTaskForm);
    document.getElementById("refreshCCoreTasksButton").addEventListener("click", loadCCoreTasks);

    setupTaskTableActions();
    setupCCoreTaskSearch();
    loadCCoreTasks();
}


setupCCoreTasksPage();

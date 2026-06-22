/*
 * CCore PostgreSQL tasks page controller.
 *
 * Responsibilities:
 * - Load persisted CCore tasks from PostgreSQL through the backend API.
 * - Load task status options from PostgreSQL reference data.
 * - Create, update, and delete rows in the ccore_tasks table.
 * - Keep frontend endpoint usage centralized through CCORE_API_ENDPOINTS.
 * - Provide compact CRUD UI behavior for the first CCore database slice.
 */

const CCORE_TASKS_LOADING_MESSAGE =
    "Loading CCore tasks...";

const CCORE_TASK_STATUSES_LOADING_MESSAGE =
    "Loading task statuses...";

const CCORE_TASKS_EMPTY_MESSAGE =
    "No PostgreSQL tasks found.";

const CCORE_TASK_STATUSES_EMPTY_MESSAGE =
    "No task statuses are configured.";

const CCORE_TASKS_ERROR_MESSAGE =
    "CCore tasks could not be loaded.";

const CCORE_TASK_STATUSES_ERROR_MESSAGE =
    "CCore task statuses could not be loaded.";

const CCORE_TASKS_TABLE_COLUMN_COUNT = 4;

let ccoreTasks = [];
let ccoreTaskStatuses = [];
let ccoreTaskSearchTerm = "";


function getCCoreTasksTableBody() {
    return document.getElementById("ccoreTasksTableBody");
}


function getCCoreTasksMessage() {
    return document.getElementById("ccoreTasksMessage");
}


function getCCoreTaskStatusInput() {
    return document.getElementById("ccoreTaskStatusInput");
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
    return String(status || "")
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


function getDefaultCCoreTaskStatusCode() {
    if (ccoreTaskStatuses.length === 0) {
        return "";
    }

    return ccoreTaskStatuses[0].code;
}


function getCCoreTaskStatusLabel(statusCode) {
    const normalizedStatusCode = normalizeCCoreTaskStatus(statusCode);
    const status = ccoreTaskStatuses.find((candidateStatus) =>
        normalizeCCoreTaskStatus(candidateStatus.code) === normalizedStatusCode
    );

    return status ? status.label : normalizedStatusCode;
}


function getCCoreTaskSearchableText(task) {
    return [
        task.taskId,
        task.taskName,
        task.status,
        task.statusLabel,
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
    const taskId = task.taskId;
    const taskName = task.taskName;
    const status = normalizeCCoreTaskStatus(task.status);
    const statusLabel = task.statusLabel || getCCoreTaskStatusLabel(status);

    return `
        <tr data-task-id="${escapeCCoreTaskValue(taskId)}">
            <td>
                <div class="ccore-task-name-cell">
                    <span class="ccore-task-name">${escapeCCoreTaskValue(taskName)}</span>
                    <span class="ccore-task-id">${escapeCCoreTaskValue(taskId)}</span>
                </div>
            </td>
            <td>
                <span class="ccore-task-status" title="${escapeCCoreTaskValue(status)}">
                    ${escapeCCoreTaskValue(statusLabel)}
                </span>
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


function parseCCoreTaskStatusesResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.statuses)) {
        throw new Error("The backend did not return a CCore task status list.");
    }

    return responseData.statuses;
}


function renderCCoreTaskStatusOptions() {
    const statusInput = getCCoreTaskStatusInput();

    if (!statusInput) {
        return;
    }

    if (ccoreTaskStatuses.length === 0) {
        statusInput.innerHTML = `<option value="">${escapeCCoreTaskValue(CCORE_TASK_STATUSES_EMPTY_MESSAGE)}</option>`;
        statusInput.disabled = true;
        return;
    }

    statusInput.innerHTML = ccoreTaskStatuses
        .map((status) => `
            <option value="${escapeCCoreTaskValue(status.code)}">
                ${escapeCCoreTaskValue(status.label)}
            </option>
        `)
        .join("");

    statusInput.disabled = false;
}


async function loadCCoreTaskStatuses() {
    const statusInput = getCCoreTaskStatusInput();

    if (statusInput) {
        statusInput.innerHTML = `<option value="">${escapeCCoreTaskValue(CCORE_TASK_STATUSES_LOADING_MESSAGE)}</option>`;
        statusInput.disabled = true;
    }

    const responseData = await getJson(CCORE_API_ENDPOINTS.tasks.statuses);
    ccoreTaskStatuses = parseCCoreTaskStatusesResponse(responseData);
    renderCCoreTaskStatusOptions();
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
        status: getCCoreTaskStatusInput().value
    };
}


function resetTaskForm() {
    document.getElementById("ccoreTaskIdInput").value = "";
    document.getElementById("ccoreTaskNameInput").value = "";
    getCCoreTaskStatusInput().value = getDefaultCCoreTaskStatusCode();
    document.getElementById("ccoreTaskFormLegend").textContent = "Create Task";
    document.getElementById("saveCCoreTaskButton").textContent = "Create Task";
}


function editTask(taskId) {
    const task = ccoreTasks.find((candidateTask) =>
        String(candidateTask.taskId) === String(taskId)
    );

    if (!task) {
        showCCoreTasksMessage("Task could not be found in the current list.", "error");
        return;
    }

    document.getElementById("ccoreTaskIdInput").value = task.taskId;
    document.getElementById("ccoreTaskNameInput").value = task.taskName || "";
    getCCoreTaskStatusInput().value = normalizeCCoreTaskStatus(task.status);
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

    if (!formData.status) {
        showCCoreTasksMessage("Task status is required.", "error");
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


async function setupCCoreTasksPage() {
    document.getElementById("ccoreTaskForm").addEventListener("submit", saveTask);
    document.getElementById("resetCCoreTaskFormButton").addEventListener("click", resetTaskForm);
    document.getElementById("refreshCCoreTasksButton").addEventListener("click", loadCCoreTasks);

    setupTaskTableActions();
    setupCCoreTaskSearch();

    try {
        await loadCCoreTaskStatuses();
        resetTaskForm();
        await loadCCoreTasks();
    } catch (error) {
        console.error("Failed to initialize CCore tasks page:", error);
        renderCCoreTasksPlaceholder(CCORE_TASKS_ERROR_MESSAGE);
        showCCoreTasksMessage(error.message || CCORE_TASK_STATUSES_ERROR_MESSAGE, "error");
    }
}


setupCCoreTasksPage();

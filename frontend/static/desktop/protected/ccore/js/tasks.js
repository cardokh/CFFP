/*
 * CCore PostgreSQL tasks list page controller.
 *
 * Responsibilities:
 * - Load persisted CCore tasks from PostgreSQL through the backend API.
 * - Render a searchable, sortable task list.
 * - Open the task details page when a task row is selected.
 * - Keep frontend endpoint usage centralized through CCORE_API_ENDPOINTS.
 */

const CCORE_TASKS_LOADING_MESSAGE =
    "Loading CCore tasks...";

const CCORE_TASKS_EMPTY_MESSAGE =
    "No PostgreSQL tasks found.";

const CCORE_TASKS_ERROR_MESSAGE =
    "CCore tasks could not be loaded.";

const CCORE_TASKS_TABLE_COLUMN_COUNT = 3;

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


function getCCoreTaskDetailsUrl(taskId) {
    return `./task-details.html?taskId=${encodeURIComponent(taskId)}`;
}


function renderCCoreTaskRow(task) {
    const taskId = task.taskId;
    const taskName = task.taskName;
    const status = normalizeCCoreTaskStatus(task.status);
    const statusLabel = task.statusLabel || status;

    return `
        <tr data-task-id="${escapeCCoreTaskValue(taskId)}" tabindex="0" aria-label="Open task ${escapeCCoreTaskValue(taskName)}">
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


function openCCoreTaskDetails(taskId) {
    if (!taskId) {
        return;
    }

    window.location.href = getCCoreTaskDetailsUrl(taskId);
}


function setupCCoreTaskRowNavigation() {
    const tableBody = getCCoreTasksTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.addEventListener("click", (event) => {
        const taskRow = event.target.closest("tr[data-task-id]");

        if (!taskRow) {
            return;
        }

        openCCoreTaskDetails(taskRow.dataset.taskId);
    });

    tableBody.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
            return;
        }

        const taskRow = event.target.closest("tr[data-task-id]");

        if (!taskRow) {
            return;
        }

        event.preventDefault();
        openCCoreTaskDetails(taskRow.dataset.taskId);
    });
}


function enableCCoreTaskSearch() {
    const searchInput = document.getElementById("ccoreTasksSearchInput");

    if (!searchInput) {
        return;
    }

    searchInput.disabled = false;
}


function setupCCoreTaskSorting() {
    if (typeof initializeTableSorting !== "function") {
        return;
    }

    initializeTableSorting(
        document.querySelector(".ccore-tasks-table") || document
    );
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
    document.getElementById("refreshCCoreTasksButton").addEventListener("click", loadCCoreTasks);

    setupCCoreTaskRowNavigation();
    setupCCoreTaskSearch();
    setupCCoreTaskSorting();

    await loadCCoreTasks();
}


setupCCoreTasksPage();

/*
 * Automation tasks page controller.
 *
 * Responsibilities:
 * - Load registered automation tasks from CCore.
 * - Render the first end-to-end automation task list UI slice.
 * - Handle loading, empty, and error states.
 *
 * Platform dependencies are loaded by protected-workspace.js.
 */

const AUTOMATION_TASKS_EMPTY_MESSAGE =
    "No automation tasks are currently registered.";

const AUTOMATION_TASKS_LOADING_MESSAGE =
    "Loading automation tasks...";

const AUTOMATION_TASKS_ERROR_MESSAGE =
    "Automation tasks could not be loaded.";


function getAutomationTasksTableBody() {
    return document.getElementById(
        "automationTasksTableBody"
    );
}


function getAutomationTasksMessage() {
    return document.getElementById(
        "automationTasksMessage"
    );
}


function escapeAutomationTaskValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function normalizeAutomationTaskStatus(status) {
    return String(status || "unknown")
        .trim()
        .toLowerCase();
}


function showAutomationTasksMessage(message, type = "info") {
    const messageElement =
        getAutomationTasksMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        `form-message ${type}`;

    messageElement.textContent =
        message;
}


function hideAutomationTasksMessage() {
    const messageElement =
        getAutomationTasksMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        "form-message info hidden";

    messageElement.textContent =
        "";
}


function renderAutomationTasksPlaceholder(message) {
    const tableBody =
        getAutomationTasksTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="shared-table-empty-state">
                ${escapeAutomationTaskValue(message)}
            </td>
        </tr>
    `;
}


function renderAutomationTaskRow(task) {
    const status =
        normalizeAutomationTaskStatus(
            task.status
        );

    return `
        <tr>
            <td>
                <span class="automation-tasks-table-code" title="${escapeAutomationTaskValue(task.id)}">
                    ${escapeAutomationTaskValue(task.id)}
                </span>
            </td>

            <td>
                ${escapeAutomationTaskValue(task.name)}
            </td>

            <td>
                ${escapeAutomationTaskValue(task.category)}
            </td>

            <td>
                <span class="automation-tasks-status ${escapeAutomationTaskValue(status)}">
                    ${escapeAutomationTaskValue(status)}
                </span>
            </td>

            <td>
                <span class="automation-tasks-table-code" title="${escapeAutomationTaskValue(task.script_path)}">
                    ${escapeAutomationTaskValue(task.script_path)}
                </span>
            </td>

            <td>
                <span class="automation-tasks-table-code" title="${escapeAutomationTaskValue(task.config_path)}">
                    ${escapeAutomationTaskValue(task.config_path)}
                </span>
            </td>
        </tr>
    `;
}


function renderAutomationTasks(tasks) {
    const tableBody =
        getAutomationTasksTableBody();

    if (!tableBody) {
        return;
    }

    if (!Array.isArray(tasks) || tasks.length === 0) {
        renderAutomationTasksPlaceholder(
            AUTOMATION_TASKS_EMPTY_MESSAGE
        );

        return;
    }

    tableBody.innerHTML =
        tasks
            .map(renderAutomationTaskRow)
            .join("");
}


function parseAutomationTasksResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.tasks)) {
        throw new Error(
            "The backend did not return an automation task list."
        );
    }

    return responseData.tasks;
}


async function loadAutomationTasks() {
    hideAutomationTasksMessage();

    renderAutomationTasksPlaceholder(
        AUTOMATION_TASKS_LOADING_MESSAGE
    );

    try {
        const responseData =
            await getJson(
                CCORE_API_ENDPOINTS.automation.tasks.list
            );

        const tasks =
            parseAutomationTasksResponse(
                responseData
            );

        renderAutomationTasks(
            tasks
        );

        if (tasks.length === 0) {
            showAutomationTasksMessage(
                AUTOMATION_TASKS_EMPTY_MESSAGE,
                "info"
            );
        }

    } catch (error) {
        console.error(
            "Failed to load automation tasks:",
            error
        );

        renderAutomationTasksPlaceholder(
            AUTOMATION_TASKS_ERROR_MESSAGE
        );

        showAutomationTasksMessage(
            error.message || AUTOMATION_TASKS_ERROR_MESSAGE,
            "error"
        );
    }
}


function setupAutomationTasksEvents() {
    const refreshButton =
        document.getElementById(
            "refreshAutomationTasksButton"
        );

    if (!refreshButton) {
        return;
    }

    refreshButton.addEventListener(
        "click",
        () => {
            loadAutomationTasks();
        }
    );
}


function initializeAutomationTasksPage() {
    setupAutomationTasksEvents();
    loadAutomationTasks();
}


initializeAutomationTasksPage();

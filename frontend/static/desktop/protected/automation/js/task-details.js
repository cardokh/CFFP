/*
 * Automation task details page controller.
 *
 * Responsibilities:
 * - Read the selected automation task ID from the page URL.
 * - Load one registered automation task from CCore.
 * - Render task metadata before configuration viewing or execution exists.
 * - Handle loading, missing ID, not found, and error states.
 *
 * Platform dependencies are loaded by protected-workspace.js.
 */

const AUTOMATION_TASK_DETAILS_LOADING_MESSAGE =
    "Loading automation task details...";

const AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE =
    "No automation task ID was provided.";

const AUTOMATION_TASK_DETAILS_ERROR_MESSAGE =
    "Automation task details could not be loaded.";


function getAutomationTaskDetailsBody() {
    return document.getElementById(
        "automationTaskDetailsBody"
    );
}


function getAutomationTaskDetailsMessage() {
    return document.getElementById(
        "automationTaskDetailsMessage"
    );
}


function getAutomationTaskIdFromLocation() {
    const urlParameters =
        new URLSearchParams(
            window.location.search
        );

    return String(
        urlParameters.get("taskId") || ""
    ).trim();
}


function escapeAutomationTaskDetailsValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function normalizeAutomationTaskDetailsStatus(status) {
    return String(status || "unknown")
        .trim()
        .toLowerCase();
}


function showAutomationTaskDetailsMessage(message, type = "info") {
    const messageElement =
        getAutomationTaskDetailsMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        `form-message ${type}`;

    messageElement.textContent =
        message;
}


function hideAutomationTaskDetailsMessage() {
    const messageElement =
        getAutomationTaskDetailsMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        "form-message info hidden";

    messageElement.textContent =
        "";
}


function renderAutomationTaskDetailsPlaceholder(message) {
    const detailsBody =
        getAutomationTaskDetailsBody();

    if (!detailsBody) {
        return;
    }

    detailsBody.innerHTML = `
        <p class="automation-task-details-placeholder">
            ${escapeAutomationTaskDetailsValue(message)}
        </p>
    `;
}


function renderAutomationTaskDetailsField(label, value, isCode = false) {
    const valueClass =
        isCode
            ? "automation-task-details-value code"
            : "automation-task-details-value";

    return `
        <div class="automation-task-details-field">
            <dt>${escapeAutomationTaskDetailsValue(label)}</dt>
            <dd class="${valueClass}" title="${escapeAutomationTaskDetailsValue(value)}">
                ${escapeAutomationTaskDetailsValue(value)}
            </dd>
        </div>
    `;
}


function renderAutomationTaskDetails(task) {
    const detailsBody =
        getAutomationTaskDetailsBody();

    if (!detailsBody) {
        return;
    }

    const status =
        normalizeAutomationTaskDetailsStatus(
            task.status
        );

    document.getElementById(
        "automationTaskDetailsTitle"
    ).textContent = task.name || "Automation Task Details";

    document.getElementById(
        "automationTaskDetailsSummary"
    ).textContent = task.description || "Registered automation task metadata.";

    detailsBody.innerHTML = `
        <div class="automation-task-details-status-row">
            <span class="automation-task-details-status ${escapeAutomationTaskDetailsValue(status)}">
                ${escapeAutomationTaskDetailsValue(status)}
            </span>
        </div>

        <dl class="automation-task-details-grid">
            ${renderAutomationTaskDetailsField("ID", task.id, true)}
            ${renderAutomationTaskDetailsField("Name", task.name)}
            ${renderAutomationTaskDetailsField("Category", task.category)}
            ${renderAutomationTaskDetailsField("Status", status)}
            ${renderAutomationTaskDetailsField("Script", task.script_path, true)}
            ${renderAutomationTaskDetailsField("Configuration", task.config_path, true)}
            ${renderAutomationTaskDetailsField("Description", task.description)}
        </dl>
    `;
}


function parseAutomationTaskDetailsResponse(responseData) {
    if (!responseData || !responseData.task) {
        throw new Error(
            "The backend did not return automation task details."
        );
    }

    return responseData.task;
}


async function loadAutomationTaskDetails() {
    hideAutomationTaskDetailsMessage();

    const taskId =
        getAutomationTaskIdFromLocation();

    if (!taskId) {
        renderAutomationTaskDetailsPlaceholder(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE
        );

        showAutomationTaskDetailsMessage(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE,
            "error"
        );

        return;
    }

    renderAutomationTaskDetailsPlaceholder(
        AUTOMATION_TASK_DETAILS_LOADING_MESSAGE
    );

    try {
        const responseData =
            await getJson(
                CCORE_API_ENDPOINTS.automation.tasks.byId(
                    taskId
                )
            );

        const task =
            parseAutomationTaskDetailsResponse(
                responseData
            );

        renderAutomationTaskDetails(
            task
        );

    } catch (error) {
        console.error(
            "Failed to load automation task details:",
            error
        );

        renderAutomationTaskDetailsPlaceholder(
            AUTOMATION_TASK_DETAILS_ERROR_MESSAGE
        );

        showAutomationTaskDetailsMessage(
            error.message || AUTOMATION_TASK_DETAILS_ERROR_MESSAGE,
            "error"
        );
    }
}


function setupAutomationTaskDetailsEvents() {
    const refreshButton =
        document.getElementById(
            "refreshAutomationTaskDetailsButton"
        );

    if (!refreshButton) {
        return;
    }

    refreshButton.addEventListener(
        "click",
        () => {
            loadAutomationTaskDetails();
        }
    );
}


function initializeAutomationTaskDetailsPage() {
    setupAutomationTaskDetailsEvents();
    loadAutomationTaskDetails();
}


initializeAutomationTaskDetailsPage();

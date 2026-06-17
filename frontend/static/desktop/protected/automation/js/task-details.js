/*
 * Automation task details page controller.
 *
 * Responsibilities:
 * - Read the selected automation task ID from the page URL.
 * - Load one registered automation task from CCore.
 * - Load and render task configuration JSON on demand.
 * - Render task metadata before execution exists.
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

const AUTOMATION_TASK_CONFIGURATION_LOADING_MESSAGE =
    "Loading automation task configuration...";

const AUTOMATION_TASK_CONFIGURATION_ERROR_MESSAGE =
    "Automation task configuration could not be loaded.";


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


function getAutomationTaskConfigurationCard() {
    return document.getElementById(
        "automationTaskConfigurationCard"
    );
}


function getAutomationTaskConfigurationBody() {
    return document.getElementById(
        "automationTaskConfigurationBody"
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


function showAutomationTaskConfigurationCard() {
    const configurationCard =
        getAutomationTaskConfigurationCard();

    if (!configurationCard) {
        return;
    }

    configurationCard.classList.remove("hidden");
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


function renderAutomationTaskConfigurationPlaceholder(message) {
    const configurationBody =
        getAutomationTaskConfigurationBody();

    if (!configurationBody) {
        return;
    }

    configurationBody.innerHTML = `
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


function getJsonValueType(value) {
    if (Array.isArray(value)) {
        return "array";
    }

    if (value === null) {
        return "null";
    }

    return typeof value;
}


function renderJsonPrimitive(value) {
    if (typeof value === "string") {
        return `"${escapeAutomationTaskDetailsValue(value)}"`;
    }

    return escapeAutomationTaskDetailsValue(
        String(value)
    );
}


function renderJsonTreeValue(value, key = "root") {
    const valueType =
        getJsonValueType(value);

    if (valueType !== "object" && valueType !== "array") {
        return `
            <span class="automation-task-json-value ${valueType}">
                ${renderJsonPrimitive(value)}
            </span>
        `;
    }

    const entries =
        valueType === "array"
            ? value.map((item, index) => [index, item])
            : Object.entries(value);

    const itemCountLabel =
        valueType === "array"
            ? `${entries.length} item${entries.length === 1 ? "" : "s"}`
            : `${entries.length} field${entries.length === 1 ? "" : "s"}`;

    return `
        <details class="automation-task-json-node" open>
            <summary>
                <span class="automation-task-json-key">
                    ${escapeAutomationTaskDetailsValue(key)}
                </span>
                <span class="automation-task-json-type">
                    ${escapeAutomationTaskDetailsValue(valueType)} · ${escapeAutomationTaskDetailsValue(itemCountLabel)}
                </span>
            </summary>

            <div class="automation-task-json-children">
                ${entries
                    .map(([entryKey, entryValue]) => `
                        <div class="automation-task-json-row">
                            <span class="automation-task-json-key">
                                ${escapeAutomationTaskDetailsValue(entryKey)}
                            </span>
                            <span class="automation-task-json-separator">:</span>
                            <div class="automation-task-json-child-value">
                                ${renderJsonTreeValue(entryValue, entryKey)}
                            </div>
                        </div>
                    `)
                    .join("")}
            </div>
        </details>
    `;
}


function renderAutomationTaskConfiguration(configurationResponse) {
    const configurationBody =
        getAutomationTaskConfigurationBody();

    if (!configurationBody) {
        return;
    }

    const configuration =
        configurationResponse.configuration;

    const rawJson =
        JSON.stringify(
            configuration,
            null,
            4
        );

    configurationBody.innerHTML = `
        <div class="automation-task-configuration-header">
            <div>
                <p class="automation-task-configuration-label">
                    Configuration path
                </p>
                <p class="automation-task-configuration-path" title="${escapeAutomationTaskDetailsValue(configurationResponse.configuration_path)}">
                    ${escapeAutomationTaskDetailsValue(configurationResponse.configuration_path)}
                </p>
            </div>
        </div>

        <div class="automation-task-configuration-grid">
            <section class="automation-task-configuration-panel">
                <h2>JSON Tree</h2>
                <div class="automation-task-json-tree">
                    ${renderJsonTreeValue(configuration, "configuration")}
                </div>
            </section>

            <section class="automation-task-configuration-panel">
                <h2>Raw JSON</h2>
                <pre class="automation-task-json-raw"><code>${escapeAutomationTaskDetailsValue(rawJson)}</code></pre>
            </section>
        </div>
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


function parseAutomationTaskConfigurationResponse(responseData) {
    if (!responseData || !Object.prototype.hasOwnProperty.call(responseData, "configuration")) {
        throw new Error(
            "The backend did not return automation task configuration."
        );
    }

    return responseData;
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


async function loadAutomationTaskConfiguration() {
    hideAutomationTaskDetailsMessage();
    showAutomationTaskConfigurationCard();

    const taskId =
        getAutomationTaskIdFromLocation();

    if (!taskId) {
        renderAutomationTaskConfigurationPlaceholder(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE
        );

        showAutomationTaskDetailsMessage(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE,
            "error"
        );

        return;
    }

    renderAutomationTaskConfigurationPlaceholder(
        AUTOMATION_TASK_CONFIGURATION_LOADING_MESSAGE
    );

    try {
        const responseData =
            await getJson(
                CCORE_API_ENDPOINTS.automation.tasks.configuration(
                    taskId
                )
            );

        const configurationResponse =
            parseAutomationTaskConfigurationResponse(
                responseData
            );

        renderAutomationTaskConfiguration(
            configurationResponse
        );

    } catch (error) {
        console.error(
            "Failed to load automation task configuration:",
            error
        );

        renderAutomationTaskConfigurationPlaceholder(
            AUTOMATION_TASK_CONFIGURATION_ERROR_MESSAGE
        );

        showAutomationTaskDetailsMessage(
            error.message || AUTOMATION_TASK_CONFIGURATION_ERROR_MESSAGE,
            "error"
        );
    }
}


function setupAutomationTaskDetailsEvents() {
    const refreshButton =
        document.getElementById(
            "refreshAutomationTaskDetailsButton"
        );

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            () => {
                loadAutomationTaskDetails();
            }
        );
    }

    const viewConfigurationButton =
        document.getElementById(
            "viewAutomationTaskConfigurationButton"
        );

    if (viewConfigurationButton) {
        viewConfigurationButton.addEventListener(
            "click",
            () => {
                loadAutomationTaskConfiguration();
            }
        );
    }
}


function initializeAutomationTaskDetailsPage() {
    setupAutomationTaskDetailsEvents();
    loadAutomationTaskDetails();
}


initializeAutomationTaskDetailsPage();

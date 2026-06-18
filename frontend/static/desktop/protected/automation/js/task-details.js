/*
 * Automation task details page controller.
 *
 * Responsibilities:
 * - Read the selected automation task ID from the page URL.
 * - Load one registered automation task from CCore.
 * - Render task metadata in a compact header and tabbed layout.
 * - Load and render task configuration JSON on demand.
 * - Validate the task through the backend validation endpoint.
 * - Keep execution visible as a future capability without implementing it yet.
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

const AUTOMATION_TASK_VALIDATION_LOADING_MESSAGE =
    "Validating automation task...";

const AUTOMATION_TASK_VALIDATION_ERROR_MESSAGE =
    "Automation task validation could not be completed.";

const AUTOMATION_TASK_EXECUTION_LOADING_MESSAGE =
    "Executing automation task...";

const AUTOMATION_TASK_EXECUTION_ERROR_MESSAGE =
    "Automation task execution could not be completed.";

let automationTaskConfigurationLoaded = false;
let automationTaskValidationLoaded = false;
let automationTaskExecutionLoaded = false;


function getAutomationTaskOverviewBody() {
    return document.getElementById(
        "automationTaskOverviewBody"
    );
}


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


function getAutomationTaskConfigurationBody() {
    return document.getElementById(
        "automationTaskConfigurationBody"
    );
}


function getAutomationTaskValidationBody() {
    return document.getElementById(
        "automationTaskValidationBody"
    );
}


function getAutomationTaskExecutionBody() {
    return document.getElementById(
        "automationTaskExecutionBody"
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


function normalizeAutomationTaskValidationStatus(status) {
    return String(status || "UNKNOWN")
        .trim()
        .toUpperCase();
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


function setActiveAutomationTaskTab(tabName) {
    document
        .querySelectorAll(".automation-task-tab")
        .forEach((tabButton) => {
            const isActive =
                tabButton.dataset.tabTarget === tabName;

            tabButton.classList.toggle(
                "active",
                isActive
            );

            tabButton.setAttribute(
                "aria-selected",
                String(isActive)
            );
        });

    document
        .querySelectorAll(".automation-task-tab-panel")
        .forEach((tabPanel) => {
            tabPanel.classList.toggle(
                "active",
                tabPanel.dataset.tabPanel === tabName
            );
        });
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


function renderAutomationTaskOverviewPlaceholder(message) {
    const overviewBody =
        getAutomationTaskOverviewBody();

    if (!overviewBody) {
        return;
    }

    overviewBody.innerHTML = `
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


function renderAutomationTaskValidationPlaceholder(message) {
    const validationBody =
        getAutomationTaskValidationBody();

    if (!validationBody) {
        return;
    }

    validationBody.innerHTML = `
        <p class="automation-task-details-placeholder">
            ${escapeAutomationTaskDetailsValue(message)}
        </p>
    `;
}


function renderAutomationTaskExecutionPlaceholder(message) {
    const executionBody =
        getAutomationTaskExecutionBody();

    if (!executionBody) {
        return;
    }

    executionBody.innerHTML = `
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


function setAutomationTaskDetailsStatus(status) {
    const statusElement =
        document.getElementById(
            "automationTaskDetailsStatus"
        );

    if (!statusElement) {
        return;
    }

    const normalizedStatus =
        normalizeAutomationTaskDetailsStatus(
            status
        );

    statusElement.className =
        `automation-task-details-status ${escapeAutomationTaskDetailsValue(normalizedStatus)}`;

    statusElement.textContent =
        normalizedStatus;
}


function setAutomationTaskDetailsCategory(category) {
    const categoryElement =
        document.getElementById(
            "automationTaskDetailsCategory"
        );

    if (!categoryElement) {
        return;
    }

    categoryElement.textContent =
        category || "uncategorized";
}


function renderAutomationTaskOverview(task) {
    const overviewBody =
        getAutomationTaskOverviewBody();

    if (!overviewBody) {
        return;
    }

    overviewBody.innerHTML = `
        <section class="automation-task-overview-grid">
            <article class="automation-task-overview-card">
                <h2>Purpose</h2>
                <p>${escapeAutomationTaskDetailsValue(task.description || "No description has been provided.")}</p>
            </article>

            <article class="automation-task-overview-card">
                <h2>Current State</h2>
                <dl class="automation-task-overview-list">
                    <div>
                        <dt>Status</dt>
                        <dd>${escapeAutomationTaskDetailsValue(task.status || "unknown")}</dd>
                    </div>
                    <div>
                        <dt>Category</dt>
                        <dd>${escapeAutomationTaskDetailsValue(task.category || "uncategorized")}</dd>
                    </div>
                </dl>
            </article>

            <article class="automation-task-overview-card wide">
                <h2>Next Available Steps</h2>
                <p>
                    Use Configuration to inspect the JSON settings, Validation to run governance checks, and Execution once task execution is implemented.
                </p>
            </article>
        </section>
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

    setAutomationTaskDetailsStatus(status);
    setAutomationTaskDetailsCategory(task.category);
    renderAutomationTaskOverview(task);

    detailsBody.innerHTML = `
        <dl class="automation-task-details-grid compact">
            ${renderAutomationTaskDetailsField("ID", task.id, true)}
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


function renderAutomationTaskValidationCheck(check) {
    const status =
        normalizeAutomationTaskValidationStatus(
            check.status
        );

    return `
        <div class="automation-task-validation-check ${escapeAutomationTaskDetailsValue(status.toLowerCase())}">
            <div class="automation-task-validation-check-status">
                ${escapeAutomationTaskDetailsValue(status)}
            </div>
            <div>
                <h3>${escapeAutomationTaskDetailsValue(check.label)}</h3>
                <p>${escapeAutomationTaskDetailsValue(check.message)}</p>
            </div>
        </div>
    `;
}


function renderAutomationTaskValidation(validationResponse) {
    const validationBody =
        getAutomationTaskValidationBody();

    if (!validationBody) {
        return;
    }

    const validation =
        validationResponse.validation;

    const status =
        normalizeAutomationTaskValidationStatus(
            validation.status
        );

    const summary =
        validation.summary || {};

    const checks =
        validation.checks || [];

    const failedChecks =
        checks.filter((check) =>
            normalizeAutomationTaskValidationStatus(check.status) === "FAILED"
        );

    const passedChecks =
        checks.filter((check) =>
            normalizeAutomationTaskValidationStatus(check.status) !== "FAILED"
        );

    const terminalOutput =
        validation.governance && validation.governance.terminal_output
            ? validation.governance.terminal_output
            : "No terminal output was captured.";

    validationBody.innerHTML = `
        <div class="automation-task-validation-summary ${escapeAutomationTaskDetailsValue(status.toLowerCase())}">
            <div>
                <p class="automation-task-configuration-label">
                    Overall result
                </p>
                <h2>${escapeAutomationTaskDetailsValue(status)}</h2>
            </div>

            <div class="automation-task-validation-counts">
                <span>${escapeAutomationTaskDetailsValue(summary.failed_check_count ?? failedChecks.length)} failed</span>
                <span>${escapeAutomationTaskDetailsValue(summary.passed_check_count ?? passedChecks.length)} passed</span>
                <span>${escapeAutomationTaskDetailsValue(summary.check_count ?? checks.length)} total</span>
            </div>
        </div>

        <section class="automation-task-validation-panel ${failedChecks.length === 0 ? "hidden" : ""}">
            <h2>Failed Checks</h2>
            <div class="automation-task-validation-checks">
                ${failedChecks
                    .map(renderAutomationTaskValidationCheck)
                    .join("")}
            </div>
        </section>

        <details class="automation-task-validation-panel" ${failedChecks.length === 0 ? "open" : ""}>
            <summary>Passed Checks</summary>
            <div class="automation-task-validation-checks">
                ${passedChecks
                    .map(renderAutomationTaskValidationCheck)
                    .join("")}
            </div>
        </details>

        <details class="automation-task-validation-panel">
            <summary>Governance Inspector Output</summary>
            <pre class="automation-task-validation-output"><code>${escapeAutomationTaskDetailsValue(terminalOutput)}</code></pre>
        </details>
    `;
}


function parseAutomationTaskValidationResponse(responseData) {
    if (!responseData || !responseData.validation) {
        throw new Error(
            "The backend did not return automation task validation data."
        );
    }

    return responseData;
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


function normalizeAutomationTaskExecutionStatus(status) {
    return String(status || "unknown")
        .trim()
        .toLowerCase();
}


function renderAutomationTaskExecution(executionResponse) {
    const executionBody =
        getAutomationTaskExecutionBody();

    if (!executionBody) {
        return;
    }

    const execution =
        executionResponse.execution || {};

    const status =
        normalizeAutomationTaskExecutionStatus(
            execution.status
        );

    const stdout =
        execution.stdout || "No standard output was captured.";

    const stderr =
        execution.stderr || "No standard error output was captured.";

    executionBody.innerHTML = `
        <div class="automation-task-execution-summary ${escapeAutomationTaskDetailsValue(status)}">
            <div>
                <p class="automation-task-configuration-label">
                    Execution result
                </p>
                <h2>${escapeAutomationTaskDetailsValue(status)}</h2>
                <p>${escapeAutomationTaskDetailsValue(execution.message || "No message was returned.")}</p>
            </div>

            <dl class="automation-task-execution-metadata">
                <div>
                    <dt>Stage</dt>
                    <dd>${escapeAutomationTaskDetailsValue(execution.stage || "unknown")}</dd>
                </div>
                <div>
                    <dt>Return Code</dt>
                    <dd>${escapeAutomationTaskDetailsValue(execution.return_code ?? "n/a")}</dd>
                </div>
                <div>
                    <dt>Duration</dt>
                    <dd>${escapeAutomationTaskDetailsValue(execution.duration_ms ?? 0)} ms</dd>
                </div>
            </dl>
        </div>

        <details class="automation-task-validation-panel" open>
            <summary>Standard Output</summary>
            <pre class="automation-task-validation-output"><code>${escapeAutomationTaskDetailsValue(stdout)}</code></pre>
        </details>

        <details class="automation-task-validation-panel">
            <summary>Standard Error</summary>
            <pre class="automation-task-validation-output"><code>${escapeAutomationTaskDetailsValue(stderr)}</code></pre>
        </details>
    `;
}


function parseAutomationTaskExecutionResponse(responseData) {
    if (!responseData || !responseData.execution) {
        throw new Error(
            "The backend did not return automation task execution data."
        );
    }

    return responseData;
}


async function loadAutomationTaskDetails() {
    hideAutomationTaskDetailsMessage();

    const taskId =
        getAutomationTaskIdFromLocation();

    if (!taskId) {
        renderAutomationTaskOverviewPlaceholder(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE
        );

        renderAutomationTaskDetailsPlaceholder(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE
        );

        showAutomationTaskDetailsMessage(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE,
            "error"
        );

        return;
    }

    renderAutomationTaskOverviewPlaceholder(
        AUTOMATION_TASK_DETAILS_LOADING_MESSAGE
    );

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

        renderAutomationTaskOverviewPlaceholder(
            AUTOMATION_TASK_DETAILS_ERROR_MESSAGE
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
    setActiveAutomationTaskTab("configuration");

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

    if (automationTaskConfigurationLoaded) {
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

        automationTaskConfigurationLoaded = true;

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


async function validateAutomationTask() {
    hideAutomationTaskDetailsMessage();
    setActiveAutomationTaskTab("validation");

    const taskId =
        getAutomationTaskIdFromLocation();

    if (!taskId) {
        renderAutomationTaskValidationPlaceholder(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE
        );

        showAutomationTaskDetailsMessage(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE,
            "error"
        );

        return;
    }

    renderAutomationTaskValidationPlaceholder(
        AUTOMATION_TASK_VALIDATION_LOADING_MESSAGE
    );

    try {
        const responseData =
            await postJson(
                CCORE_API_ENDPOINTS.automation.tasks.validate(
                    taskId
                ),
                {}
            );

        const validationResponse =
            parseAutomationTaskValidationResponse(
                responseData
            );

        renderAutomationTaskValidation(
            validationResponse
        );

        automationTaskValidationLoaded = true;

    } catch (error) {
        console.error(
            "Failed to validate automation task:",
            error
        );

        renderAutomationTaskValidationPlaceholder(
            AUTOMATION_TASK_VALIDATION_ERROR_MESSAGE
        );

        showAutomationTaskDetailsMessage(
            error.message || AUTOMATION_TASK_VALIDATION_ERROR_MESSAGE,
            "error"
        );
    }
}


async function executeAutomationTask() {
    hideAutomationTaskDetailsMessage();
    setActiveAutomationTaskTab("execution");

    const taskId =
        getAutomationTaskIdFromLocation();

    if (!taskId) {
        renderAutomationTaskExecutionPlaceholder(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE
        );

        showAutomationTaskDetailsMessage(
            AUTOMATION_TASK_DETAILS_MISSING_ID_MESSAGE,
            "error"
        );

        return;
    }

    renderAutomationTaskExecutionPlaceholder(
        AUTOMATION_TASK_EXECUTION_LOADING_MESSAGE
    );

    try {
        const responseData =
            await postJson(
                CCORE_API_ENDPOINTS.automation.tasks.execute(
                    taskId
                ),
                {}
            );

        const executionResponse =
            parseAutomationTaskExecutionResponse(
                responseData
            );

        renderAutomationTaskExecution(
            executionResponse
        );

        automationTaskExecutionLoaded = true;

    } catch (error) {
        console.error(
            "Failed to execute automation task:",
            error
        );

        renderAutomationTaskExecutionPlaceholder(
            AUTOMATION_TASK_EXECUTION_ERROR_MESSAGE
        );

        showAutomationTaskDetailsMessage(
            error.message || AUTOMATION_TASK_EXECUTION_ERROR_MESSAGE,
            "error"
        );
    }
}


function setupAutomationTaskTabs() {
    document
        .querySelectorAll(".automation-task-tab")
        .forEach((tabButton) => {
            tabButton.addEventListener(
                "click",
                () => {
                    const targetTab =
                        tabButton.dataset.tabTarget;

                    if (!targetTab) {
                        return;
                    }

                    setActiveAutomationTaskTab(
                        targetTab
                    );
                }
            );
        });
}


function setupAutomationTaskDetailsEvents() {
    setupAutomationTaskTabs();

    const refreshButton =
        document.getElementById(
            "refreshAutomationTaskDetailsButton"
        );

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            () => {
                automationTaskConfigurationLoaded = false;
                automationTaskValidationLoaded = false;
                automationTaskExecutionLoaded = false;
                renderAutomationTaskConfigurationPlaceholder(
                    "Configuration has not been loaded yet."
                );
                renderAutomationTaskValidationPlaceholder(
                    "Validation has not been run yet."
                );
                renderAutomationTaskExecutionPlaceholder(
                    "Execution has not been run yet."
                );
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

    const validateButton =
        document.getElementById(
            "validateAutomationTaskButton"
        );

    if (validateButton) {
        validateButton.addEventListener(
            "click",
            () => {
                validateAutomationTask();
            }
        );
    }

    const executeButton =
        document.getElementById(
            "executeAutomationTaskButton"
        );

    if (executeButton) {
        executeButton.addEventListener(
            "click",
            () => {
                executeAutomationTask();
            }
        );
    }
}


function initializeAutomationTaskDetailsPage() {
    setupAutomationTaskDetailsEvents();
    loadAutomationTaskDetails();
}


initializeAutomationTaskDetailsPage();

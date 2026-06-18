/*
 * Automation pipeline details page controller.
 *
 * Responsibilities:
 * - Load one registered automation pipeline from CCore.
 * - Present pipeline metadata and ordered orchestration steps.
 * - Keep execution behavior out of the details view.
 * - Reuse the existing automation details layout without changing backend contracts.
 */

const AUTOMATION_PIPELINE_DETAILS_MISSING_ID_MESSAGE =
    "No automation pipeline ID was provided.";

const AUTOMATION_PIPELINE_DETAILS_LOADING_MESSAGE =
    "Loading automation pipeline details...";

const AUTOMATION_PIPELINE_DETAILS_ERROR_MESSAGE =
    "Automation pipeline details could not be loaded.";


function getAutomationPipelineDetailsBody() {
    return document.getElementById(
        "automationPipelineDetailsBody"
    );
}


function getAutomationPipelineDetailsMessage() {
    return document.getElementById(
        "automationPipelineDetailsMessage"
    );
}


function escapeAutomationPipelineDetailsValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function normalizeAutomationPipelineDetailsStatus(status) {
    return String(status || "unknown")
        .trim()
        .toLowerCase();
}


function showAutomationPipelineDetailsMessage(message, type = "info") {
    const messageElement =
        getAutomationPipelineDetailsMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        `form-message ${type}`;

    messageElement.textContent =
        message;
}


function hideAutomationPipelineDetailsMessage() {
    const messageElement =
        getAutomationPipelineDetailsMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        "form-message info hidden";

    messageElement.textContent =
        "";
}


function getAutomationPipelineIdFromQuery() {
    const params =
        new URLSearchParams(window.location.search);

    return params.get("pipelineId") || "";
}


function renderAutomationPipelineDetailsPlaceholder(message) {
    const body =
        getAutomationPipelineDetailsBody();

    if (!body) {
        return;
    }

    body.innerHTML = `
        <section class="shared-panel automation-task-details-card">
            <p class="automation-task-details-placeholder">
                ${escapeAutomationPipelineDetailsValue(message)}
            </p>
        </section>
    `;
}


function renderAutomationPipelineDetailsField(label, value, isCode = false) {
    const valueClass = isCode
        ? "automation-task-details-code-value"
        : "";

    return `
        <div>
            <dt>${escapeAutomationPipelineDetailsValue(label)}</dt>
            <dd class="${valueClass}" title="${escapeAutomationPipelineDetailsValue(value)}">
                ${escapeAutomationPipelineDetailsValue(value)}
            </dd>
        </div>
    `;
}


function setAutomationPipelineDetailsStatus(status) {
    const statusElement =
        document.getElementById(
            "automationPipelineDetailsStatus"
        );

    if (!statusElement) {
        return;
    }

    const normalizedStatus =
        normalizeAutomationPipelineDetailsStatus(status);

    statusElement.className =
        `automation-task-details-status ${escapeAutomationPipelineDetailsValue(normalizedStatus)}`;

    statusElement.textContent =
        normalizedStatus;
}


function setAutomationPipelineDetailsCategory(category) {
    const categoryElement =
        document.getElementById(
            "automationPipelineDetailsCategory"
        );

    if (!categoryElement) {
        return;
    }

    categoryElement.textContent =
        category || "uncategorized";
}


function renderAutomationPipelineSteps(steps) {
    const orderedSteps = Array.isArray(steps)
        ? [...steps].sort((firstStep, secondStep) => {
            return Number(firstStep.order || 0) - Number(secondStep.order || 0);
        })
        : [];

    if (orderedSteps.length === 0) {
        return `
            <p class="automation-task-details-placeholder">
                No pipeline steps are registered.
            </p>
        `;
    }

    return `
        <div class="shared-table-wrapper">
            <table class="shared-table automation-task-details-table">
                <thead>
                    <tr>
                        <th>Order</th>
                        <th>Name</th>
                        <th>Task</th>
                        <th>Required</th>
                    </tr>
                </thead>
                <tbody>
                    ${orderedSteps.map((step) => `
                        <tr>
                            <td>${escapeAutomationPipelineDetailsValue(step.order)}</td>
                            <td>${escapeAutomationPipelineDetailsValue(step.name)}</td>
                            <td>
                                <span class="automation-task-details-code-value">
                                    ${escapeAutomationPipelineDetailsValue(step.task_id)}
                                </span>
                            </td>
                            <td>${step.required ? "Yes" : "No"}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;
}


function renderAutomationPipelineDetails(pipeline) {
    const body =
        getAutomationPipelineDetailsBody();

    if (!body) {
        return;
    }

    const status =
        normalizeAutomationPipelineDetailsStatus(
            pipeline.status
        );

    document.getElementById(
        "automationPipelineDetailsTitle"
    ).textContent = pipeline.name || "Automation Pipeline Details";

    document.getElementById(
        "automationPipelineDetailsSummary"
    ).textContent = pipeline.description || "No description has been provided.";

    setAutomationPipelineDetailsStatus(status);
    setAutomationPipelineDetailsCategory(pipeline.category);

    body.innerHTML = `
        <section class="shared-panel automation-task-details-card">
            <h2>Pipeline Metadata</h2>

            <dl class="automation-task-details-definition-list">
                ${renderAutomationPipelineDetailsField("ID", pipeline.id, true)}
                ${renderAutomationPipelineDetailsField("Category", pipeline.category)}
                ${renderAutomationPipelineDetailsField("Status", pipeline.status)}
                ${renderAutomationPipelineDetailsField("Version", pipeline.version)}
                ${renderAutomationPipelineDetailsField("Execution Mode", pipeline.execution_mode)}
                ${renderAutomationPipelineDetailsField("Failure Strategy", pipeline.failure_strategy)}
            </dl>
        </section>

        <section class="shared-panel automation-task-details-card">
            <h2>Pipeline Steps</h2>
            ${renderAutomationPipelineSteps(pipeline.steps)}
        </section>
    `;
}


function parseAutomationPipelineDetailsResponse(responseData) {
    if (!responseData || !responseData.pipeline) {
        throw new Error(
            "The backend did not return automation pipeline details."
        );
    }

    return responseData.pipeline;
}


async function loadAutomationPipelineDetails() {
    hideAutomationPipelineDetailsMessage();

    const pipelineId =
        getAutomationPipelineIdFromQuery();

    if (!pipelineId) {
        renderAutomationPipelineDetailsPlaceholder(
            AUTOMATION_PIPELINE_DETAILS_MISSING_ID_MESSAGE
        );

        showAutomationPipelineDetailsMessage(
            AUTOMATION_PIPELINE_DETAILS_MISSING_ID_MESSAGE,
            "error"
        );

        return;
    }

    renderAutomationPipelineDetailsPlaceholder(
        AUTOMATION_PIPELINE_DETAILS_LOADING_MESSAGE
    );

    try {
        const responseData =
            await getJson(
                CCORE_API_ENDPOINTS.automation.pipelines.byId(
                    pipelineId
                )
            );

        const pipeline =
            parseAutomationPipelineDetailsResponse(
                responseData
            );

        renderAutomationPipelineDetails(
            pipeline
        );

    } catch (error) {
        console.error(
            "Failed to load automation pipeline details:",
            error
        );

        renderAutomationPipelineDetailsPlaceholder(
            AUTOMATION_PIPELINE_DETAILS_ERROR_MESSAGE
        );

        showAutomationPipelineDetailsMessage(
            error.message || AUTOMATION_PIPELINE_DETAILS_ERROR_MESSAGE,
            "error"
        );
    }
}


function setupAutomationPipelineDetailsEvents() {
    const backLink =
        document.getElementById(
            "backToAutomationPipelinesLink"
        );

    if (backLink) {
        backLink.href =
            LLA_PATHS.desktop.protected.automation.pipelines;
    }

    const refreshButton =
        document.getElementById(
            "refreshAutomationPipelineDetailsButton"
        );

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            () => {
                loadAutomationPipelineDetails();
            }
        );
    }
}


function initializeAutomationPipelineDetailsPage() {
    setupAutomationPipelineDetailsEvents();
    loadAutomationPipelineDetails();
}


initializeAutomationPipelineDetailsPage();

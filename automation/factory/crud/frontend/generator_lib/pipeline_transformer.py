"""Transform the accepted CCore Tasks frontend into the CCore Pipelines frontend."""
from __future__ import annotations

import re


class PipelineFrontendTransformer:
    """Entity-specific transformation from Tasks golden files to Pipeline files."""

    def transform_list_html(self, content: str) -> str:
        replacements = self._common_replacements()
        replacements.update({
            "./css/tasks.css": "./css/pipelines.css",
            "./js/tasks.js": "./js/pipelines.js",
            "task-details.html": "pipeline-details.html",
            "Create Task": "Create Pipeline",
            "Search tasks...": "Search pipelines...",
            "0 tasks": "0 pipelines",
            "Loading CCore tasks...": "Loading CCore pipelines...",
            "CRUD: Create/Read/Update/ and Delete persisted CCore tasks stored in PostgreSQL table\n                            <code>ccore_tasks</code>.": "CRUD: Create/Read/Update/Delete persisted CCore pipelines stored in PostgreSQL table\n                            <code>ccore_pipelines</code>.",
            "Name\n                                            </button>": "Pipeline Name\n                                            </button>",
            "data-sort-key=\"taskName\"": "data-sort-key=\"pipelineName\"",
            "data-sort-key=\"statusLabel\"": "data-sort-key=\"pipelineStatusLabel\"",
        })
        return self._replace_all(content, replacements)

    def transform_list_js(self, content: str) -> str:
        content = self._replace_all(content, self._common_replacements())
        replacements = {
            "PostgreSQL tasks list": "PostgreSQL pipelines list",
            "CCORE_TASKS": "CCORE_PIPELINES",
            "CCore tasks": "CCore pipelines",
            "CCore task": "CCore pipeline",
            "ccoreTasks": "ccorePipelines",
            "ccoreTask": "ccorePipeline",
            "CCoreTasks": "CCorePipelines",
            "CCoreTask": "CCorePipeline",
            "taskName": "pipelineName",
            "taskId": "pipelineId",
            "statusLabel": "pipelineStatusLabel",
            "statusId": "pipelineStatusId",
            "status": "pipelineStatusLabel",
            "tasks": "pipelines",
            "Tasks": "Pipelines",
            "task": "pipeline",
            "Task": "Pipeline",
            "./pipeline-details.html?pipelineId=": "./pipeline-details.html?pipelineId=",
            "No PostgreSQL pipelines found.": "No PostgreSQL pipelines found.",
            "CCore pipelines could not be loaded.": "CCore pipelines could not be loaded.",
        }
        content = self._replace_all(content, replacements)
        content = content.replace(
            "const pipelineStatusLabel = normalizeCCorePipelineStatus(pipeline.pipelineStatusLabel);\n"
            "    const pipelineStatusLabel = pipeline.pipelineStatusLabel || pipelineStatusLabel;",
            "const pipelineStatusValue = normalizeCCorePipelineStatus(pipeline.pipelineStatusLabel);\n"
            "    const pipelineStatusLabel = pipeline.pipelineStatusLabel || pipelineStatusValue;",
        )
        content = content.replace("ccore-pipeline-pipelineStatusLabel", "ccore-pipeline-status")
        return content

    def transform_list_css(self, content: str) -> str:
        return self._replace_all(content, {
            "ccore-tasks": "ccore-pipelines",
            "ccore-task": "ccore-pipeline",
        })

    def transform_details_html(self, content: str) -> str:
        content = self._remove_execution_sections(content)
        content = self._replace_all(content, self._common_replacements())
        replacements = {
            "./css/task-details.css": "./css/pipeline-details.css",
            "./js/task-details.js": "./js/pipeline-details.js",
            "CCore Pipeline Details": "CCore Pipeline Details",
            "Task Details": "Pipeline Details",
            "Task Name": "Pipeline Name",
            "Task Status": "Pipeline Status",
            "Task ID": "Pipeline ID",
            "New task": "New pipeline",
            "Manage the pipeline definition, configure runtime metadata, execute the pipeline,\n                            inspect execution history, and view the selected execution report.": "Manage the pipeline definition, description, status, and persisted PostgreSQL CRUD lifecycle.",
        }
        content = self._replace_all(content, replacements)
        content = self._insert_pipeline_description_field(content)
        return content

    def transform_details_css(self, content: str) -> str:
        content = self._remove_execution_css(content)
        return self._replace_all(content, {
            "ccore-task-details": "ccore-pipeline-details",
            "ccore-task": "ccore-pipeline",
        })

    def transform_details_js(self) -> str:
        return '''/*
 * CCore PostgreSQL pipeline details page controller.
 *
 * Responsibilities:
 * - Load one persisted CCore pipeline when pipelineId is provided.
 * - Create, update, and delete rows in the ccore_pipelines table.
 * - Populate the Pipeline Status dropdown from backend reference data.
 * - Keep validation and form behavior aligned with the accepted Tasks module.
 */

const CCORE_PIPELINE_STATUSES_EMPTY_MESSAGE = "No pipeline statuses are configured.";
const CCORE_PIPELINE_DETAILS_ERROR_MESSAGE = "CCore pipeline details could not be loaded.";
const CCORE_PIPELINE_NAME_REQUIRED_MESSAGE = "Pipeline name is required.";
const CCORE_PIPELINE_STATUS_REQUIRED_MESSAGE = "Pipeline status is required.";
const CCORE_PIPELINE_NO_CHANGES_MESSAGE = "No changes to update.";
const CCORE_PIPELINE_CREATED_SUCCESS_MESSAGE = "Pipeline created successfully.";
const CCORE_PIPELINE_UPDATED_SUCCESS_MESSAGE = "Pipeline updated successfully.";
const CCORE_PIPELINE_SAVE_ERROR_MESSAGE = "Pipeline could not be saved.";
const CCORE_PIPELINE_DELETE_CONFIRM_MESSAGE = "Delete this CCore pipeline?";
const CCORE_PIPELINE_DELETE_ERROR_MESSAGE = "Pipeline could not be deleted.";

let ccorePipelineStatuses = [];
let currentCCorePipelineId = "";
let originalCCorePipelineFormData = null;

function escapeCCorePipelineValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showCCorePipelineDetailsMessage(message, type = "info") {
    const messageElement = document.getElementById("ccorePipelineDetailsMessage");
    if (!messageElement) {
        return;
    }
    messageElement.className = `form-message ${type} ccore-pipeline-details-message`;
    messageElement.textContent = message;
}

function hideCCorePipelineDetailsMessage() {
    const messageElement = document.getElementById("ccorePipelineDetailsMessage");
    if (!messageElement) {
        return;
    }
    messageElement.className = "form-message info hidden ccore-pipeline-details-message";
    messageElement.textContent = "";
}

function formatCCorePipelineDate(value) {
    if (!value) {
        return "—";
    }
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function parseLookupResponse(responseData, propertyName) {
    if (!responseData || !Array.isArray(responseData[propertyName])) {
        throw new Error(`The backend did not return ${propertyName}.`);
    }
    return responseData[propertyName].map((item) => ({
        ...item,
        id: Number(item.id),
        label: String(item.label || "")
    }));
}

function parseCCorePipelineResponse(responseData) {
    if (!responseData || !responseData.pipeline) {
        throw new Error("The backend did not return a CCore pipeline.");
    }
    return responseData.pipeline;
}

function getCCorePipelineIdFromUrl() {
    return new URLSearchParams(window.location.search).get("pipelineId") || "";
}

function populateSelect(selectId, options, placeholder) {
    const select = document.getElementById(selectId);
    select.innerHTML = `<option value="">${escapeCCorePipelineValue(placeholder)}</option>`;
    options.forEach((option) => {
        const optionElement = document.createElement("option");
        optionElement.value = String(option.id);
        optionElement.textContent = option.label;
        select.appendChild(optionElement);
    });
    select.disabled = options.length === 0;
}

async function loadCCorePipelineStatuses() {
    const responseData = await getJson(CCORE_API_ENDPOINTS.pipelines.statuses);
    ccorePipelineStatuses = parseLookupResponse(responseData, "pipelineStatuses");
    populateSelect("ccorePipelineStatusInput", ccorePipelineStatuses, "Select status");
    if (ccorePipelineStatuses.length === 0) {
        throw new Error(CCORE_PIPELINE_STATUSES_EMPTY_MESSAGE);
    }
}

function getCCorePipelineFormData() {
    return {
        pipelineName: document.getElementById("ccorePipelineNameInput").value.trim(),
        pipelineDescription: document.getElementById("ccorePipelineDescriptionInput").value.trim(),
        pipelineStatusId: Number(document.getElementById("ccorePipelineStatusInput").value)
    };
}

function validateCCorePipelineForm(formData) {
    if (!formData.pipelineName) {
        throw new Error(CCORE_PIPELINE_NAME_REQUIRED_MESSAGE);
    }
    if (!formData.pipelineStatusId) {
        throw new Error(CCORE_PIPELINE_STATUS_REQUIRED_MESSAGE);
    }
}

function hasCCorePipelineChanges(formData) {
    return JSON.stringify(formData) !== JSON.stringify(originalCCorePipelineFormData);
}

function setCCorePipelineFormData(pipeline) {
    document.getElementById("ccorePipelineIdInput").value = pipeline.pipelineId || "";
    document.getElementById("ccorePipelineNameInput").value = pipeline.pipelineName || "";
    document.getElementById("ccorePipelineDescriptionInput").value = pipeline.pipelineDescription || "";
    document.getElementById("ccorePipelineStatusInput").value = String(pipeline.pipelineStatusId || "");
    document.getElementById("ccorePipelineCreatedAtInput").value = formatCCorePipelineDate(pipeline.createdAt);
    document.getElementById("ccorePipelineDisplayIdInput").value = pipeline.pipelineId || "New pipeline";
    originalCCorePipelineFormData = getCCorePipelineFormData();
}

function resetCCorePipelineDetailsForCreate() {
    currentCCorePipelineId = "";
    document.getElementById("ccorePipelineDetailsTitle").textContent = "Create CCore Pipeline";
    document.getElementById("ccorePipelineDetailsLegend").textContent = "Create Pipeline";
    document.getElementById("deleteCCorePipelineButton").disabled = true;
    setCCorePipelineFormData({
        pipelineId: "",
        pipelineName: "",
        pipelineDescription: "",
        pipelineStatusId: "",
        createdAt: ""
    });
}

async function loadCCorePipelineDetails(pipelineId) {
    const responseData = await getJson(CCORE_API_ENDPOINTS.pipelines.byId(pipelineId));
    const pipeline = parseCCorePipelineResponse(responseData);
    currentCCorePipelineId = pipeline.pipelineId;
    document.getElementById("ccorePipelineDetailsTitle").textContent = pipeline.pipelineName || "CCore Pipeline Details";
    document.getElementById("ccorePipelineDetailsLegend").textContent = "Update Pipeline";
    document.getElementById("deleteCCorePipelineButton").disabled = false;
    setCCorePipelineFormData(pipeline);
}

async function createCCorePipeline(formData) {
    const responseData = await postJson(CCORE_API_ENDPOINTS.pipelines.create, formData);
    const pipeline = parseCCorePipelineResponse(responseData);
    currentCCorePipelineId = pipeline.pipelineId;
    setCCorePipelineFormData(pipeline);
    window.history.replaceState({}, "", `./pipeline-details.html?pipelineId=${encodeURIComponent(currentCCorePipelineId)}`);
    document.getElementById("deleteCCorePipelineButton").disabled = false;
    showCCorePipelineDetailsMessage(responseData.message || CCORE_PIPELINE_CREATED_SUCCESS_MESSAGE, "success");
}

async function updateCCorePipeline(formData) {
    if (!hasCCorePipelineChanges(formData)) {
        showCCorePipelineDetailsMessage(CCORE_PIPELINE_NO_CHANGES_MESSAGE, "info");
        return;
    }
    const responseData = await putJson(CCORE_API_ENDPOINTS.pipelines.byId(currentCCorePipelineId), formData);
    const pipeline = parseCCorePipelineResponse(responseData);
    setCCorePipelineFormData(pipeline);
    showCCorePipelineDetailsMessage(responseData.message || CCORE_PIPELINE_UPDATED_SUCCESS_MESSAGE, "success");
}

async function handleSaveCCorePipelineSubmit(event) {
    event.preventDefault();
    hideCCorePipelineDetailsMessage();
    const formData = getCCorePipelineFormData();
    try {
        validateCCorePipelineForm(formData);
        if (currentCCorePipelineId) {
            await updateCCorePipeline(formData);
        } else {
            await createCCorePipeline(formData);
        }
    } catch (error) {
        showCCorePipelineDetailsMessage(error.message || CCORE_PIPELINE_SAVE_ERROR_MESSAGE, "error");
    }
}

async function deleteCCorePipeline() {
    hideCCorePipelineDetailsMessage();
    if (!currentCCorePipelineId || !window.confirm(CCORE_PIPELINE_DELETE_CONFIRM_MESSAGE)) {
        return;
    }
    try {
        await deleteJson(CCORE_API_ENDPOINTS.pipelines.byId(currentCCorePipelineId));
        window.location.href = "./pipelines.html";
    } catch (error) {
        showCCorePipelineDetailsMessage(error.message || CCORE_PIPELINE_DELETE_ERROR_MESSAGE, "error");
    }
}

async function setupCCorePipelineDetailsPage() {
    document.getElementById("ccorePipelineDetailsForm").addEventListener("submit", handleSaveCCorePipelineSubmit);
    document.getElementById("deleteCCorePipelineButton").addEventListener("click", deleteCCorePipeline);
    try {
        await loadCCorePipelineStatuses();
        const pipelineId = getCCorePipelineIdFromUrl();
        if (pipelineId) {
            await loadCCorePipelineDetails(pipelineId);
        } else {
            resetCCorePipelineDetailsForCreate();
        }
    } catch (error) {
        console.error("Failed to initialize CCore pipeline details page:", error);
        showCCorePipelineDetailsMessage(error.message || CCORE_PIPELINE_DETAILS_ERROR_MESSAGE, "error");
    }
}

setupCCorePipelineDetailsPage();
'''

    def transform_automation_dashboard(self, content: str) -> str:
        if "/desktop/protected/ccore/automation/pipelines/pipelines.html" in content:
            return content
        card = '''

                            <a class="automation-dashboard-card"
                                href="/desktop/protected/ccore/automation/pipelines/pipelines.html">
                                <span class="automation-dashboard-card-icon">🧩</span>
                                <h3>CCore Automation Pipelines</h3>
                                <p>Create, update, and delete PostgreSQL-backed CCore pipeline records.</p>
                                <span class="automation-dashboard-card-action">Open module →</span>
                            </a>'''
        marker = '''                            <a class="automation-dashboard-card"
                                href="/desktop/protected/ccore/automation/metrics/metrics.html">'''
        return content.replace(marker, card + "\n\n" + marker)

    def transform_api_endpoints(self, content: str) -> str:
        if "pipelines: {" in content:
            return content
        pipelines_block = '''

    pipelines: {
        list: "/api/ccore/pipelines",
        create: "/api/ccore/pipelines",
        statuses: "/api/ccore/pipeline-statuses",

        byId(pipelineId) {
            return `/api/ccore/pipelines/${encodeURIComponent(pipelineId)}`;
        }
    },'''
        marker = '''
    metrics: {'''
        return content.replace(marker, pipelines_block + "\n" + marker)

    def _remove_execution_sections(self, content: str) -> str:
        content = re.sub(
            r"\n\s*<fieldset id=\"ccoreExecutionConfigurationPanel\"[\s\S]*?<\/fieldset>",
            "",
            content,
            count=1,
        )
        content = re.sub(
            r"\n\s*<fieldset id=\"ccoreExecutionHistoryPanel\"[\s\S]*?<\/fieldset>",
            "",
            content,
            count=1,
        )
        content = re.sub(
            r"\n\s*<fieldset id=\"ccoreExecutionReportPanel\"[\s\S]*?<\/fieldset>",
            "",
            content,
            count=1,
        )
        return content

    def _remove_execution_css(self, content: str) -> str:
        return re.sub(r"\n\.ccore-execution[\s\S]*", "\n", content)

    def _insert_pipeline_description_field(self, content: str) -> str:
        if "ccorePipelineDescriptionInput" in content:
            return content
        marker = '''                                <label class="ccore-pipeline-details-field" for="ccorePipelineStatusInput">'''
        field = '''                                <label class="ccore-pipeline-details-field ccore-pipeline-details-description-field" for="ccorePipelineDescriptionInput">
                                    <span>Pipeline Description</span>
                                    <textarea id="ccorePipelineDescriptionInput" maxlength="1000" rows="4"></textarea>
                                </label>

'''
        return content.replace(marker, field + marker)

    def _common_replacements(self) -> dict[str, str]:
        return {
            "CCore Tasks": "CCore Pipelines",
            "CCore Task": "CCore Pipeline",
            "CCore tasks": "CCore pipelines",
            "CCore task": "CCore pipeline",
            "ccoreTasks": "ccorePipelines",
            "ccoreTask": "ccorePipeline",
            "ccore-tasks": "ccore-pipelines",
            "ccore-task": "ccore-pipeline",
            "Tasks": "Pipelines",
            "Task": "Pipeline",
            "tasks": "pipelines",
            "task": "pipeline",
            "ccore_pipeliness": "ccore_pipelines",
            "pipeline-details.html?pipelineId=": "pipeline-details.html?pipelineId=",
        }

    def _replace_all(self, content: str, replacements: dict[str, str]) -> str:
        for source, target in replacements.items():
            content = content.replace(source, target)
        return content

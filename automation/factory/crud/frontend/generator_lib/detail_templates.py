"""Pipeline details templates based on the Tasks detail layout."""
from __future__ import annotations

from .config_loader import EntityConfig


def build_detail_html(entity: EntityConfig) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CCore Pipeline Details | CFFP</title>

    <link rel="stylesheet" href="/desktop/shared/styles/protected-layout.css">
    <link rel="stylesheet" href="/desktop/shared/styles/shared-panels.css">
    <link rel="stylesheet" href="/desktop/shared/styles/shared-table-toolbar.css">
    <link rel="stylesheet" href="/desktop/shared/styles/shared-buttons.css">

    <link rel="stylesheet" href="./css/pipeline-details.css">
</head>

<body>

    <main class="dashboard-layout">

        <div id="desktop-sidebar-container"></div>

        <section class="main-content">

            <div id="header-panel-container"></div>

            <section class="protected-content-panel">

                <div class="ccore-pipeline-details-content">

                    <header class="ccore-pipeline-details-header">
                        <h1 id="ccorePipelineDetailsTitle">CCore Pipeline Details</h1>
                        <p>
                            Manage the pipeline definition and its PostgreSQL-backed status metadata.
                        </p>
                    </header>

                    <fieldset class="shared-panel ccore-pipeline-details-card">
                        <legend id="ccorePipelineDetailsLegend">Pipeline Details</legend>

                        <form id="ccorePipelineDetailsForm" class="ccore-pipeline-details-form">
                            <input id="ccorePipelineIdInput" type="hidden">

                            <div class="ccore-pipeline-details-grid">
                                <label class="ccore-pipeline-details-field" for="ccorePipelineNameInput">
                                    <span>Pipeline Name</span>
                                    <input id="ccorePipelineNameInput" type="text" maxlength="255" required>
                                </label>

                                <label class="ccore-pipeline-details-field" for="ccorePipelineStatusInput">
                                    <span>Status</span>
                                    <select id="ccorePipelineStatusInput" required disabled>
                                        <option value="">Loading statuses...</option>
                                    </select>
                                </label>

                                <label class="ccore-pipeline-details-field readonly" for="ccorePipelineCreatedAtInput">
                                    <span>Created</span>
                                    <input id="ccorePipelineCreatedAtInput" type="text" readonly value="—">
                                </label>

                                <label class="ccore-pipeline-details-field readonly ccore-pipeline-details-id-field"
                                    for="ccorePipelineDisplayIdInput">
                                    <span>Pipeline ID</span>
                                    <input id="ccorePipelineDisplayIdInput" type="text" readonly value="New pipeline">
                                </label>
                            </div>

                            <label class="ccore-pipeline-details-field ccore-pipeline-description-field"
                                for="ccorePipelineDescriptionInput">
                                <span>Description</span>
                                <textarea id="ccorePipelineDescriptionInput" rows="4" maxlength="2000"></textarea>
                            </label>
                        </form>
                    </fieldset>

                    <div id="ccorePipelineDetailsMessage" class="form-message info hidden ccore-pipeline-details-message"></div>

                    <section class="shared-toolbar-panel shared-table-toolbar ccore-pipeline-details-toolbar">
                        <div class="shared-table-toolbar-left">
                            <a class="shared-button secondary shared-table-toolbar-action" href="./pipelines.html">
                                Back to Pipelines
                            </a>
                        </div>

                        <div class="shared-table-toolbar-center">
                            <span id="ccorePipelineDetailsMode" class="ccore-pipeline-details-mode">Create mode</span>
                        </div>

                        <div class="shared-table-toolbar-right">
                            <button id="deleteCCorePipelineButton"
                                class="shared-button secondary shared-table-toolbar-action hidden" type="button">
                                Delete Pipeline
                            </button>

                            <button id="saveCCorePipelineButton" class="shared-button primary shared-table-toolbar-action"
                                type="submit" form="ccorePipelineDetailsForm">
                                Create Pipeline
                            </button>
                        </div>
                    </section>

                </div>

            </section>

            <div id="footer-panel-container"></div>

        </section>

    </main>

    <script src="/desktop/protected/shared/components/protected-workspace/protected-workspace.js"></script>

    <script>
        loadProtectedWorkspace("automation")
            .then(async () => {{
                const pageScript = document.createElement("script");
                pageScript.src = "./js/pipeline-details.js";
                document.body.appendChild(pageScript);
            }});
    </script>

</body>

</html>'''


def build_detail_js(entity: EntityConfig) -> str:
    return f'''/*
 * CCore PostgreSQL pipeline details page controller.
 *
 * Responsibilities:
 * - Load one persisted CCore pipeline when pipelineId is provided.
 * - Create, update, and delete rows in the ccore_pipelines table.
 * - Load pipeline statuses from backend lookup metadata.
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

function escapeCCorePipelineValue(value) {{
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}}

function showCCorePipelineDetailsMessage(message, type = "info") {{
    const messageElement = document.getElementById("ccorePipelineDetailsMessage");
    if (!messageElement) {{
        return;
    }}
    messageElement.className = `form-message ${{type}} ccore-pipeline-details-message`;
    messageElement.textContent = message;
}}

function hideCCorePipelineDetailsMessage() {{
    const messageElement = document.getElementById("ccorePipelineDetailsMessage");
    if (!messageElement) {{
        return;
    }}
    messageElement.className = "form-message info hidden ccore-pipeline-details-message";
    messageElement.textContent = "";
}}

function formatCCorePipelineDate(value) {{
    if (!value) {{
        return "—";
    }}
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}}

function parseLookupResponse(responseData, propertyName) {{
    if (!responseData || !Array.isArray(responseData[propertyName])) {{
        throw new Error(`The backend did not return ${{propertyName}}.`);
    }}
    return responseData[propertyName].map((item) => ({{
        ...item,
        id: Number(item.id),
        label: String(item.label || "")
    }}));
}}

function parseCCorePipelineResponse(responseData) {{
    if (!responseData || !responseData.pipeline) {{
        throw new Error("The backend did not return a CCore pipeline.");
    }}
    return responseData.pipeline;
}}

function renderLookupOptions(selectElementId, lookups, emptyMessage) {{
    const selectElement = document.getElementById(selectElementId);
    if (!selectElement) {{
        return;
    }}
    selectElement.innerHTML = "";
    if (!Array.isArray(lookups) || lookups.length === 0) {{
        const option = document.createElement("option");
        option.value = "";
        option.textContent = emptyMessage;
        selectElement.appendChild(option);
        selectElement.disabled = true;
        return;
    }}
    lookups.forEach((item) => {{
        const option = document.createElement("option");
        option.value = String(item.id);
        option.textContent = item.label;
        selectElement.appendChild(option);
    }});
    selectElement.disabled = false;
}}

function getDefaultLookupId(lookups) {{
    if (!Array.isArray(lookups) || lookups.length === 0) {{
        return "";
    }}
    return String(lookups[0].id);
}}

function setCCorePipelineDetailsMode(mode) {{
    const isEditMode = mode === "edit";
    document.getElementById("ccorePipelineDetailsTitle").textContent = isEditMode ? "CCore Pipeline Details" : "Create CCore Pipeline";
    document.getElementById("ccorePipelineDetailsLegend").textContent = isEditMode ? "Pipeline Details" : "Create Pipeline";
    document.getElementById("ccorePipelineDetailsMode").textContent = isEditMode ? "Edit mode" : "Create mode";
    document.getElementById("saveCCorePipelineButton").textContent = isEditMode ? "Update Pipeline" : "Create Pipeline";
    document.getElementById("deleteCCorePipelineButton").classList.toggle("hidden", !isEditMode);
}}

function getCCorePipelineFormData() {{
    return {{
        pipelineId: document.getElementById("ccorePipelineIdInput").value,
        pipelineName: document.getElementById("ccorePipelineNameInput").value.trim(),
        pipelineDescription: document.getElementById("ccorePipelineDescriptionInput").value.trim(),
        pipelineStatusId: Number(document.getElementById("ccorePipelineStatusInput").value)
    }};
}}

function normalizeCCorePipelineFormSnapshot(formData) {{
    return {{
        pipelineName: String(formData.pipelineName || "").trim(),
        pipelineDescription: String(formData.pipelineDescription || "").trim(),
        pipelineStatusId: Number(formData.pipelineStatusId)
    }};
}}

function setOriginalCCorePipelineFormData(formData) {{
    originalCCorePipelineFormData = normalizeCCorePipelineFormSnapshot(formData);
}}

function hasCCorePipelineFormChanged(formData) {{
    const normalized = normalizeCCorePipelineFormSnapshot(formData);
    return JSON.stringify(normalized) !== JSON.stringify(originalCCorePipelineFormData);
}}

function populateCCorePipelineDetails(pipeline) {{
    currentCCorePipelineId = pipeline.pipelineId || "";
    document.getElementById("ccorePipelineIdInput").value = currentCCorePipelineId;
    document.getElementById("ccorePipelineNameInput").value = pipeline.pipelineName || "";
    document.getElementById("ccorePipelineDescriptionInput").value = pipeline.pipelineDescription || "";
    document.getElementById("ccorePipelineStatusInput").value = String(pipeline.pipelineStatusId);
    document.getElementById("ccorePipelineCreatedAtInput").value = formatCCorePipelineDate(pipeline.createdAt);
    document.getElementById("ccorePipelineDisplayIdInput").value = currentCCorePipelineId || "New pipeline";
    setCCorePipelineDetailsMode(currentCCorePipelineId ? "edit" : "create");
    setOriginalCCorePipelineFormData(getCCorePipelineFormData());
}}

function resetCCorePipelineDetailsForCreate() {{
    currentCCorePipelineId = "";
    document.getElementById("ccorePipelineIdInput").value = "";
    document.getElementById("ccorePipelineNameInput").value = "";
    document.getElementById("ccorePipelineDescriptionInput").value = "";
    document.getElementById("ccorePipelineStatusInput").value = getDefaultLookupId(ccorePipelineStatuses);
    document.getElementById("ccorePipelineCreatedAtInput").value = "—";
    document.getElementById("ccorePipelineDisplayIdInput").value = "New pipeline";
    setCCorePipelineDetailsMode("create");
    setOriginalCCorePipelineFormData(getCCorePipelineFormData());
}}

async function loadCCorePipelineStatuses() {{
    const responseData = await getJson(CCORE_API_ENDPOINTS.pipelines.statuses);
    ccorePipelineStatuses = parseLookupResponse(responseData, "pipelineStatuses");
    renderLookupOptions("ccorePipelineStatusInput", ccorePipelineStatuses, CCORE_PIPELINE_STATUSES_EMPTY_MESSAGE);
}}

async function loadCCorePipelineDetails(pipelineId) {{
    const responseData = await getJson(CCORE_API_ENDPOINTS.pipelines.byId(pipelineId));
    populateCCorePipelineDetails(parseCCorePipelineResponse(responseData));
}}

function createCCorePipeline(formData) {{
    return postJson(CCORE_API_ENDPOINTS.pipelines.create, {{
        pipelineName: formData.pipelineName,
        pipelineDescription: formData.pipelineDescription || null,
        pipelineStatusId: formData.pipelineStatusId
    }});
}}

function updateCCorePipeline(formData) {{
    return putJson(CCORE_API_ENDPOINTS.pipelines.byId(formData.pipelineId), {{
        pipelineName: formData.pipelineName,
        pipelineDescription: formData.pipelineDescription || null,
        pipelineStatusId: formData.pipelineStatusId
    }});
}}

function validateCCorePipelineForm(formData) {{
    if (!formData.pipelineName) {{
        showCCorePipelineDetailsMessage(CCORE_PIPELINE_NAME_REQUIRED_MESSAGE, "error");
        return false;
    }}
    if (!formData.pipelineStatusId) {{
        showCCorePipelineDetailsMessage(CCORE_PIPELINE_STATUS_REQUIRED_MESSAGE, "error");
        return false;
    }}
    return true;
}}

async function handleCCorePipelineSave(event) {{
    event.preventDefault();
    hideCCorePipelineDetailsMessage();

    const formData = getCCorePipelineFormData();
    if (!validateCCorePipelineForm(formData)) {{
        return;
    }}

    if (formData.pipelineId && !hasCCorePipelineFormChanged(formData)) {{
        showCCorePipelineDetailsMessage(CCORE_PIPELINE_NO_CHANGES_MESSAGE, "info");
        return;
    }}

    try {{
        const responseData = formData.pipelineId
            ? await updateCCorePipeline(formData)
            : await createCCorePipeline(formData);
        const pipeline = parseCCorePipelineResponse(responseData);
        populateCCorePipelineDetails(pipeline);
        showCCorePipelineDetailsMessage(
            formData.pipelineId ? CCORE_PIPELINE_UPDATED_SUCCESS_MESSAGE : CCORE_PIPELINE_CREATED_SUCCESS_MESSAGE,
            "success"
        );
        if (!formData.pipelineId && pipeline.pipelineId) {{
            window.history.replaceState(null, "", `./pipeline-details.html?pipelineId=${{encodeURIComponent(pipeline.pipelineId)}}`);
        }}
    }} catch (error) {{
        console.error("Failed to save CCore pipeline:", error);
        showCCorePipelineDetailsMessage(error.message || CCORE_PIPELINE_SAVE_ERROR_MESSAGE, "error");
    }}
}}

async function handleCCorePipelineDelete() {{
    const pipelineId = currentCCorePipelineId;
    if (!pipelineId || !window.confirm(CCORE_PIPELINE_DELETE_CONFIRM_MESSAGE)) {{
        return;
    }}

    hideCCorePipelineDetailsMessage();
    try {{
        await deleteJson(CCORE_API_ENDPOINTS.pipelines.byId(pipelineId));
        window.location.href = "./pipelines.html";
    }} catch (error) {{
        console.error("Failed to delete CCore pipeline:", error);
        showCCorePipelineDetailsMessage(error.message || CCORE_PIPELINE_DELETE_ERROR_MESSAGE, "error");
    }}
}}

async function initializeCCorePipelineDetailsPage() {{
    hideCCorePipelineDetailsMessage();
    const parameters = new URLSearchParams(window.location.search);
    const pipelineId = parameters.get("pipelineId") || "";

    try {{
        await loadCCorePipelineStatuses();
        if (pipelineId) {{
            await loadCCorePipelineDetails(pipelineId);
        }} else {{
            resetCCorePipelineDetailsForCreate();
        }}
    }} catch (error) {{
        console.error("Failed to initialize CCore pipeline details page:", error);
        showCCorePipelineDetailsMessage(error.message || CCORE_PIPELINE_DETAILS_ERROR_MESSAGE, "error");
    }}
}}

function setupCCorePipelineDetailsForm() {{
    const form = document.getElementById("ccorePipelineDetailsForm");
    if (form) {{
        form.addEventListener("submit", handleCCorePipelineSave);
    }}

    const deleteButton = document.getElementById("deleteCCorePipelineButton");
    if (deleteButton) {{
        deleteButton.addEventListener("click", handleCCorePipelineDelete);
    }}
}}

setupCCorePipelineDetailsForm();
initializeCCorePipelineDetailsPage();
'''

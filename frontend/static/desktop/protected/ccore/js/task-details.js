/*
 * CCore PostgreSQL task details page controller.
 *
 * Responsibilities:
 * - Load one persisted CCore task when taskId is provided.
 * - Create, update, and delete rows in the ccore_tasks table.
 * - Load execution provider and implementer lookup metadata.
 * - Execute a task with selected provider/implementer IDs.
 * - Render execution history and selected execution report.
 */

const CCORE_TASK_STATUSES_LOADING_MESSAGE = "Loading task statuses...";
const CCORE_TASK_STATUSES_EMPTY_MESSAGE = "No task statuses are configured.";
const CCORE_TASK_DETAILS_ERROR_MESSAGE = "CCore task details could not be loaded.";
const CCORE_TASK_NAME_REQUIRED_MESSAGE = "Task name is required.";
const CCORE_TASK_STATUS_REQUIRED_MESSAGE = "Task status is required.";
const CCORE_TASK_NO_CHANGES_MESSAGE = "No changes to update.";
const CCORE_TASK_CREATED_SUCCESS_MESSAGE = "Task created successfully.";
const CCORE_TASK_UPDATED_SUCCESS_MESSAGE = "Task updated successfully.";
const CCORE_TASK_SAVE_ERROR_MESSAGE = "Task could not be saved.";
const CCORE_TASK_DELETE_CONFIRM_MESSAGE = "Delete this CCore task?";
const CCORE_TASK_DELETE_ERROR_MESSAGE = "Task could not be deleted.";
const CCORE_EXECUTION_LOOKUPS_ERROR_MESSAGE = "Execution configuration metadata could not be loaded.";
const CCORE_EXECUTION_REQUIRED_MESSAGE = "Select both an execution provider and an implementer.";
const CCORE_EXECUTION_ERROR_MESSAGE = "Task execution could not be completed.";
const CCORE_EXECUTION_HISTORY_ERROR_MESSAGE = "Execution history could not be loaded.";
const CCORE_EXECUTION_TABLE_COLUMN_COUNT = 5;
const CCORE_EXECUTION_PAGE_SIZE = 5;

let ccoreTaskStatuses = [];
let ccoreExecutionProviders = [];
let ccoreExecutionImplementers = [];
let ccoreExecutions = [];
let ccoreExecutionSearchTerm = "";
let ccoreExecutionCurrentPage = 1;
let selectedCCoreExecutionId = "";
let currentCCoreTaskId = "";
let originalCCoreTaskFormData = null;

function escapeCCoreTaskValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showCCoreTaskDetailsMessage(message, type = "info") {
    const messageElement = document.getElementById("ccoreTaskDetailsMessage");
    if (!messageElement) {
        return;
    }
    messageElement.className = `form-message ${type} ccore-task-details-message`;
    messageElement.textContent = message;
}

function hideCCoreTaskDetailsMessage() {
    const messageElement = document.getElementById("ccoreTaskDetailsMessage");
    if (!messageElement) {
        return;
    }
    messageElement.className = "form-message info hidden ccore-task-details-message";
    messageElement.textContent = "";
}

function formatCCoreTaskDate(value) {
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
        id: Number(item.id),
        label: String(item.label || "")
    }));
}

function parseCCoreTaskResponse(responseData) {
    if (!responseData || !responseData.task) {
        throw new Error("The backend did not return a CCore task.");
    }
    return responseData.task;
}

function parseCCoreExecutionsResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.executions)) {
        throw new Error("The backend did not return CCore task executions.");
    }
    return responseData.executions;
}

function renderLookupOptions(selectElementId, lookups, emptyMessage) {
    const selectElement = document.getElementById(selectElementId);
    if (!selectElement) {
        return;
    }
    selectElement.innerHTML = "";
    if (!Array.isArray(lookups) || lookups.length === 0) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = emptyMessage;
        selectElement.appendChild(option);
        selectElement.disabled = true;
        return;
    }
    lookups.forEach((item) => {
        const option = document.createElement("option");
        option.value = String(item.id);
        option.textContent = item.label;
        selectElement.appendChild(option);
    });
    selectElement.disabled = false;
}

function getDefaultLookupId(lookups) {
    if (!Array.isArray(lookups) || lookups.length === 0) {
        return "";
    }
    return String(lookups[0].id);
}

function setCCoreTaskDetailsMode(mode) {
    const isEditMode = mode === "edit";
    document.getElementById("ccoreTaskDetailsTitle").textContent = isEditMode ? "CCore Task Details" : "Create CCore Task";
    document.getElementById("ccoreTaskDetailsLegend").textContent = isEditMode ? "Task Details" : "Create Task";
    document.getElementById("ccoreTaskDetailsMode").textContent = isEditMode ? "Edit mode" : "Create mode";
    document.getElementById("saveCCoreTaskButton").textContent = isEditMode ? "Update Task" : "Create Task";
    document.getElementById("deleteCCoreTaskButton").classList.toggle("hidden", !isEditMode);
    document.getElementById("ccoreExecutionConfigurationPanel").classList.toggle("hidden", !isEditMode);
    document.getElementById("ccoreExecutionHistoryPanel").classList.toggle("hidden", !isEditMode);
    document.getElementById("ccoreExecutionReportPanel").classList.toggle("hidden", !isEditMode);
}

function getCCoreTaskFormData() {
    return {
        taskId: document.getElementById("ccoreTaskIdInput").value,
        taskName: document.getElementById("ccoreTaskNameInput").value.trim(),
        statusId: Number(document.getElementById("ccoreTaskStatusInput").value)
    };
}

function normalizeCCoreTaskFormSnapshot(formData) {
    return {
        taskName: String(formData.taskName || "").trim(),
        statusId: Number(formData.statusId)
    };
}

function setOriginalCCoreTaskFormData(formData) {
    originalCCoreTaskFormData = normalizeCCoreTaskFormSnapshot(formData);
}

function hasCCoreTaskFormChanged(formData) {
    const normalized = normalizeCCoreTaskFormSnapshot(formData);
    return JSON.stringify(normalized) !== JSON.stringify(originalCCoreTaskFormData);
}

function populateCCoreTaskDetails(task) {
    currentCCoreTaskId = task.taskId || "";
    document.getElementById("ccoreTaskIdInput").value = currentCCoreTaskId;
    document.getElementById("ccoreTaskNameInput").value = task.taskName || "";
    document.getElementById("ccoreTaskStatusInput").value = String(task.statusId);
    document.getElementById("ccoreTaskCreatedAtInput").value = formatCCoreTaskDate(task.createdAt);
    document.getElementById("ccoreTaskDisplayIdInput").value = currentCCoreTaskId || "New task";
    setCCoreTaskDetailsMode(currentCCoreTaskId ? "edit" : "create");
    setOriginalCCoreTaskFormData(getCCoreTaskFormData());
}

function resetCCoreTaskDetailsForCreate() {
    currentCCoreTaskId = "";
    document.getElementById("ccoreTaskIdInput").value = "";
    document.getElementById("ccoreTaskNameInput").value = "";
    document.getElementById("ccoreTaskStatusInput").value = getDefaultLookupId(ccoreTaskStatuses);
    document.getElementById("ccoreTaskCreatedAtInput").value = "—";
    document.getElementById("ccoreTaskDisplayIdInput").value = "New task";
    setCCoreTaskDetailsMode("create");
    setOriginalCCoreTaskFormData(getCCoreTaskFormData());
}

async function loadCCoreTaskStatuses() {
    const responseData = await getJson(CCORE_API_ENDPOINTS.tasks.statuses);
    ccoreTaskStatuses = parseLookupResponse(responseData, "statuses");
    renderLookupOptions("ccoreTaskStatusInput", ccoreTaskStatuses, CCORE_TASK_STATUSES_EMPTY_MESSAGE);
}

async function loadExecutionLookups() {
    const [providersResponse, implementersResponse] = await Promise.all([
        getJson(CCORE_API_ENDPOINTS.tasks.executionProviders),
        getJson(CCORE_API_ENDPOINTS.tasks.executionImplementers)
    ]);
    ccoreExecutionProviders = parseLookupResponse(providersResponse, "providers");
    ccoreExecutionImplementers = parseLookupResponse(implementersResponse, "implementers");
    renderLookupOptions("ccoreExecutionProviderInput", ccoreExecutionProviders, "No providers configured.");
    renderLookupOptions("ccoreExecutionImplementerInput", ccoreExecutionImplementers, "No implementers configured.");
    document.getElementById("ccoreExecutionProviderInput").value = getDefaultLookupId(ccoreExecutionProviders);
    document.getElementById("ccoreExecutionImplementerInput").value = getDefaultLookupId(ccoreExecutionImplementers);
}

async function loadCCoreTaskDetails(taskId) {
    hideCCoreTaskDetailsMessage();
    const responseData = await getJson(CCORE_API_ENDPOINTS.tasks.byId(taskId));
    populateCCoreTaskDetails(parseCCoreTaskResponse(responseData));
}

async function saveCCoreTask(taskName, statusId) {
    return postJson(CCORE_API_ENDPOINTS.tasks.create, { taskName, statusId });
}

async function updateCCoreTask(taskId, taskName, statusId) {
    return putJson(CCORE_API_ENDPOINTS.tasks.byId(taskId), { taskName, statusId });
}

async function handleSaveCCoreTaskSubmit(event) {
    event.preventDefault();
    hideCCoreTaskDetailsMessage();
    const formData = getCCoreTaskFormData();
    const normalizedFormData = normalizeCCoreTaskFormSnapshot(formData);
    if (!normalizedFormData.taskName) {
        showCCoreTaskDetailsMessage(CCORE_TASK_NAME_REQUIRED_MESSAGE, "error");
        return;
    }
    if (!normalizedFormData.statusId) {
        showCCoreTaskDetailsMessage(CCORE_TASK_STATUS_REQUIRED_MESSAGE, "error");
        return;
    }
    if (formData.taskId && !hasCCoreTaskFormChanged(formData)) {
        showCCoreTaskDetailsMessage(CCORE_TASK_NO_CHANGES_MESSAGE, "info");
        return;
    }
    try {
        let responseData;
        if (formData.taskId) {
            responseData = await updateCCoreTask(formData.taskId, normalizedFormData.taskName, normalizedFormData.statusId);
            showCCoreTaskDetailsMessage(CCORE_TASK_UPDATED_SUCCESS_MESSAGE, "success");
        } else {
            responseData = await saveCCoreTask(normalizedFormData.taskName, normalizedFormData.statusId);
            showCCoreTaskDetailsMessage(CCORE_TASK_CREATED_SUCCESS_MESSAGE, "success");
        }
        const savedTask = parseCCoreTaskResponse(responseData);
        populateCCoreTaskDetails(savedTask);
        if (!formData.taskId && savedTask.taskId) {
            window.history.replaceState({}, "", `./task-details.html?taskId=${encodeURIComponent(savedTask.taskId)}`);
            await loadCCoreExecutionHistory();
        }
    } catch (error) {
        showCCoreTaskDetailsMessage(error.message || CCORE_TASK_SAVE_ERROR_MESSAGE, "error");
    }
}

async function deleteCCoreTask() {
    const taskId = currentCCoreTaskId;
    if (!taskId || !window.confirm(CCORE_TASK_DELETE_CONFIRM_MESSAGE)) {
        return;
    }
    try {
        await deleteJson(CCORE_API_ENDPOINTS.tasks.byId(taskId));
        window.location.href = "./tasks.html";
    } catch (error) {
        showCCoreTaskDetailsMessage(error.message || CCORE_TASK_DELETE_ERROR_MESSAGE, "error");
    }
}

function getCCoreTaskIdFromUrl() {
    return new URLSearchParams(window.location.search).get("taskId") || "";
}

function getFilteredExecutions() {
    const term = ccoreExecutionSearchTerm.trim().toLowerCase();
    if (!term) {
        return ccoreExecutions;
    }
    return ccoreExecutions.filter((execution) => [
        execution.statusLabel,
        execution.providerLabel,
        execution.implementerLabel,
        execution.requestedBy,
        execution.startedAt,
        execution.completedAt,
        execution.executionId
    ].join(" ").toLowerCase().includes(term));
}

function renderCCoreExecutionPlaceholder(message) {
    document.getElementById("ccoreExecutionTableBody").innerHTML = `
        <tr>
            <td colspan="${CCORE_EXECUTION_TABLE_COLUMN_COUNT}" class="shared-table-empty-state">
                ${escapeCCoreTaskValue(message)}
            </td>
        </tr>
    `;
}

function updateExecutionPager(totalRows) {
    const pageCount = Math.max(1, Math.ceil(totalRows / CCORE_EXECUTION_PAGE_SIZE));
    ccoreExecutionCurrentPage = Math.min(ccoreExecutionCurrentPage, pageCount);
    document.getElementById("ccoreExecutionPageIndicator").textContent = `Page ${ccoreExecutionCurrentPage} of ${pageCount}`;
    document.getElementById("ccoreExecutionCountLabel").textContent = `${totalRows} ${totalRows === 1 ? "execution" : "executions"}`;
    document.getElementById("ccoreExecutionPrevButton").disabled = ccoreExecutionCurrentPage <= 1;
    document.getElementById("ccoreExecutionNextButton").disabled = ccoreExecutionCurrentPage >= pageCount;
}

function renderCCoreExecutionHistory() {
    const filtered = getFilteredExecutions();
    updateExecutionPager(filtered.length);
    if (filtered.length === 0) {
        renderCCoreExecutionPlaceholder("No executions found for this task.");
        return;
    }
    const startIndex = (ccoreExecutionCurrentPage - 1) * CCORE_EXECUTION_PAGE_SIZE;
    const pageRows = filtered.slice(startIndex, startIndex + CCORE_EXECUTION_PAGE_SIZE);
    document.getElementById("ccoreExecutionTableBody").innerHTML = pageRows.map((execution) => `
        <tr data-execution-id="${escapeCCoreTaskValue(execution.executionId)}" class="${execution.executionId === selectedCCoreExecutionId ? "selected" : ""}">
            <td><span class="ccore-execution-status-pill">${escapeCCoreTaskValue(execution.statusLabel)}</span></td>
            <td>${escapeCCoreTaskValue(formatCCoreTaskDate(execution.startedAt))}</td>
            <td>${escapeCCoreTaskValue(formatCCoreTaskDate(execution.completedAt || execution.failedAt))}</td>
            <td>${escapeCCoreTaskValue(execution.providerLabel)}</td>
            <td>${escapeCCoreTaskValue(execution.implementerLabel)}</td>
        </tr>
    `).join("");
    document.querySelectorAll("#ccoreExecutionTableBody tr[data-execution-id]").forEach((row) => {
        row.addEventListener("click", () => selectCCoreExecution(row.dataset.executionId));
    });
}

async function loadCCoreExecutionHistory() {
    if (!currentCCoreTaskId) {
        return;
    }
    try {
        const responseData = await getJson(CCORE_API_ENDPOINTS.tasks.executions(currentCCoreTaskId));
        ccoreExecutions = parseCCoreExecutionsResponse(responseData);
        ccoreExecutionCurrentPage = 1;
        if (!ccoreExecutions.some((execution) => execution.executionId === selectedCCoreExecutionId)) {
            selectedCCoreExecutionId = "";
            renderExecutionReport(null);
        }
        renderCCoreExecutionHistory();
    } catch (error) {
        showCCoreTaskDetailsMessage(error.message || CCORE_EXECUTION_HISTORY_ERROR_MESSAGE, "error");
    }
}

function selectCCoreExecution(executionId) {
    selectedCCoreExecutionId = executionId;
    const execution = ccoreExecutions.find((item) => item.executionId === executionId) || null;
    renderCCoreExecutionHistory();
    renderExecutionReport(execution);
}

function renderJsonBlock(title, value) {
    return `
        <div class="ccore-execution-report-block">
            <h3>${escapeCCoreTaskValue(title)}</h3>
            <pre>${escapeCCoreTaskValue(JSON.stringify(value || {}, null, 2))}</pre>
        </div>
    `;
}

function renderExecutionReport(execution) {
    const reportContent = document.getElementById("ccoreExecutionReportContent");
    if (!execution) {
        reportContent.className = "ccore-execution-report-empty";
        reportContent.textContent = "No execution selected.";
        return;
    }
    reportContent.className = "";
    reportContent.innerHTML = `
        <div class="ccore-execution-report-grid">
            <div class="ccore-execution-report-item"><span>Execution ID</span><strong>${escapeCCoreTaskValue(execution.executionId)}</strong></div>
            <div class="ccore-execution-report-item"><span>Status</span><strong>${escapeCCoreTaskValue(execution.statusLabel)}</strong></div>
            <div class="ccore-execution-report-item"><span>Provider</span><strong>${escapeCCoreTaskValue(execution.providerLabel)}</strong></div>
            <div class="ccore-execution-report-item"><span>Implementer</span><strong>${escapeCCoreTaskValue(execution.implementerLabel)}</strong></div>
            <div class="ccore-execution-report-item"><span>Started</span><strong>${escapeCCoreTaskValue(formatCCoreTaskDate(execution.startedAt))}</strong></div>
            <div class="ccore-execution-report-item"><span>Completed</span><strong>${escapeCCoreTaskValue(formatCCoreTaskDate(execution.completedAt || execution.failedAt))}</strong></div>
        </div>
        ${renderJsonBlock("Configuration Snapshot", execution.configurationSnapshot)}
        ${renderJsonBlock("Validation Snapshot", execution.validationSnapshot)}
        ${renderJsonBlock("Execution Report", execution.executionReport)}
        ${renderJsonBlock("Error Details", execution.errorDetails)}
    `;
}

async function executeCCoreTask() {
    hideCCoreTaskDetailsMessage();
    if (!currentCCoreTaskId) {
        showCCoreTaskDetailsMessage("Save the task before executing it.", "error");
        return;
    }
    const providerId = Number(document.getElementById("ccoreExecutionProviderInput").value);
    const implementerId = Number(document.getElementById("ccoreExecutionImplementerInput").value);
    if (!providerId || !implementerId) {
        showCCoreTaskDetailsMessage(CCORE_EXECUTION_REQUIRED_MESSAGE, "error");
        return;
    }
    const executeButton = document.getElementById("executeCCoreTaskButton");
    executeButton.disabled = true;
    executeButton.textContent = "Executing...";
    try {
        const responseData = await postJson(CCORE_API_ENDPOINTS.tasks.execute(currentCCoreTaskId), {
            providerId,
            implementerId,
            requestedBy: "system",
            inputPayload: {}
        });
        const returnedExecutionId = responseData?.execution?.executionDetails?.executionId || "";
        selectedCCoreExecutionId = returnedExecutionId;
        showCCoreTaskDetailsMessage(responseData.message || "Task execution request completed.", "success");
        await loadCCoreExecutionHistory();
        if (selectedCCoreExecutionId) {
            selectCCoreExecution(selectedCCoreExecutionId);
        }
    } catch (error) {
        showCCoreTaskDetailsMessage(error.message || CCORE_EXECUTION_ERROR_MESSAGE, "error");
        await loadCCoreExecutionHistory();
    } finally {
        executeButton.disabled = false;
        executeButton.textContent = "Execute Task";
    }
}

function setupExecutionEventHandlers() {
    document.getElementById("executeCCoreTaskButton").addEventListener("click", executeCCoreTask);
    document.getElementById("refreshCCoreExecutionsButton").addEventListener("click", loadCCoreExecutionHistory);
    document.getElementById("ccoreExecutionSearchInput").addEventListener("input", (event) => {
        ccoreExecutionSearchTerm = event.target.value || "";
        ccoreExecutionCurrentPage = 1;
        renderCCoreExecutionHistory();
    });
    document.getElementById("ccoreExecutionPrevButton").addEventListener("click", () => {
        ccoreExecutionCurrentPage = Math.max(1, ccoreExecutionCurrentPage - 1);
        renderCCoreExecutionHistory();
    });
    document.getElementById("ccoreExecutionNextButton").addEventListener("click", () => {
        ccoreExecutionCurrentPage += 1;
        renderCCoreExecutionHistory();
    });
}

async function setupCCoreTaskDetailsPage() {
    document.getElementById("ccoreTaskDetailsForm").addEventListener("submit", handleSaveCCoreTaskSubmit);
    document.getElementById("deleteCCoreTaskButton").addEventListener("click", deleteCCoreTask);
    setupExecutionEventHandlers();
    try {
        await loadCCoreTaskStatuses();
        await loadExecutionLookups();
        const taskId = getCCoreTaskIdFromUrl();
        if (taskId) {
            await loadCCoreTaskDetails(taskId);
            await loadCCoreExecutionHistory();
        } else {
            resetCCoreTaskDetailsForCreate();
        }
    } catch (error) {
        console.error("Failed to initialize CCore task details page:", error);
        showCCoreTaskDetailsMessage(error.message || CCORE_TASK_DETAILS_ERROR_MESSAGE || CCORE_EXECUTION_LOOKUPS_ERROR_MESSAGE, "error");
    }
}

setupCCoreTaskDetailsPage();

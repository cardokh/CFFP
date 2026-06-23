/*
 * CCore PostgreSQL task details page controller.
 *
 * Responsibilities:
 * - Load one persisted CCore task when taskId is provided.
 * - Create, update, and delete rows in the ccore_tasks table.
 * - Keep list-page navigation separate from record maintenance.
 * - Keep frontend endpoint usage centralized through CCORE_API_ENDPOINTS.
 * - Use the integer-based task status contract: { id: Number, label: String }.
 */

const CCORE_TASK_STATUSES_LOADING_MESSAGE =
    "Loading task statuses...";

const CCORE_TASK_STATUSES_EMPTY_MESSAGE =
    "No task statuses are configured.";

const CCORE_TASK_STATUSES_ERROR_MESSAGE =
    "CCore task statuses could not be loaded.";

const CCORE_TASK_DETAILS_ERROR_MESSAGE =
    "CCore task details could not be loaded.";

const CCORE_TASK_NAME_REQUIRED_MESSAGE =
    "Task name is required.";

const CCORE_TASK_STATUS_REQUIRED_MESSAGE =
    "Task status is required.";

const CCORE_TASK_NO_CHANGES_MESSAGE =
    "No changes to update.";

const CCORE_TASK_CREATED_SUCCESS_MESSAGE =
    "Task created successfully.";

const CCORE_TASK_UPDATED_SUCCESS_MESSAGE =
    "Task updated successfully.";

const CCORE_TASK_SAVE_ERROR_MESSAGE =
    "Task could not be saved.";

const CCORE_TASK_DELETE_CONFIRM_MESSAGE =
    "Delete this CCore task?";

const CCORE_TASK_DELETE_ERROR_MESSAGE =
    "Task could not be deleted.";

let ccoreTaskStatuses = [];
let currentCCoreTaskId = "";
let originalCCoreTaskFormData = null;


function getCCoreTaskDetailsMessage() {
    return document.getElementById("ccoreTaskDetailsMessage");
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


function showCCoreTaskDetailsMessage(message, type = "info") {
    const messageElement = getCCoreTaskDetailsMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className = `form-message ${type} ccore-task-details-message`;
    messageElement.textContent = message;
}


function hideCCoreTaskDetailsMessage() {
    const messageElement = getCCoreTaskDetailsMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className = "form-message info hidden ccore-task-details-message";
    messageElement.textContent = "";
}


function parseCCoreTaskStatusId(value) {
    const statusId = Number(value);

    if (!Number.isInteger(statusId) || statusId <= 0) {
        return null;
    }

    return statusId;
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


function getDefaultCCoreTaskStatusId(statuses = ccoreTaskStatuses) {
    if (!Array.isArray(statuses) || statuses.length === 0) {
        return "";
    }

    return statuses[0].id;
}


function normalizeCCoreTaskFormSnapshot(formData) {
    return {
        taskName: String(formData.taskName || "").trim(),
        statusId: parseCCoreTaskStatusId(formData.statusId)
    };
}


function setOriginalCCoreTaskFormData(formData) {
    originalCCoreTaskFormData = normalizeCCoreTaskFormSnapshot(formData);
}


function hasCCoreTaskFormChanged(formData) {
    if (!originalCCoreTaskFormData) {
        return true;
    }

    const currentFormData = normalizeCCoreTaskFormSnapshot(formData);

    return (
        currentFormData.taskName !== originalCCoreTaskFormData.taskName ||
        currentFormData.statusId !== originalCCoreTaskFormData.statusId
    );
}


function getCCoreTaskIdFromUrl() {
    const urlParameters = new URLSearchParams(window.location.search);
    return String(urlParameters.get("taskId") || "").trim();
}


function parseCCoreTaskStatusesResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.statuses)) {
        throw new Error("The backend did not return a CCore task status list.");
    }

    return responseData.statuses.map((status) => ({
        id: Number(status.id),
        label: String(status.label || "")
    }));
}


function parseCCoreTaskResponse(responseData) {
    if (!responseData || !responseData.task) {
        throw new Error("The backend did not return a CCore task.");
    }

    return responseData.task;
}


function renderCCoreTaskStatusOptions(statuses = ccoreTaskStatuses, selectElementId = "ccoreTaskStatusInput") {
    const statusInput = document.getElementById(selectElementId);

    if (!statusInput) {
        return;
    }

    statusInput.innerHTML = "";

    if (!Array.isArray(statuses) || statuses.length === 0) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = CCORE_TASK_STATUSES_EMPTY_MESSAGE;
        statusInput.appendChild(option);
        statusInput.disabled = true;
        return;
    }

    statuses.forEach((status) => {
        const option = document.createElement("option");
        option.value = String(status.id);
        option.textContent = status.label;
        statusInput.appendChild(option);
    });

    statusInput.disabled = false;
}


function setCCoreTaskDetailsMode(mode) {
    const isEditMode = mode === "edit";

    document.getElementById("ccoreTaskDetailsTitle").textContent =
        isEditMode ? "CCore Task Details" : "Create CCore Task";

    document.getElementById("ccoreTaskDetailsLegend").textContent =
        isEditMode ? "Task Details" : "Create Task";

    document.getElementById("ccoreTaskDetailsMode").textContent =
        isEditMode ? "Edit mode" : "Create mode";

    document.getElementById("saveCCoreTaskButton").textContent =
        isEditMode ? "Update Task" : "Create Task";

    document.getElementById("deleteCCoreTaskButton").classList.toggle(
        "hidden",
        !isEditMode
    );
}


function getCCoreTaskFormData() {
    const statusInput = getCCoreTaskStatusInput();

    return {
        taskId: document.getElementById("ccoreTaskIdInput").value,
        taskName: document.getElementById("ccoreTaskNameInput").value.trim(),
        statusId: Number(statusInput.value)
    };
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
    document.getElementById("ccoreTaskStatusInput").value = String(getDefaultCCoreTaskStatusId());
    document.getElementById("ccoreTaskCreatedAtInput").value = "—";
    document.getElementById("ccoreTaskDisplayIdInput").value = "New task";

    setCCoreTaskDetailsMode("create");
    setOriginalCCoreTaskFormData(getCCoreTaskFormData());
}


async function loadCCoreTaskStatuses() {
    const statusInput = getCCoreTaskStatusInput();

    if (statusInput) {
        statusInput.innerHTML = `<option value="">${escapeCCoreTaskValue(CCORE_TASK_STATUSES_LOADING_MESSAGE)}</option>`;
        statusInput.disabled = true;
    }

    const responseData = await getJson(CCORE_API_ENDPOINTS.tasks.statuses);
    ccoreTaskStatuses = parseCCoreTaskStatusesResponse(responseData);
    renderCCoreTaskStatusOptions(ccoreTaskStatuses, "ccoreTaskStatusInput");
}


async function loadCCoreTaskDetails(taskId) {
    hideCCoreTaskDetailsMessage();

    const responseData = await getJson(CCORE_API_ENDPOINTS.tasks.byId(taskId));
    const task = parseCCoreTaskResponse(responseData);

    populateCCoreTaskDetails(task);
}


async function saveCCoreTask(taskName, statusId) {
    return postJson(
        CCORE_API_ENDPOINTS.tasks.create,
        {
            taskName,
            statusId
        }
    );
}


async function updateCCoreTask(taskId, taskName, statusId) {
    return putJson(
        CCORE_API_ENDPOINTS.tasks.byId(taskId),
        {
            taskName,
            statusId
        }
    );
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
            responseData = await updateCCoreTask(
                formData.taskId,
                normalizedFormData.taskName,
                normalizedFormData.statusId
            );

            showCCoreTaskDetailsMessage(CCORE_TASK_UPDATED_SUCCESS_MESSAGE, "success");
        } else {
            responseData = await saveCCoreTask(
                normalizedFormData.taskName,
                normalizedFormData.statusId
            );

            showCCoreTaskDetailsMessage(CCORE_TASK_CREATED_SUCCESS_MESSAGE, "success");
        }

        const savedTask = parseCCoreTaskResponse(responseData);
        populateCCoreTaskDetails(savedTask);

        if (!formData.taskId && savedTask.taskId) {
            window.history.replaceState(
                {},
                "",
                `./task-details.html?taskId=${encodeURIComponent(savedTask.taskId)}`
            );
        }

    } catch (error) {
        showCCoreTaskDetailsMessage(error.message || CCORE_TASK_SAVE_ERROR_MESSAGE, "error");
    }
}


async function deleteCCoreTask() {
    const taskId = currentCCoreTaskId;

    if (!taskId) {
        return;
    }

    if (!window.confirm(CCORE_TASK_DELETE_CONFIRM_MESSAGE)) {
        return;
    }

    try {
        await deleteJson(CCORE_API_ENDPOINTS.tasks.byId(taskId));
        window.location.href = "./tasks.html";

    } catch (error) {
        showCCoreTaskDetailsMessage(error.message || CCORE_TASK_DELETE_ERROR_MESSAGE, "error");
    }
}


async function setupCCoreTaskDetailsPage() {
    document.getElementById("ccoreTaskDetailsForm").addEventListener("submit", handleSaveCCoreTaskSubmit);
    document.getElementById("deleteCCoreTaskButton").addEventListener("click", deleteCCoreTask);

    try {
        await loadCCoreTaskStatuses();

        const taskId = getCCoreTaskIdFromUrl();

        if (taskId) {
            await loadCCoreTaskDetails(taskId);
        } else {
            resetCCoreTaskDetailsForCreate();
        }

    } catch (error) {
        console.error("Failed to initialize CCore task details page:", error);
        showCCoreTaskDetailsMessage(
            error.message || CCORE_TASK_DETAILS_ERROR_MESSAGE || CCORE_TASK_STATUSES_ERROR_MESSAGE,
            "error"
        );
    }
}


setupCCoreTaskDetailsPage();

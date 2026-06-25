/*
 * CCore PostgreSQL metrics page controller.
 *
 * Responsibilities:
 * - Load persisted CCore metrics from PostgreSQL through the backend API.
 * - Load metric type options from PostgreSQL reference data.
 * - Create, update, and delete rows in the ccore_metrics table.
 * - Keep frontend endpoint usage centralized through CCORE_API_ENDPOINTS.
 * - Provide compact CRUD UI behavior following the CCore golden vertical slice blueprint.
 */

const CCORE_METRICS_LOADING_MESSAGE =
    "Loading CCore metrics...";

const CCORE_METRIC_TYPES_LOADING_MESSAGE =
    "Loading metric types...";

const CCORE_METRICS_EMPTY_MESSAGE =
    "No PostgreSQL metrics found.";

const CCORE_METRIC_TYPES_EMPTY_MESSAGE =
    "No metric types are configured.";

const CCORE_METRICS_ERROR_MESSAGE =
    "CCore metrics could not be loaded.";

const CCORE_METRIC_TYPES_ERROR_MESSAGE =
    "CCore metric types could not be loaded.";

const CCORE_METRICS_TABLE_COLUMN_COUNT = 5;

let ccoreMetrics = [];
let ccoreMetricTypes = [];
let ccoreMetricSearchTerm = "";


function getCCoreMetricsTableBody() {
    return document.getElementById("ccoreMetricsTableBody");
}


function getCCoreMetricsMessage() {
    return document.getElementById("ccoreMetricsMessage");
}


function getCCoreMetricTypeInput() {
    return document.getElementById("ccoreMetricTypeInput");
}


function escapeCCoreMetricValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function showCCoreMetricsMessage(message, type = "info") {
    const messageElement = getCCoreMetricsMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className = `form-message ${type}`;
    messageElement.textContent = message;
}


function hideCCoreMetricsMessage() {
    const messageElement = getCCoreMetricsMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className = "form-message info hidden";
    messageElement.textContent = "";
}


function renderCCoreMetricsPlaceholder(message) {
    const tableBody = getCCoreMetricsTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = `
        <tr>
            <td colspan="${CCORE_METRICS_TABLE_COLUMN_COUNT}" class="shared-table-empty-state">
                ${escapeCCoreMetricValue(message)}
            </td>
        </tr>
    `;
}


function normalizeCCoreMetricType(metricType) {
    return String(metricType || "")
        .trim()
        .toUpperCase();
}


function formatCCoreMetricDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}


function getDefaultCCoreMetricTypeCode() {
    if (ccoreMetricTypes.length === 0) {
        return "";
    }

    return ccoreMetricTypes[0].code;
}


function getCCoreMetricTypeLabel(metricTypeCode) {
    const normalizedMetricTypeCode = normalizeCCoreMetricType(metricTypeCode);
    const metricType = ccoreMetricTypes.find((candidateMetricType) =>
        normalizeCCoreMetricType(candidateMetricType.code) === normalizedMetricTypeCode
    );

    return metricType ? metricType.label : normalizedMetricTypeCode;
}


function getCCoreMetricSearchableText(metric) {
    return [
        metric.metricId,
        metric.metricName,
        metric.metricKey,
        metric.metricType,
        metric.metricTypeLabel,
        metric.createdAt
    ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
}


function getFilteredCCoreMetrics() {
    const searchTerm = ccoreMetricSearchTerm.trim().toLowerCase();

    if (!searchTerm) {
        return ccoreMetrics;
    }

    return ccoreMetrics.filter((metric) =>
        getCCoreMetricSearchableText(metric).includes(searchTerm)
    );
}


function renderCCoreMetricRow(metric) {
    const metricId = metric.metricId;
    const metricName = metric.metricName;
    const metricKey = metric.metricKey;
    const metricType = normalizeCCoreMetricType(metric.metricType);
    const metricTypeLabel = metric.metricTypeLabel || getCCoreMetricTypeLabel(metricType);

    return `
        <tr data-metric-id="${escapeCCoreMetricValue(metricId)}">
            <td>
                <div class="ccore-metric-name-cell">
                    <span class="ccore-metric-name">${escapeCCoreMetricValue(metricName)}</span>
                    <span class="ccore-metric-id">${escapeCCoreMetricValue(metricId)}</span>
                </div>
            </td>
            <td>${escapeCCoreMetricValue(metricKey)}</td>
            <td>
                <span class="ccore-metric-type" title="${escapeCCoreMetricValue(metricType)}">
                    ${escapeCCoreMetricValue(metricTypeLabel)}
                </span>
            </td>
            <td>${escapeCCoreMetricValue(formatCCoreMetricDate(metric.createdAt))}</td>
            <td>
                <div class="ccore-metric-row-actions">
                    <button class="shared-button secondary" type="button" data-action="edit" data-metric-id="${escapeCCoreMetricValue(metricId)}">
                        Edit
                    </button>
                    <button class="shared-button secondary" type="button" data-action="delete" data-metric-id="${escapeCCoreMetricValue(metricId)}">
                        Delete
                    </button>
                </div>
            </td>
        </tr>
    `;
}


function updateCCoreMetricsCount(filteredMetrics) {
    const countElement = document.getElementById("ccoreMetricsCount");

    if (!countElement) {
        return;
    }

    const count = filteredMetrics.length;
    countElement.textContent = `${count} ${count === 1 ? "metric" : "metrics"}`;
}


function renderCCoreMetrics() {
    const filteredMetrics = getFilteredCCoreMetrics();

    if (filteredMetrics.length === 0) {
        renderCCoreMetricsPlaceholder(CCORE_METRICS_EMPTY_MESSAGE);
        updateCCoreMetricsCount(filteredMetrics);
        return;
    }

    const tableBody = getCCoreMetricsTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = filteredMetrics
        .map(renderCCoreMetricRow)
        .join("");

    updateCCoreMetricsCount(filteredMetrics);
}


function parseCCoreMetricsResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.metrics)) {
        throw new Error("The backend did not return a CCore metric list.");
    }

    return responseData.metrics;
}


function parseCCoreMetricTypesResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.metricTypes)) {
        throw new Error("The backend did not return a CCore metric type list.");
    }

    return responseData.metricTypes;
}


function renderCCoreMetricTypeOptions() {
    const metricTypeInput = getCCoreMetricTypeInput();

    if (!metricTypeInput) {
        return;
    }

    if (ccoreMetricTypes.length === 0) {
        metricTypeInput.innerHTML = `<option value="">${escapeCCoreMetricValue(CCORE_METRIC_TYPES_EMPTY_MESSAGE)}</option>`;
        metricTypeInput.disabled = true;
        return;
    }

    metricTypeInput.innerHTML = ccoreMetricTypes
        .map((metricType) => `
            <option value="${escapeCCoreMetricValue(metricType.code)}">
                ${escapeCCoreMetricValue(metricType.label)}
            </option>
        `)
        .join("");

    metricTypeInput.disabled = false;
}


async function loadCCoreMetricTypes() {
    const metricTypeInput = getCCoreMetricTypeInput();

    if (metricTypeInput) {
        metricTypeInput.innerHTML = `<option value="">${escapeCCoreMetricValue(CCORE_METRIC_TYPES_LOADING_MESSAGE)}</option>`;
        metricTypeInput.disabled = true;
    }

    const responseData = await getJson(CCORE_API_ENDPOINTS.metrics.types);
    ccoreMetricTypes = parseCCoreMetricTypesResponse(responseData);
    renderCCoreMetricTypeOptions();
}


async function loadCCoreMetrics() {
    hideCCoreMetricsMessage();
    renderCCoreMetricsPlaceholder(CCORE_METRICS_LOADING_MESSAGE);

    try {
        const responseData = await getJson(CCORE_API_ENDPOINTS.metrics.list);
        ccoreMetrics = parseCCoreMetricsResponse(responseData);

        enableCCoreMetricSearch();
        renderCCoreMetrics();

        if (ccoreMetrics.length === 0) {
            showCCoreMetricsMessage(CCORE_METRICS_EMPTY_MESSAGE, "info");
        }

    } catch (error) {
        console.error("Failed to load CCore metrics:", error);
        ccoreMetrics = [];
        renderCCoreMetricsPlaceholder(CCORE_METRICS_ERROR_MESSAGE);
        showCCoreMetricsMessage(error.message || CCORE_METRICS_ERROR_MESSAGE, "error");
    }
}


function getMetricFormData() {
    return {
        metricId: document.getElementById("ccoreMetricIdInput").value,
        metricName: document.getElementById("ccoreMetricNameInput").value.trim(),
        metricKey: document.getElementById("ccoreMetricKeyInput").value.trim(),
        metricType: getCCoreMetricTypeInput().value
    };
}


function resetMetricForm() {
    document.getElementById("ccoreMetricIdInput").value = "";
    document.getElementById("ccoreMetricNameInput").value = "";
    document.getElementById("ccoreMetricKeyInput").value = "";
    getCCoreMetricTypeInput().value = getDefaultCCoreMetricTypeCode();
    document.getElementById("ccoreMetricFormLegend").textContent = "Create Metric";
    document.getElementById("saveCCoreMetricButton").textContent = "Create Metric";
}


function editMetric(metricId) {
    const metric = ccoreMetrics.find((candidateMetric) =>
        String(candidateMetric.metricId) === String(metricId)
    );

    if (!metric) {
        showCCoreMetricsMessage("Metric could not be found in the current list.", "error");
        return;
    }

    document.getElementById("ccoreMetricIdInput").value = metric.metricId;
    document.getElementById("ccoreMetricNameInput").value = metric.metricName || "";
    document.getElementById("ccoreMetricKeyInput").value = metric.metricKey || "";
    getCCoreMetricTypeInput().value = normalizeCCoreMetricType(metric.metricType);
    document.getElementById("ccoreMetricFormLegend").textContent = "Edit Metric";
    document.getElementById("saveCCoreMetricButton").textContent = "Update Metric";
}


async function saveMetric(event) {
    event.preventDefault();
    hideCCoreMetricsMessage();

    const formData = getMetricFormData();

    if (!formData.metricName) {
        showCCoreMetricsMessage("Metric name is required.", "error");
        return;
    }

    if (!formData.metricKey) {
        showCCoreMetricsMessage("Metric key is required.", "error");
        return;
    }

    if (!formData.metricType) {
        showCCoreMetricsMessage("Metric type is required.", "error");
        return;
    }

    try {
        if (formData.metricId) {
            await putJson(
                CCORE_API_ENDPOINTS.metrics.byId(formData.metricId),
                {
                    metricName: formData.metricName,
                    metricKey: formData.metricKey,
                    metricType: formData.metricType
                }
            );

            showCCoreMetricsMessage("Metric updated successfully.", "success");
        } else {
            await postJson(
                CCORE_API_ENDPOINTS.metrics.create,
                {
                    metricName: formData.metricName,
                    metricKey: formData.metricKey,
                    metricType: formData.metricType
                }
            );

            showCCoreMetricsMessage("Metric created successfully.", "success");
        }

        resetMetricForm();
        await loadCCoreMetrics();

    } catch (error) {
        showCCoreMetricsMessage(error.message || "Metric could not be saved.", "error");
    }
}


async function deleteMetric(metricId) {
    if (!window.confirm("Delete this CCore metric?")) {
        return;
    }

    try {
        await deleteJson(CCORE_API_ENDPOINTS.metrics.byId(metricId));
        showCCoreMetricsMessage("Metric deleted successfully.", "success");
        resetMetricForm();
        await loadCCoreMetrics();

    } catch (error) {
        showCCoreMetricsMessage(error.message || "Metric could not be deleted.", "error");
    }
}


function setupMetricTableActions() {
    const tableBody = getCCoreMetricsTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.addEventListener("click", (event) => {
        const actionButton = event.target.closest("button[data-action]");

        if (!actionButton) {
            return;
        }

        const metricId = actionButton.dataset.metricId;
        const action = actionButton.dataset.action;

        if (action === "edit") {
            editMetric(metricId);
            return;
        }

        if (action === "delete") {
            deleteMetric(metricId);
        }
    });
}


function enableCCoreMetricSearch() {
    const searchInput = document.getElementById("ccoreMetricsSearchInput");

    if (!searchInput) {
        return;
    }

    searchInput.disabled = false;
}


function setupCCoreMetricSearch() {
    const searchInput = document.getElementById("ccoreMetricsSearchInput");

    if (!searchInput) {
        return;
    }

    searchInput.addEventListener("input", () => {
        ccoreMetricSearchTerm = searchInput.value;
        renderCCoreMetrics();
    });
}


async function setupCCoreMetricsPage() {
    document.getElementById("ccoreMetricForm").addEventListener("submit", saveMetric);
    document.getElementById("resetCCoreMetricFormButton").addEventListener("click", resetMetricForm);
    document.getElementById("refreshCCoreMetricsButton").addEventListener("click", loadCCoreMetrics);

    setupMetricTableActions();
    setupCCoreMetricSearch();

    try {
        await loadCCoreMetricTypes();
        resetMetricForm();
        await loadCCoreMetrics();
    } catch (error) {
        console.error("Failed to initialize CCore metrics page:", error);
        renderCCoreMetricsPlaceholder(CCORE_METRICS_ERROR_MESSAGE);
        showCCoreMetricsMessage(error.message || CCORE_METRIC_TYPES_ERROR_MESSAGE, "error");
    }
}


setupCCoreMetricsPage();

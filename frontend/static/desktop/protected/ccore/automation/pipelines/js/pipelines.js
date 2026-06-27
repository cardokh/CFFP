/*
 * CCore PostgreSQL pipelines list page controller.
 *
 * Responsibilities:
 * - Load persisted CCore pipelines from PostgreSQL through the backend API.
 * - Render a searchable, sortable, paginated pipeline list.
 * - Open the pipeline details page when a pipeline row is selected.
 * - Keep frontend endpoint usage centralized through CCORE_API_ENDPOINTS.
 */

const CCORE_PIPELINES_LOADING_MESSAGE =
    "Loading CCore pipelines...";

const CCORE_PIPELINES_EMPTY_MESSAGE =
    "No PostgreSQL pipelines found.";

const CCORE_PIPELINES_ERROR_MESSAGE =
    "CCore pipelines could not be loaded.";

const CCORE_PIPELINES_TABLE_COLUMN_COUNT = 3;
const CCORE_PIPELINES_PAGE_SIZE = 5;

let ccorePipelines = [];
let ccorePipelineSearchTerm = "";
let ccorePipelinesCurrentPage = 1;
let ccorePipelinesSortKey = "pipelineName";
let ccorePipelinesSortDirection = "asc";


function getCCorePipelinesTableBody() {
    return document.getElementById("ccorePipelinesTableBody");
}


function getCCorePipelinesMessage() {
    return document.getElementById("ccorePipelinesMessage");
}


function escapeCCorePipelineValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function showCCorePipelinesMessage(message, type = "info") {
    const messageElement = getCCorePipelinesMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className = `form-message ${type}`;
    messageElement.textContent = message;
}


function hideCCorePipelinesMessage() {
    const messageElement = getCCorePipelinesMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className = "form-message info hidden";
    messageElement.textContent = "";
}


function renderCCorePipelinesPlaceholder(message) {
    const tableBody = getCCorePipelinesTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = `
        <tr>
            <td colspan="${CCORE_PIPELINES_TABLE_COLUMN_COUNT}" class="shared-table-empty-state">
                ${escapeCCorePipelineValue(message)}
            </td>
        </tr>
    `;
}


function normalizeCCorePipelineStatus(status) {
    return String(status || "")
        .trim()
        .toUpperCase();
}


function formatCCorePipelineDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}


function getCCorePipelineSearchableText(pipeline) {
    return [
        pipeline.pipelineId,
        pipeline.pipelineName,
        pipeline.pipelineStatusLabel,
        pipeline.pipelineStatusLabel,
        pipeline.createdAt
    ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
}


function getFilteredCCorePipelines() {
    const searchTerm = ccorePipelineSearchTerm.trim().toLowerCase();

    if (!searchTerm) {
        return ccorePipelines;
    }

    return ccorePipelines.filter((pipeline) =>
        getCCorePipelineSearchableText(pipeline).includes(searchTerm)
    );
}


function getCCorePipelineSortValue(pipeline, sortKey) {
    if (sortKey === "pipelineStatusLabel") {
        return String(pipeline.pipelineStatusLabel || pipeline.pipelineStatusLabel || "").toLowerCase();
    }

    if (sortKey === "createdAt") {
        const date = new Date(pipeline.createdAt || "");
        return Number.isNaN(date.getTime()) ? 0 : date.getTime();
    }

    return String(pipeline[sortKey] || "").toLowerCase();
}


function getSortedCCorePipelines(pipelines) {
    return [...pipelines].sort((firstPipeline, secondPipeline) => {
        const firstValue = getCCorePipelineSortValue(firstPipeline, ccorePipelinesSortKey);
        const secondValue = getCCorePipelineSortValue(secondPipeline, ccorePipelinesSortKey);

        if (firstValue < secondValue) {
            return ccorePipelinesSortDirection === "asc" ? -1 : 1;
        }

        if (firstValue > secondValue) {
            return ccorePipelinesSortDirection === "asc" ? 1 : -1;
        }

        return 0;
    });
}


function getCCorePipelinesTotalPages(totalPipelines) {
    return Math.max(1, Math.ceil(totalPipelines / CCORE_PIPELINES_PAGE_SIZE));
}


function clampCCorePipelinesCurrentPage(totalPipelines) {
    const totalPages = getCCorePipelinesTotalPages(totalPipelines);

    if (ccorePipelinesCurrentPage > totalPages) {
        ccorePipelinesCurrentPage = totalPages;
    }

    if (ccorePipelinesCurrentPage < 1) {
        ccorePipelinesCurrentPage = 1;
    }
}


function getPaginatedCCorePipelines(pipelines) {
    clampCCorePipelinesCurrentPage(pipelines.length);

    const startIndex = (ccorePipelinesCurrentPage - 1) * CCORE_PIPELINES_PAGE_SIZE;
    const endIndex = startIndex + CCORE_PIPELINES_PAGE_SIZE;

    return pipelines.slice(startIndex, endIndex);
}


function getVisibleCCorePipelines() {
    const filteredPipelines = getFilteredCCorePipelines();
    const sortedPipelines = getSortedCCorePipelines(filteredPipelines);
    const paginatedPipelines = getPaginatedCCorePipelines(sortedPipelines);

    return {
        filteredPipelines,
        paginatedPipelines,
        totalPages: getCCorePipelinesTotalPages(filteredPipelines.length)
    };
}


function getCCorePipelineDetailsUrl(pipelineId) {
    return `./pipeline-details.html?pipelineId=${encodeURIComponent(pipelineId)}`;
}


function renderCCorePipelineRow(pipeline) {
    const pipelineId = pipeline.pipelineId;
    const pipelineName = pipeline.pipelineName;
    const status = normalizeCCorePipelineStatus(pipeline.pipelineStatusLabel);
    const pipelineStatusLabel = pipeline.pipelineStatusLabel || status;

    return `
        <tr data-pipeline-id="${escapeCCorePipelineValue(pipelineId)}" tabindex="0" aria-label="Open pipeline ${escapeCCorePipelineValue(pipelineName)}">
            <td>
                <div class="ccore-pipeline-name-cell">
                    <span class="ccore-pipeline-name">${escapeCCorePipelineValue(pipelineName)}</span>
                </div>
            </td>
            <td>
                <span class="ccore-pipeline-status" title="${escapeCCorePipelineValue(status)}">
                    ${escapeCCorePipelineValue(pipelineStatusLabel)}
                </span>
            </td>
            <td>${escapeCCorePipelineValue(formatCCorePipelineDate(pipeline.createdAt))}</td>
        </tr>
    `;
}


function updateCCorePipelinesCount(filteredPipelines) {
    const countElement = document.getElementById("ccorePipelinesCount");

    if (!countElement) {
        return;
    }

    const count = filteredPipelines.length;
    countElement.textContent = `${count} ${count === 1 ? "pipeline" : "pipelines"}`;
}


function updateCCorePipelinesPagination(totalPages) {
    const previousButton = document.getElementById("ccorePipelinesPreviousPageButton");
    const nextButton = document.getElementById("ccorePipelinesNextPageButton");
    const pageIndicator = document.getElementById("ccorePipelinesPageIndicator");

    if (pageIndicator) {
        pageIndicator.textContent = `Page ${ccorePipelinesCurrentPage} of ${totalPages}`;
    }

    if (previousButton) {
        previousButton.disabled = ccorePipelinesCurrentPage <= 1;
    }

    if (nextButton) {
        nextButton.disabled = ccorePipelinesCurrentPage >= totalPages;
    }
}


function updateCCorePipelineSortIndicators() {
    document
        .querySelectorAll(".ccore-pipelines-table .shared-table-sort-button")
        .forEach((button) => {
            const isActive = button.dataset.sortKey === ccorePipelinesSortKey;

            button.classList.toggle(
                "sorted-asc",
                isActive && ccorePipelinesSortDirection === "asc"
            );

            button.classList.toggle(
                "sorted-desc",
                isActive && ccorePipelinesSortDirection === "desc"
            );

            button.dataset.sortDirection = isActive
                ? ccorePipelinesSortDirection
                : "";
        });
}


function renderCCorePipelines() {
    const visiblePipelines = getVisibleCCorePipelines();

    if (visiblePipelines.filteredPipelines.length === 0) {
        renderCCorePipelinesPlaceholder(CCORE_PIPELINES_EMPTY_MESSAGE);
        updateCCorePipelinesCount(visiblePipelines.filteredPipelines);
        updateCCorePipelinesPagination(visiblePipelines.totalPages);
        updateCCorePipelineSortIndicators();
        return;
    }

    const tableBody = getCCorePipelinesTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = visiblePipelines.paginatedPipelines
        .map(renderCCorePipelineRow)
        .join("");

    updateCCorePipelinesCount(visiblePipelines.filteredPipelines);
    updateCCorePipelinesPagination(visiblePipelines.totalPages);
    updateCCorePipelineSortIndicators();
}


function parseCCorePipelinesResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.pipelines)) {
        throw new Error("The backend did not return a CCore pipeline list.");
    }

    return responseData.pipelines;
}


async function loadCCorePipelines() {
    hideCCorePipelinesMessage();
    renderCCorePipelinesPlaceholder(CCORE_PIPELINES_LOADING_MESSAGE);

    try {
        const responseData = await getJson(CCORE_API_ENDPOINTS.pipelines.list);
        ccorePipelines = parseCCorePipelinesResponse(responseData);
        ccorePipelinesCurrentPage = 1;

        enableCCorePipelineSearch();
        renderCCorePipelines();

        if (ccorePipelines.length === 0) {
            showCCorePipelinesMessage(CCORE_PIPELINES_EMPTY_MESSAGE, "info");
        }

    } catch (error) {
        console.error("Failed to load CCore pipelines:", error);
        ccorePipelines = [];
        ccorePipelinesCurrentPage = 1;
        renderCCorePipelinesPlaceholder(CCORE_PIPELINES_ERROR_MESSAGE);
        updateCCorePipelinesPagination(1);
        showCCorePipelinesMessage(error.message || CCORE_PIPELINES_ERROR_MESSAGE, "error");
    }
}


function openCCorePipelineDetails(pipelineId) {
    if (!pipelineId) {
        return;
    }

    window.location.href = getCCorePipelineDetailsUrl(pipelineId);
}


function setupCCorePipelineRowNavigation() {
    const tableBody = getCCorePipelinesTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.addEventListener("click", (event) => {
        const pipelineRow = event.target.closest("tr[data-pipeline-id]");

        if (!pipelineRow) {
            return;
        }

        openCCorePipelineDetails(pipelineRow.dataset.pipelineId);
    });

    tableBody.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
            return;
        }

        const pipelineRow = event.target.closest("tr[data-pipeline-id]");

        if (!pipelineRow) {
            return;
        }

        event.preventDefault();
        openCCorePipelineDetails(pipelineRow.dataset.pipelineId);
    });
}


function enableCCorePipelineSearch() {
    const searchInput = document.getElementById("ccorePipelinesSearchInput");

    if (!searchInput) {
        return;
    }

    searchInput.disabled = false;
}


function setupCCorePipelineSorting() {
    document
        .querySelectorAll(".ccore-pipelines-table .shared-table-sort-button")
        .forEach((button) => {
            button.addEventListener("click", () => {
                const sortKey = button.dataset.sortKey;

                if (!sortKey) {
                    return;
                }

                if (ccorePipelinesSortKey === sortKey) {
                    ccorePipelinesSortDirection = ccorePipelinesSortDirection === "asc"
                        ? "desc"
                        : "asc";
                } else {
                    ccorePipelinesSortKey = sortKey;
                    ccorePipelinesSortDirection = "asc";
                }

                ccorePipelinesCurrentPage = 1;
                renderCCorePipelines();
            });
        });

    updateCCorePipelineSortIndicators();
}


function setupCCorePipelineSearch() {
    const searchInput = document.getElementById("ccorePipelinesSearchInput");

    if (!searchInput) {
        return;
    }

    searchInput.addEventListener("input", () => {
        ccorePipelineSearchTerm = searchInput.value;
        ccorePipelinesCurrentPage = 1;
        renderCCorePipelines();
    });
}


function setupCCorePipelinePagination() {
    const previousButton = document.getElementById("ccorePipelinesPreviousPageButton");
    const nextButton = document.getElementById("ccorePipelinesNextPageButton");

    if (previousButton) {
        previousButton.addEventListener("click", () => {
            ccorePipelinesCurrentPage -= 1;
            renderCCorePipelines();
        });
    }

    if (nextButton) {
        nextButton.addEventListener("click", () => {
            ccorePipelinesCurrentPage += 1;
            renderCCorePipelines();
        });
    }
}


async function setupCCorePipelinesPage() {
    document.getElementById("refreshCCorePipelinesButton").addEventListener("click", loadCCorePipelines);

    setupCCorePipelineRowNavigation();
    setupCCorePipelineSearch();
    setupCCorePipelineSorting();
    setupCCorePipelinePagination();

    await loadCCorePipelines();
}


setupCCorePipelinesPage();

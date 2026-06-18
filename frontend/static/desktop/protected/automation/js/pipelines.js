/*
 * Automation pipelines page controller.
 *
 * Responsibilities:
 * - Load registered automation pipelines from CCore.
 * - Render a compact pipeline summary list.
 * - Use shared table search and pagination helpers.
 * - Provide client-side sorting for the pipeline summary list.
 * - Keep execution concerns out of the registry/list slice.
 * - Handle loading, empty, and error states.
 */

const AUTOMATION_PIPELINES_EMPTY_MESSAGE =
    "No automation pipelines are currently registered.";

const AUTOMATION_PIPELINES_LOADING_MESSAGE =
    "Loading automation pipelines...";

const AUTOMATION_PIPELINES_ERROR_MESSAGE =
    "Automation pipelines could not be loaded.";

const AUTOMATION_PIPELINES_TABLE_COLUMN_COUNT = 5;
const AUTOMATION_PIPELINES_ROWS_PER_PAGE = 8;

let automationPipelines = [];
let automationPipelinesCurrentPage = 1;
let automationPipelinesSortKey = "name";
let automationPipelinesSortDirection = "asc";


function getAutomationPipelinesTableBody() {
    return document.getElementById(
        "automationPipelinesTableBody"
    );
}


function getAutomationPipelinesMessage() {
    return document.getElementById(
        "automationPipelinesMessage"
    );
}


function escapeAutomationPipelineValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function normalizeAutomationPipelineStatus(status) {
    return String(status || "unknown")
        .trim()
        .toLowerCase();
}


function showAutomationPipelinesMessage(message, type = "info") {
    const messageElement =
        getAutomationPipelinesMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        `form-message ${type}`;

    messageElement.textContent =
        message;
}


function hideAutomationPipelinesMessage() {
    const messageElement =
        getAutomationPipelinesMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        "form-message info hidden";

    messageElement.textContent =
        "";
}


function renderAutomationPipelinesPlaceholder(message) {
    const tableBody =
        getAutomationPipelinesTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = `
        <tr>
            <td colspan="${AUTOMATION_PIPELINES_TABLE_COLUMN_COUNT}" class="shared-table-empty-state">
                ${escapeAutomationPipelineValue(message)}
            </td>
        </tr>
    `;
}


function getAutomationPipelineStepSummary(pipeline) {
    const steps = Array.isArray(pipeline.steps)
        ? pipeline.steps
        : [];

    if (steps.length === 0) {
        return "No steps";
    }

    return `${steps.length} step${steps.length === 1 ? "" : "s"}`;
}


function getAutomationPipelineSearchableText(pipeline) {
    const steps = Array.isArray(pipeline.steps)
        ? pipeline.steps
        : [];

    const stepText = steps
        .map((step) => [
            step.id,
            step.name,
            step.task_id
        ].filter(Boolean).join(" "))
        .join(" ");

    return [
        pipeline.id,
        pipeline.name,
        pipeline.description,
        pipeline.category,
        pipeline.status,
        pipeline.execution_mode,
        pipeline.failure_strategy,
        stepText
    ]
        .filter(Boolean)
        .join(" ");
}


function getAutomationPipelineSortValue(pipeline, sortKey) {
    if (sortKey === "status") {
        return normalizeAutomationPipelineStatus(
            pipeline.status
        );
    }

    return String(pipeline[sortKey] || "")
        .trim()
        .toLowerCase();
}


function getSortedAutomationPipelines(pipelines) {
    return [...pipelines].sort((firstPipeline, secondPipeline) => {
        const firstValue =
            getAutomationPipelineSortValue(
                firstPipeline,
                automationPipelinesSortKey
            );

        const secondValue =
            getAutomationPipelineSortValue(
                secondPipeline,
                automationPipelinesSortKey
            );

        if (firstValue < secondValue) {
            return automationPipelinesSortDirection === "asc" ? -1 : 1;
        }

        if (firstValue > secondValue) {
            return automationPipelinesSortDirection === "asc" ? 1 : -1;
        }

        return 0;
    });
}


function getFilteredAutomationPipelines() {
    const searchTerm =
        getTableSearchInputValue(
            "automationPipelinesSearchInput"
        );

    const filteredPipelines =
        filterTableItems(
            automationPipelines,
            searchTerm,
            getAutomationPipelineSearchableText
        );

    return getSortedAutomationPipelines(
        filteredPipelines
    );
}


function renderAutomationPipelineRow(pipeline) {
    const status =
        normalizeAutomationPipelineStatus(
            pipeline.status
        );

    return `
        <tr>
            <td>
                <span class="automation-tasks-status ${escapeAutomationPipelineValue(status)}">
                    ${escapeAutomationPipelineValue(status)}
                </span>
            </td>

            <td>
                <div class="automation-tasks-name-cell">
                    <span class="automation-tasks-name">
                        ${escapeAutomationPipelineValue(pipeline.name)}
                    </span>

                    <span class="automation-tasks-id" title="${escapeAutomationPipelineValue(pipeline.id)}">
                        ${escapeAutomationPipelineValue(pipeline.id)}
                    </span>
                </div>
            </td>

            <td>
                ${escapeAutomationPipelineValue(pipeline.category)}
            </td>

            <td>
                <div class="automation-tasks-name-cell">
                    <span>${escapeAutomationPipelineValue(pipeline.execution_mode)}</span>
                    <span class="automation-tasks-id">${escapeAutomationPipelineValue(pipeline.failure_strategy)}</span>
                </div>
            </td>

            <td>
                ${escapeAutomationPipelineValue(getAutomationPipelineStepSummary(pipeline))}
            </td>
        </tr>
    `;
}


function updateAutomationPipelinesCounts(filteredPipelines) {
    const totalCountElement =
        document.getElementById(
            "automationPipelinesCount"
        );

    const filteredCountElement =
        document.getElementById(
            "automationPipelinesFilteredCount"
        );

    if (totalCountElement) {
        totalCountElement.textContent =
            `${automationPipelines.length} pipeline${automationPipelines.length === 1 ? "" : "s"}`;
    }

    if (filteredCountElement) {
        filteredCountElement.textContent =
            `${filteredPipelines.length} shown`;
    }
}


function updateAutomationPipelinesSortIndicators() {
    document
        .querySelectorAll(".automation-pipelines-table .shared-table-sort-button")
        .forEach((button) => {
            const isActive =
                button.dataset.sortKey === automationPipelinesSortKey;

            button.dataset.sortDirection =
                isActive
                    ? automationPipelinesSortDirection
                    : "";

            button.classList.toggle(
                "sorted-asc",
                isActive && automationPipelinesSortDirection === "asc"
            );

            button.classList.toggle(
                "sorted-desc",
                isActive && automationPipelinesSortDirection === "desc"
            );
        });
}


function renderAutomationPipelines() {
    const tableBody =
        getAutomationPipelinesTableBody();

    if (!tableBody) {
        return;
    }

    if (!Array.isArray(automationPipelines) || automationPipelines.length === 0) {
        updateAutomationPipelinesCounts([]);
        renderAutomationPipelinesPlaceholder(
            AUTOMATION_PIPELINES_EMPTY_MESSAGE
        );
        return;
    }

    const filteredPipelines =
        getFilteredAutomationPipelines();

    updateAutomationPipelinesCounts(
        filteredPipelines
    );

    if (filteredPipelines.length === 0) {
        renderAutomationPipelinesPlaceholder(
            "No automation pipelines match the current search."
        );
        updateTablePaginationControls({
            items: filteredPipelines,
            rowsPerPage: AUTOMATION_PIPELINES_ROWS_PER_PAGE,
            currentPage: 1,
            previousButtonId: "automationPipelinesPreviousPageButton",
            nextButtonId: "automationPipelinesNextPageButton",
            statusElementId: "automationPipelinesPaginationStatus"
        });
        return;
    }

    const totalPages =
        getTableTotalPages(
            filteredPipelines,
            AUTOMATION_PIPELINES_ROWS_PER_PAGE
        );

    automationPipelinesCurrentPage =
        clampTablePage(
            automationPipelinesCurrentPage,
            totalPages
        );

    const pagedPipelines =
        getPagedTableItems(
            filteredPipelines,
            automationPipelinesCurrentPage,
            AUTOMATION_PIPELINES_ROWS_PER_PAGE
        );

    tableBody.innerHTML =
        pagedPipelines
            .map(renderAutomationPipelineRow)
            .join("");

    automationPipelinesCurrentPage =
        updateTablePaginationControls({
            items: filteredPipelines,
            rowsPerPage: AUTOMATION_PIPELINES_ROWS_PER_PAGE,
            currentPage: automationPipelinesCurrentPage,
            previousButtonId: "automationPipelinesPreviousPageButton",
            nextButtonId: "automationPipelinesNextPageButton",
            statusElementId: "automationPipelinesPaginationStatus"
        });

    updateAutomationPipelinesSortIndicators();
}


function parseAutomationPipelinesResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.pipelines)) {
        throw new Error(
            "The backend did not return an automation pipeline list."
        );
    }

    return responseData.pipelines;
}


async function loadAutomationPipelines() {
    hideAutomationPipelinesMessage();

    automationPipelines = [];
    automationPipelinesCurrentPage = 1;

    renderAutomationPipelinesPlaceholder(
        AUTOMATION_PIPELINES_LOADING_MESSAGE
    );

    try {
        const responseData =
            await getJson(
                CCORE_API_ENDPOINTS.automation.pipelines.list
            );

        automationPipelines =
            parseAutomationPipelinesResponse(
                responseData
            );

        enableTableSearchInput(
            "automationPipelinesSearchInput"
        );

        renderAutomationPipelines();

        if (automationPipelines.length === 0) {
            showAutomationPipelinesMessage(
                AUTOMATION_PIPELINES_EMPTY_MESSAGE,
                "info"
            );
        }

    } catch (error) {
        console.error(
            "Failed to load automation pipelines:",
            error
        );

        renderAutomationPipelinesPlaceholder(
            AUTOMATION_PIPELINES_ERROR_MESSAGE
        );

        showAutomationPipelinesMessage(
            error.message || AUTOMATION_PIPELINES_ERROR_MESSAGE,
            "error"
        );
    }
}


function setupAutomationPipelinesEvents() {
    const tasksLink =
        document.getElementById(
            "automationTasksLink"
        );

    if (tasksLink) {
        tasksLink.href =
            LLA_PATHS.desktop.protected.automation.tasks;
    }

    const refreshButton =
        document.getElementById(
            "refreshAutomationPipelinesButton"
        );

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            () => {
                loadAutomationPipelines();
            }
        );
    }

    const searchInput =
        document.getElementById(
            "automationPipelinesSearchInput"
        );

    if (searchInput) {
        searchInput.addEventListener(
            "input",
            () => {
                automationPipelinesCurrentPage = 1;
                renderAutomationPipelines();
            }
        );
    }

    const previousButton =
        document.getElementById(
            "automationPipelinesPreviousPageButton"
        );

    if (previousButton) {
        previousButton.addEventListener(
            "click",
            () => {
                automationPipelinesCurrentPage -= 1;
                renderAutomationPipelines();
            }
        );
    }

    const nextButton =
        document.getElementById(
            "automationPipelinesNextPageButton"
        );

    if (nextButton) {
        nextButton.addEventListener(
            "click",
            () => {
                automationPipelinesCurrentPage += 1;
                renderAutomationPipelines();
            }
        );
    }

    document
        .querySelectorAll(".automation-pipelines-table .shared-table-sort-button")
        .forEach((button) => {
            button.addEventListener(
                "click",
                () => {
                    const selectedSortKey =
                        button.dataset.sortKey;

                    if (!selectedSortKey) {
                        return;
                    }

                    if (automationPipelinesSortKey === selectedSortKey) {
                        automationPipelinesSortDirection =
                            automationPipelinesSortDirection === "asc"
                                ? "desc"
                                : "asc";
                    } else {
                        automationPipelinesSortKey =
                            selectedSortKey;
                        automationPipelinesSortDirection =
                            "asc";
                    }

                    automationPipelinesCurrentPage = 1;
                    renderAutomationPipelines();
                }
            );
        });
}


function initializeAutomationPipelinesPage() {
    setupAutomationPipelinesEvents();
    loadAutomationPipelines();
}


initializeAutomationPipelinesPage();

/*
 * Automation tasks page controller.
 *
 * Responsibilities:
 * - Load registered automation tasks from CCore.
 * - Render a compact task summary list.
 * - Use shared table search and pagination helpers.
 * - Provide client-side sorting for the task summary list.
 * - Navigate to task details without hardcoding detail page URLs.
 * - Keep implementation paths out of the list page; details belong on the task details page.
 * - Handle loading, empty, and error states.
 *
 * Platform dependencies are loaded by protected-workspace.js.
 */

const AUTOMATION_TASKS_EMPTY_MESSAGE =
    "No automation tasks are currently registered.";

const AUTOMATION_TASKS_LOADING_MESSAGE =
    "Loading automation tasks...";

const AUTOMATION_TASKS_ERROR_MESSAGE =
    "Automation tasks could not be loaded.";

const AUTOMATION_TASKS_TABLE_COLUMN_COUNT = 4;
const AUTOMATION_TASKS_ROWS_PER_PAGE = 8;

let automationTasks = [];
let automationTasksCurrentPage = 1;
let automationTasksSortKey = "name";
let automationTasksSortDirection = "asc";


function getAutomationTasksTableBody() {
    return document.getElementById(
        "automationTasksTableBody"
    );
}


function getAutomationTasksMessage() {
    return document.getElementById(
        "automationTasksMessage"
    );
}


function escapeAutomationTaskValue(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function normalizeAutomationTaskStatus(status) {
    return String(status || "unknown")
        .trim()
        .toLowerCase();
}


function getAutomationTaskDetailsPath(taskId) {
    return LLA_PATHS.desktop.protected.automation.taskDetails(
        taskId
    );
}


function showAutomationTasksMessage(message, type = "info") {
    const messageElement =
        getAutomationTasksMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        `form-message ${type}`;

    messageElement.textContent =
        message;
}


function hideAutomationTasksMessage() {
    const messageElement =
        getAutomationTasksMessage();

    if (!messageElement) {
        return;
    }

    messageElement.className =
        "form-message info hidden";

    messageElement.textContent =
        "";
}


function renderAutomationTasksPlaceholder(message) {
    const tableBody =
        getAutomationTasksTableBody();

    if (!tableBody) {
        return;
    }

    tableBody.innerHTML = `
        <tr>
            <td colspan="${AUTOMATION_TASKS_TABLE_COLUMN_COUNT}" class="shared-table-empty-state">
                ${escapeAutomationTaskValue(message)}
            </td>
        </tr>
    `;
}


function getAutomationTaskSearchableText(task) {
    return [
        task.id,
        task.name,
        task.description,
        task.category,
        task.status
    ]
        .filter(Boolean)
        .join(" ");
}


function getAutomationTaskSortValue(task, sortKey) {
    if (sortKey === "status") {
        return normalizeAutomationTaskStatus(
            task.status
        );
    }

    return String(task[sortKey] || "")
        .trim()
        .toLowerCase();
}


function getSortedAutomationTasks(tasks) {
    return [...tasks].sort((firstTask, secondTask) => {
        const firstValue =
            getAutomationTaskSortValue(
                firstTask,
                automationTasksSortKey
            );

        const secondValue =
            getAutomationTaskSortValue(
                secondTask,
                automationTasksSortKey
            );

        if (firstValue < secondValue) {
            return automationTasksSortDirection === "asc" ? -1 : 1;
        }

        if (firstValue > secondValue) {
            return automationTasksSortDirection === "asc" ? 1 : -1;
        }

        return 0;
    });
}


function getFilteredAutomationTasks() {
    const searchTerm =
        getTableSearchInputValue(
            "automationTasksSearchInput"
        );

    const filteredTasks =
        filterTableItems(
            automationTasks,
            searchTerm,
            getAutomationTaskSearchableText
        );

    return getSortedAutomationTasks(
        filteredTasks
    );
}


function renderAutomationTaskRow(task) {
    const status =
        normalizeAutomationTaskStatus(
            task.status
        );

    const detailsPath =
        getAutomationTaskDetailsPath(
            task.id
        );

    return `
        <tr>
            <td>
                <span class="automation-tasks-status ${escapeAutomationTaskValue(status)}">
                    ${escapeAutomationTaskValue(status)}
                </span>
            </td>

            <td>
                <div class="automation-tasks-name-cell">
                    <span class="automation-tasks-name">
                        ${escapeAutomationTaskValue(task.name)}
                    </span>

                    <span class="automation-tasks-id" title="${escapeAutomationTaskValue(task.id)}">
                        ${escapeAutomationTaskValue(task.id)}
                    </span>
                </div>
            </td>

            <td>
                ${escapeAutomationTaskValue(task.category)}
            </td>

            <td>
                <a class="shared-button secondary automation-tasks-details-link" href="${escapeAutomationTaskValue(detailsPath)}">
                    Details
                </a>
            </td>
        </tr>
    `;
}


function updateAutomationTasksCounts(filteredTasks) {
    const totalCountElement =
        document.getElementById(
            "automationTasksCount"
        );

    const filteredCountElement =
        document.getElementById(
            "automationTasksFilteredCount"
        );

    if (totalCountElement) {
        totalCountElement.textContent =
            `${automationTasks.length} task${automationTasks.length === 1 ? "" : "s"}`;
    }

    if (filteredCountElement) {
        filteredCountElement.textContent =
            `${filteredTasks.length} shown`;
    }
}


function updateAutomationTasksSortIndicators() {
    document
        .querySelectorAll(".automation-tasks-table .shared-table-sort-button")
        .forEach((button) => {
            const isActive =
                button.dataset.sortKey === automationTasksSortKey;

            button.dataset.sortDirection =
                isActive
                    ? automationTasksSortDirection
                    : "";

            button.classList.toggle(
                "sorted-asc",
                isActive && automationTasksSortDirection === "asc"
            );

            button.classList.toggle(
                "sorted-desc",
                isActive && automationTasksSortDirection === "desc"
            );
        });
}


function renderAutomationTasks() {
    const tableBody =
        getAutomationTasksTableBody();

    if (!tableBody) {
        return;
    }

    if (!Array.isArray(automationTasks) || automationTasks.length === 0) {
        updateAutomationTasksCounts([]);
        renderAutomationTasksPlaceholder(
            AUTOMATION_TASKS_EMPTY_MESSAGE
        );
        return;
    }

    const filteredTasks =
        getFilteredAutomationTasks();

    updateAutomationTasksCounts(
        filteredTasks
    );

    if (filteredTasks.length === 0) {
        renderAutomationTasksPlaceholder(
            "No automation tasks match the current search."
        );
        updateTablePaginationControls({
            items: filteredTasks,
            rowsPerPage: AUTOMATION_TASKS_ROWS_PER_PAGE,
            currentPage: 1,
            previousButtonId: "automationTasksPreviousPageButton",
            nextButtonId: "automationTasksNextPageButton",
            statusElementId: "automationTasksPaginationStatus"
        });
        return;
    }

    const totalPages =
        getTableTotalPages(
            filteredTasks,
            AUTOMATION_TASKS_ROWS_PER_PAGE
        );

    automationTasksCurrentPage =
        clampTablePage(
            automationTasksCurrentPage,
            totalPages
        );

    const pagedTasks =
        getPagedTableItems(
            filteredTasks,
            automationTasksCurrentPage,
            AUTOMATION_TASKS_ROWS_PER_PAGE
        );

    tableBody.innerHTML =
        pagedTasks
            .map(renderAutomationTaskRow)
            .join("");

    automationTasksCurrentPage =
        updateTablePaginationControls({
            items: filteredTasks,
            rowsPerPage: AUTOMATION_TASKS_ROWS_PER_PAGE,
            currentPage: automationTasksCurrentPage,
            previousButtonId: "automationTasksPreviousPageButton",
            nextButtonId: "automationTasksNextPageButton",
            statusElementId: "automationTasksPaginationStatus"
        });

    updateAutomationTasksSortIndicators();
}


function parseAutomationTasksResponse(responseData) {
    if (!responseData || !Array.isArray(responseData.tasks)) {
        throw new Error(
            "The backend did not return an automation task list."
        );
    }

    return responseData.tasks;
}


async function loadAutomationTasks() {
    hideAutomationTasksMessage();

    automationTasks = [];
    automationTasksCurrentPage = 1;

    renderAutomationTasksPlaceholder(
        AUTOMATION_TASKS_LOADING_MESSAGE
    );

    try {
        const responseData =
            await getJson(
                CCORE_API_ENDPOINTS.automation.tasks.list
            );

        automationTasks =
            parseAutomationTasksResponse(
                responseData
            );

        enableTableSearchInput(
            "automationTasksSearchInput"
        );

        renderAutomationTasks();

        if (automationTasks.length === 0) {
            showAutomationTasksMessage(
                AUTOMATION_TASKS_EMPTY_MESSAGE,
                "info"
            );
        }

    } catch (error) {
        console.error(
            "Failed to load automation tasks:",
            error
        );

        renderAutomationTasksPlaceholder(
            AUTOMATION_TASKS_ERROR_MESSAGE
        );

        showAutomationTasksMessage(
            error.message || AUTOMATION_TASKS_ERROR_MESSAGE,
            "error"
        );
    }
}


function setupAutomationTasksEvents() {
    const backToAutomationButton =
        document.getElementById(
            "backToAutomationButton"
        );

    if (backToAutomationButton) {
        backToAutomationButton.href =
            LLA_PATHS.desktop.protected.automation.home;
    }

    const pipelinesLink =
        document.getElementById(
            "automationPipelinesLink"
        );

    if (pipelinesLink) {
        pipelinesLink.href =
            LLA_PATHS.desktop.protected.automation.pipelines;
    }

    const refreshButton =
        document.getElementById(
            "refreshAutomationTasksButton"
        );

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            () => {
                loadAutomationTasks();
            }
        );
    }

    const searchInput =
        document.getElementById(
            "automationTasksSearchInput"
        );

    if (searchInput) {
        searchInput.addEventListener(
            "input",
            () => {
                automationTasksCurrentPage = 1;
                renderAutomationTasks();
            }
        );
    }

    const previousButton =
        document.getElementById(
            "automationTasksPreviousPageButton"
        );

    if (previousButton) {
        previousButton.addEventListener(
            "click",
            () => {
                automationTasksCurrentPage -= 1;
                renderAutomationTasks();
            }
        );
    }

    const nextButton =
        document.getElementById(
            "automationTasksNextPageButton"
        );

    if (nextButton) {
        nextButton.addEventListener(
            "click",
            () => {
                automationTasksCurrentPage += 1;
                renderAutomationTasks();
            }
        );
    }

    document
        .querySelectorAll(".automation-tasks-table .shared-table-sort-button")
        .forEach((button) => {
            button.addEventListener(
                "click",
                () => {
                    const selectedSortKey =
                        button.dataset.sortKey;

                    if (!selectedSortKey) {
                        return;
                    }

                    if (automationTasksSortKey === selectedSortKey) {
                        automationTasksSortDirection =
                            automationTasksSortDirection === "asc"
                                ? "desc"
                                : "asc";
                    } else {
                        automationTasksSortKey =
                            selectedSortKey;
                        automationTasksSortDirection =
                            "asc";
                    }

                    automationTasksCurrentPage = 1;
                    renderAutomationTasks();
                }
            );
        });
}


function initializeAutomationTasksPage() {
    setupAutomationTasksEvents();
    loadAutomationTasks();
}


initializeAutomationTasksPage();

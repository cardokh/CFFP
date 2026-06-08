const LEARNING_ITEMS_MESSAGE_ID = "learningItemsMessage";
const LEARNING_ITEMS_TABLE_BODY_ID = "learningItemsTableBody";
const LEARNING_ITEMS_SEARCH_INPUT_ID = "learningItemsSearchInput";

const LEARNING_ITEMS_PREVIOUS_PAGE_BUTTON_ID =
    "learningItemsPreviousPageButton";

const LEARNING_ITEMS_PAGINATION_STATUS_ID =
    "learningItemsPaginationStatus";

const LEARNING_ITEMS_NEXT_PAGE_BUTTON_ID =
    "learningItemsNextPageButton";

const ADMIN_TABLE_ROWS_PER_PAGE_STORAGE_KEY =
    "adminTableRowsPerPage";

const DEFAULT_ADMIN_TABLE_ROWS_PER_PAGE =
    10;

const ALLOWED_ADMIN_TABLE_ROWS_PER_PAGE_VALUES =
    [10, 25, 50];

let allLearningItems =
    [];

let currentLearningItemsPage =
    1;

function navigateToLearningItemEdit(learningItemId) {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.learningItems.edit(learningItemId);
}

function navigateToCreateLearningItem() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.learningItems.create;
}

function navigateToAdminDashboard() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.dashboard;
}

function handleLearningItemRowClick(event) {
    const row =
        event.target.closest("tr[data-learning-item-id]");

    if (!row) {
        return;
    }

    const learningItemId =
        row.dataset.learningItemId;

    if (!learningItemId) {
        showErrorMessage(
            LEARNING_ITEMS_MESSAGE_ID,
            "Learning item ID is missing."
        );

        return;
    }

    navigateToLearningItemEdit(learningItemId);
}

function formatBoolean(value) {
    return value ? "Yes" : "No";
}

function getAdminTableRowsPerPage() {
    const savedRowsPerPage =
        Number(
            localStorage.getItem(
                ADMIN_TABLE_ROWS_PER_PAGE_STORAGE_KEY
            )
        );

    if (
        ALLOWED_ADMIN_TABLE_ROWS_PER_PAGE_VALUES.includes(
            savedRowsPerPage
        )
    ) {
        return savedRowsPerPage;
    }

    return DEFAULT_ADMIN_TABLE_ROWS_PER_PAGE;
}

function getLearningItemId(learningItem) {
    return learningItem.itemId;
}

function getLearningItemSourceText(learningItem) {
    return learningItem.sourceText || "";
}

function getLearningItemEnglishTranslation(learningItem) {
    return learningItem.englishTranslation || "";
}

function getLearningItemType(learningItem) {
    return learningItem.itemType || "";
}

function getLearningItemIsActive(learningItem) {
    return Boolean(learningItem.isActive);
}

function getSearchInputValue() {
    return document
        .getElementById(LEARNING_ITEMS_SEARCH_INPUT_ID)
        .value;
}

function getSearchableLearningItemText(learningItem) {
    return [
        getLearningItemId(learningItem),
        getLearningItemSourceText(learningItem),
        getLearningItemEnglishTranslation(learningItem),
        getLearningItemType(learningItem),
        formatBoolean(getLearningItemIsActive(learningItem))
    ]
        .join(" ")
        .toLowerCase();
}

function filterLearningItems(searchTerm) {
    const normalizedSearchTerm =
        searchTerm.trim().toLowerCase();

    if (!normalizedSearchTerm) {
        return allLearningItems;
    }

    return allLearningItems.filter((learningItem) =>
        getSearchableLearningItemText(learningItem).includes(
            normalizedSearchTerm
        )
    );
}

function getTotalLearningItemPages(learningItems) {
    const rowsPerPage =
        getAdminTableRowsPerPage();

    return Math.max(
        1,
        Math.ceil(learningItems.length / rowsPerPage)
    );
}

function getPagedLearningItems(learningItems) {
    const rowsPerPage =
        getAdminTableRowsPerPage();

    const startIndex =
        (currentLearningItemsPage - 1) * rowsPerPage;

    const endIndex =
        startIndex + rowsPerPage;

    return learningItems.slice(startIndex, endIndex);
}

function updateLearningItemsPaginationControls(filteredLearningItems) {
    const totalPages =
        getTotalLearningItemPages(filteredLearningItems);

    if (currentLearningItemsPage > totalPages) {
        currentLearningItemsPage =
            totalPages;
    }

    document
        .getElementById(LEARNING_ITEMS_PAGINATION_STATUS_ID)
        .textContent =
        `Page ${currentLearningItemsPage} of ${totalPages}`;

    setElementDisabled(
        LEARNING_ITEMS_PREVIOUS_PAGE_BUTTON_ID,
        currentLearningItemsPage <= 1
    );

    setElementDisabled(
        LEARNING_ITEMS_NEXT_PAGE_BUTTON_ID,
        currentLearningItemsPage >= totalPages
    );
}

function renderLearningItemsTable(learningItems) {
    const tableBody =
        document.getElementById(LEARNING_ITEMS_TABLE_BODY_ID);

    tableBody.innerHTML = learningItems.map((learningItem) => `
        <tr data-learning-item-id="${escapeHtml(getLearningItemId(learningItem))}">
            <td>${escapeHtml(getLearningItemId(learningItem))}</td>

            <td>
                ${escapeHtml(getLearningItemSourceText(learningItem))}
            </td>

            <td>
                ${escapeHtml(getLearningItemEnglishTranslation(learningItem))}
            </td>

            <td>
                ${escapeHtml(getLearningItemType(learningItem))}
            </td>

            <td>
                ${escapeHtml(formatBoolean(getLearningItemIsActive(learningItem)))}
            </td>
        </tr>
    `).join("");

    initializeTableSorting();
}

function renderTableMessage(message) {
    const tableBody =
        document.getElementById(LEARNING_ITEMS_TABLE_BODY_ID);

    tableBody.innerHTML = `
        <tr>
            <td colspan="5">
                ${escapeHtml(message)}
            </td>
        </tr>
    `;
}

function renderEmptyLearningItemsState() {
    renderTableMessage("No learning items found.");
}

function renderEmptySearchState() {
    renderTableMessage("No matching learning items found.");
}

function renderLearningItemsLoadError() {
    renderTableMessage("Failed to load learning items.");
}

function renderLearningItemsForCurrentState() {
    const filteredLearningItems =
        filterLearningItems(getSearchInputValue());

    if (filteredLearningItems.length === 0) {
        renderEmptySearchState();
        updateLearningItemsPaginationControls(filteredLearningItems);
        return;
    }

    updateLearningItemsPaginationControls(filteredLearningItems);

    renderLearningItemsTable(
        getPagedLearningItems(filteredLearningItems)
    );
}

function handleSearchInput() {
    hideMessage(LEARNING_ITEMS_MESSAGE_ID);

    currentLearningItemsPage =
        1;

    renderLearningItemsForCurrentState();
}

function handlePreviousPageClick() {
    if (currentLearningItemsPage <= 1) {
        return;
    }

    currentLearningItemsPage -=
        1;

    renderLearningItemsForCurrentState();
}

function handleNextPageClick() {
    const filteredLearningItems =
        filterLearningItems(getSearchInputValue());

    const totalPages =
        getTotalLearningItemPages(filteredLearningItems);

    if (currentLearningItemsPage >= totalPages) {
        return;
    }

    currentLearningItemsPage +=
        1;

    renderLearningItemsForCurrentState();
}

function enableLearningItemsSearch() {
    setElementDisabled(
        LEARNING_ITEMS_SEARCH_INPUT_ID,
        false
    );
}

async function loadLearningItems() {
    hideMessage(LEARNING_ITEMS_MESSAGE_ID);

    try {
        const data =
            await getJson(
                LLA_API_ENDPOINTS.admin.learningItems.list
            );

        const learningItems =
            data.learningItems;

        if (!learningItems || learningItems.length === 0) {
            allLearningItems =
                [];

            renderEmptyLearningItemsState();
            updateLearningItemsPaginationControls(allLearningItems);
            enableLearningItemsSearch();

            return;
        }

        allLearningItems =
            learningItems;

        currentLearningItemsPage =
            1;

        renderLearningItemsForCurrentState();
        enableLearningItemsSearch();

    } catch (error) {
        console.error(error);

        renderLearningItemsLoadError();

        showErrorMessage(
            LEARNING_ITEMS_MESSAGE_ID,
            error.message || "Failed to load learning items."
        );
    }
}

document
    .getElementById(LEARNING_ITEMS_TABLE_BODY_ID)
    .addEventListener("click", handleLearningItemRowClick);

document
    .getElementById("backToAdminButton")
    .addEventListener("click", navigateToAdminDashboard);

document
    .getElementById("addLearningItemButton")
    .addEventListener("click", navigateToCreateLearningItem);

document
    .getElementById(LEARNING_ITEMS_SEARCH_INPUT_ID)
    .addEventListener("input", handleSearchInput);

document
    .getElementById(LEARNING_ITEMS_PREVIOUS_PAGE_BUTTON_ID)
    .addEventListener("click", handlePreviousPageClick);

document
    .getElementById(LEARNING_ITEMS_NEXT_PAGE_BUTTON_ID)
    .addEventListener("click", handleNextPageClick);

loadLearningItems();
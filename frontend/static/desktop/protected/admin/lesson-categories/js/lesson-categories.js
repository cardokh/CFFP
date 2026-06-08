const LESSON_CATEGORIES_MESSAGE_ID = "lessonCategoriesMessage";
const LESSON_CATEGORIES_TABLE_BODY_ID = "lessonCategoriesTableBody";
const LESSON_CATEGORIES_SEARCH_INPUT_ID = "lessonCategoriesSearchInput";

const LESSON_CATEGORIES_PREVIOUS_PAGE_BUTTON_ID =
    "lessonCategoriesPreviousPageButton";

const LESSON_CATEGORIES_PAGINATION_STATUS_ID =
    "lessonCategoriesPaginationStatus";

const LESSON_CATEGORIES_NEXT_PAGE_BUTTON_ID =
    "lessonCategoriesNextPageButton";

const ADMIN_TABLE_ROWS_PER_PAGE_STORAGE_KEY =
    "adminTableRowsPerPage";

const DEFAULT_ADMIN_TABLE_ROWS_PER_PAGE =
    10;

const ALLOWED_ADMIN_TABLE_ROWS_PER_PAGE_VALUES =
    [10, 25, 50];

let allLessonCategories =
    [];

let currentLessonCategoriesPage =
    1;

function navigateToLessonCategoryEdit(categoryId) {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.lessonCategories.edit(categoryId);
}

function navigateToCreateLessonCategory() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.lessonCategories.create;
}

function navigateToAdminDashboard() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.dashboard;
}

function handleLessonCategoryRowClick(event) {
    const row =
        event.target.closest("tr[data-category-id]");

    if (!row) {
        return;
    }

    const categoryId =
        row.dataset.categoryId;

    if (!categoryId) {
        showErrorMessage(
            LESSON_CATEGORIES_MESSAGE_ID,
            "Category ID is missing."
        );

        return;
    }

    navigateToLessonCategoryEdit(categoryId);
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

function getLessonCategoryId(lessonCategory) {
    return lessonCategory.categoryId;
}

function getLessonCategoryName(lessonCategory) {
    return lessonCategory.name || "";
}

function getLessonCategoryDescription(lessonCategory) {
    return lessonCategory.description || "";
}

function getLessonCategoryIsActive(lessonCategory) {
    return Boolean(lessonCategory.isActive);
}

function getSearchInputValue() {
    return document
        .getElementById(LESSON_CATEGORIES_SEARCH_INPUT_ID)
        .value;
}

function getSearchableLessonCategoryText(lessonCategory) {
    return [
        getLessonCategoryId(lessonCategory),
        getLessonCategoryName(lessonCategory),
        getLessonCategoryDescription(lessonCategory),
        formatBoolean(getLessonCategoryIsActive(lessonCategory))
    ]
        .join(" ")
        .toLowerCase();
}

function filterLessonCategories(searchTerm) {
    const normalizedSearchTerm =
        searchTerm.trim().toLowerCase();

    if (!normalizedSearchTerm) {
        return allLessonCategories;
    }

    return allLessonCategories.filter((lessonCategory) =>
        getSearchableLessonCategoryText(lessonCategory).includes(
            normalizedSearchTerm
        )
    );
}

function getTotalLessonCategoryPages(lessonCategories) {
    const rowsPerPage =
        getAdminTableRowsPerPage();

    return Math.max(
        1,
        Math.ceil(lessonCategories.length / rowsPerPage)
    );
}

function getPagedLessonCategories(lessonCategories) {
    const rowsPerPage =
        getAdminTableRowsPerPage();

    const startIndex =
        (currentLessonCategoriesPage - 1) * rowsPerPage;

    const endIndex =
        startIndex + rowsPerPage;

    return lessonCategories.slice(startIndex, endIndex);
}

function updateLessonCategoriesPaginationControls(filteredLessonCategories) {
    const totalPages =
        getTotalLessonCategoryPages(filteredLessonCategories);

    if (currentLessonCategoriesPage > totalPages) {
        currentLessonCategoriesPage =
            totalPages;
    }

    document
        .getElementById(LESSON_CATEGORIES_PAGINATION_STATUS_ID)
        .textContent =
        `Page ${currentLessonCategoriesPage} of ${totalPages}`;

    setElementDisabled(
        LESSON_CATEGORIES_PREVIOUS_PAGE_BUTTON_ID,
        currentLessonCategoriesPage <= 1
    );

    setElementDisabled(
        LESSON_CATEGORIES_NEXT_PAGE_BUTTON_ID,
        currentLessonCategoriesPage >= totalPages
    );
}

function renderLessonCategoriesTable(lessonCategories) {
    const tableBody =
        document.getElementById(LESSON_CATEGORIES_TABLE_BODY_ID);

    tableBody.innerHTML = lessonCategories.map((lessonCategory) => `
        <tr data-category-id="${escapeHtml(getLessonCategoryId(lessonCategory))}">
            <td>${escapeHtml(getLessonCategoryId(lessonCategory))}</td>

            <td>
                ${escapeHtml(getLessonCategoryName(lessonCategory))}
            </td>

            <td>
                ${escapeHtml(getLessonCategoryDescription(lessonCategory))}
            </td>

            <td>
                ${escapeHtml(formatBoolean(getLessonCategoryIsActive(lessonCategory)))}
            </td>
        </tr>
    `).join("");
}

function renderTableMessage(message) {
    const tableBody =
        document.getElementById(LESSON_CATEGORIES_TABLE_BODY_ID);

    tableBody.innerHTML = `
        <tr>
            <td colspan="4">
                ${escapeHtml(message)}
            </td>
        </tr>
    `;
}

function renderEmptyLessonCategoriesState() {
    renderTableMessage("No lesson categories found.");
}

function renderEmptySearchState() {
    renderTableMessage("No matching lesson categories found.");
}

function renderLessonCategoriesLoadError() {
    renderTableMessage("Failed to load lesson categories.");
}

function renderLessonCategoriesForCurrentState() {
    const filteredLessonCategories =
        filterLessonCategories(getSearchInputValue());

    if (filteredLessonCategories.length === 0) {
        renderEmptySearchState();
        updateLessonCategoriesPaginationControls(filteredLessonCategories);
        return;
    }

    updateLessonCategoriesPaginationControls(filteredLessonCategories);

    renderLessonCategoriesTable(
        getPagedLessonCategories(filteredLessonCategories)
    );

    initializeTableSorting();
}

function handleSearchInput() {
    hideMessage(LESSON_CATEGORIES_MESSAGE_ID);

    currentLessonCategoriesPage =
        1;

    renderLessonCategoriesForCurrentState();
}

function handlePreviousPageClick() {
    if (currentLessonCategoriesPage <= 1) {
        return;
    }

    currentLessonCategoriesPage -=
        1;

    renderLessonCategoriesForCurrentState();
}

function handleNextPageClick() {
    const filteredLessonCategories =
        filterLessonCategories(getSearchInputValue());

    const totalPages =
        getTotalLessonCategoryPages(filteredLessonCategories);

    if (currentLessonCategoriesPage >= totalPages) {
        return;
    }

    currentLessonCategoriesPage +=
        1;

    renderLessonCategoriesForCurrentState();
}

function enableLessonCategoriesSearch() {
    setElementDisabled(
        LESSON_CATEGORIES_SEARCH_INPUT_ID,
        false
    );
}

async function loadLessonCategories() {
    hideMessage(LESSON_CATEGORIES_MESSAGE_ID);

    try {
        const data =
            await getJson(
                LLA_API_ENDPOINTS.admin.lessonCategories.list
            );

        const lessonCategories =
            data.lessonCategories;

        if (!lessonCategories || lessonCategories.length === 0) {
            allLessonCategories =
                [];

            renderEmptyLessonCategoriesState();
            updateLessonCategoriesPaginationControls(allLessonCategories);
            enableLessonCategoriesSearch();

            return;
        }

        allLessonCategories =
            lessonCategories;

        currentLessonCategoriesPage =
            1;

        renderLessonCategoriesForCurrentState();
        enableLessonCategoriesSearch();

    } catch (error) {
        console.error(error);

        renderLessonCategoriesLoadError();

        showErrorMessage(
            LESSON_CATEGORIES_MESSAGE_ID,
            error.message || "Failed to load lesson categories."
        );
    }
}

document
    .getElementById(LESSON_CATEGORIES_TABLE_BODY_ID)
    .addEventListener("click", handleLessonCategoryRowClick);

document
    .getElementById("backToAdminButton")
    .addEventListener("click", navigateToAdminDashboard);

document
    .getElementById("addLessonCategoryButton")
    .addEventListener("click", navigateToCreateLessonCategory);

document
    .getElementById(LESSON_CATEGORIES_SEARCH_INPUT_ID)
    .addEventListener("input", handleSearchInput);

document
    .getElementById(LESSON_CATEGORIES_PREVIOUS_PAGE_BUTTON_ID)
    .addEventListener("click", handlePreviousPageClick);

document
    .getElementById(LESSON_CATEGORIES_NEXT_PAGE_BUTTON_ID)
    .addEventListener("click", handleNextPageClick);

loadLessonCategories();
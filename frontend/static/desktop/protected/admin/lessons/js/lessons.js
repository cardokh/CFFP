const LESSONS_MESSAGE_ID = "lessonsMessage";
const LESSONS_TABLE_BODY_ID = "lessonsTableBody";
const LESSONS_SEARCH_INPUT_ID = "lessonsSearchInput";

const LESSONS_PREVIOUS_PAGE_BUTTON_ID =
    "lessonsPreviousPageButton";

const LESSONS_PAGINATION_STATUS_ID =
    "lessonsPaginationStatus";

const LESSONS_NEXT_PAGE_BUTTON_ID =
    "lessonsNextPageButton";

const ADMIN_TABLE_ROWS_PER_PAGE_STORAGE_KEY =
    "adminTableRowsPerPage";

const DEFAULT_ADMIN_TABLE_ROWS_PER_PAGE =
    10;

const ALLOWED_ADMIN_TABLE_ROWS_PER_PAGE_VALUES =
    [10, 25, 50];

let allLessons = [];

let lessonFormOptions = {
    lesson_categories: [],
    lesson_types: [],
    embodiment_types: [],
    interaction_styles: []
};

let currentLessonsPage = 1;


function navigateToLessonEdit(lessonId) {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.lessons.edit(lessonId);
}

function navigateToCreateLesson() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.lessons.create;
}


function navigateToAdminDashboard() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.dashboard;
}


function handleLessonRowClick(event) {
    const row =
        event.target.closest("tr[data-lesson-id]");

    if (!row) {
        return;
    }

    const lessonId =
        row.dataset.lessonId;

    if (!lessonId) {
        showErrorMessage(
            LESSONS_MESSAGE_ID,
            "Lesson ID is missing."
        );

        return;
    }

    navigateToLessonEdit(lessonId);
}


function formatBoolean(value) {
    return value ? "Yes" : "No";
}


function findLookupName(items, id) {
    if (!Array.isArray(items)) {
        return "";
    }

    const matchingItem =
        items.find((item) =>
            Number(item.id) === Number(id)
        );

    return matchingItem ? matchingItem.name || "" : "";
}


function getLessonCategoryName(lesson) {
    return findLookupName(
        lessonFormOptions.lesson_categories,
        lesson.categoryId
    );
}


function getLessonTypeName(lesson) {
    return findLookupName(
        lessonFormOptions.lesson_types,
        lesson.lessonTypeId
    );
}


function getLessonEmbodimentName(lesson) {
    return findLookupName(
        lessonFormOptions.embodiment_types,
        lesson.embodimentTypeId
    );
}


function getLessonInteractionStyleName(lesson) {
    return findLookupName(
        lessonFormOptions.interaction_styles,
        lesson.interactionStyleId
    );
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


function getSearchInputValue() {
    return getTableSearchInputValue(
        LESSONS_SEARCH_INPUT_ID
    );
}


function getSearchableLessonText(lesson) {
    return [
        lesson.lessonId,
        lesson.title,
        getLessonCategoryName(lesson),
        getLessonTypeName(lesson),
        getLessonEmbodimentName(lesson),
        getLessonInteractionStyleName(lesson),
        formatBoolean(lesson.isActive)
    ]
        .join(" ")
        .toLowerCase();
}


function filterLessons(searchTerm) {
    return filterTableItems(
        allLessons,
        searchTerm,
        getSearchableLessonText
    );
}


function getTotalLessonPages(lessons) {
    return getTableTotalPages(
        lessons,
        getAdminTableRowsPerPage()
    );
}


function getPagedLessons(lessons) {
    return getPagedTableItems(
        lessons,
        currentLessonsPage,
        getAdminTableRowsPerPage()
    );
}


function updateLessonsPaginationControls(filteredLessons) {
    currentLessonsPage =
        updateTablePaginationControls({
            items: filteredLessons,
            currentPage: currentLessonsPage,
            rowsPerPage: getAdminTableRowsPerPage(),
            previousButtonId: LESSONS_PREVIOUS_PAGE_BUTTON_ID,
            nextButtonId: LESSONS_NEXT_PAGE_BUTTON_ID,
            statusElementId: LESSONS_PAGINATION_STATUS_ID
        });
}


function renderLessonsTable(lessons) {
    const tableBody =
        document.getElementById(LESSONS_TABLE_BODY_ID);

    tableBody.innerHTML =
        lessons.map((lesson) => `
            <tr data-lesson-id="${escapeHtml(lesson.lessonId)}">
                <td>${escapeHtml(lesson.lessonId)}</td>
                <td>${escapeHtml(lesson.title || "")}</td>
                <td>${escapeHtml(getLessonCategoryName(lesson))}</td>
                <td>${escapeHtml(getLessonTypeName(lesson))}</td>
                <td>${escapeHtml(getLessonEmbodimentName(lesson))}</td>
                <td>${escapeHtml(getLessonInteractionStyleName(lesson))}</td>
                <td>${escapeHtml(formatBoolean(lesson.isActive))}</td>
            </tr>
        `).join("");

    initializeTableSorting();
}


function renderTableMessage(message) {
    const tableBody =
        document.getElementById(LESSONS_TABLE_BODY_ID);

    tableBody.innerHTML = `
        <tr>
            <td colspan="7">
                ${escapeHtml(message)}
            </td>
        </tr>
    `;
}


function renderEmptyLessonsState() {
    renderTableMessage("No lessons found.");
}


function renderEmptySearchState() {
    renderTableMessage("No matching lessons found.");
}


function renderLessonsLoadError() {
    renderTableMessage("Failed to load lessons.");
}


function renderLessonsForCurrentState() {
    const filteredLessons =
        filterLessons(getSearchInputValue());

    if (filteredLessons.length === 0) {
        renderEmptySearchState();
        updateLessonsPaginationControls(filteredLessons);
        return;
    }

    updateLessonsPaginationControls(filteredLessons);

    renderLessonsTable(
        getPagedLessons(filteredLessons)
    );
}


function handleSearchInput() {
    hideMessage(LESSONS_MESSAGE_ID);

    currentLessonsPage = 1;

    renderLessonsForCurrentState();
}


function handlePreviousPageClick() {
    if (currentLessonsPage <= 1) {
        return;
    }

    currentLessonsPage -= 1;

    renderLessonsForCurrentState();
}


function handleNextPageClick() {
    const filteredLessons =
        filterLessons(getSearchInputValue());

    const totalPages =
        getTotalLessonPages(filteredLessons);

    if (currentLessonsPage >= totalPages) {
        return;
    }

    currentLessonsPage += 1;

    renderLessonsForCurrentState();
}


function enableLessonsSearch() {
    enableTableSearchInput(
        LESSONS_SEARCH_INPUT_ID
    );
}


async function loadLessonFormOptions() {
    const formOptionsData =
        await getJson(
            LLA_API_ENDPOINTS.admin.referenceData.lessonFormOptions
        );

    if (
        !formOptionsData.success ||
        !formOptionsData.form_options
    ) {
        throw new Error(
            "Failed to load lesson reference data."
        );
    }

    lessonFormOptions =
        formOptionsData.form_options;
}


async function loadLessonList() {
    const data =
        await getJson(
            LLA_API_ENDPOINTS.admin.lessons.list
        );

    if (!data.success || !Array.isArray(data.lessons)) {
        throw new Error(
            data.error || "Failed to load lessons."
        );
    }

    return data.lessons;
}


async function loadLessons() {
    hideMessage(LESSONS_MESSAGE_ID);

    try {
        await loadLessonFormOptions();

        allLessons =
            await loadLessonList();

        currentLessonsPage = 1;

        enableLessonsSearch();

        if (allLessons.length === 0) {
            renderEmptyLessonsState();
            updateLessonsPaginationControls(allLessons);
            return;
        }

        renderLessonsForCurrentState();

    } catch (error) {
        console.error(error);

        renderLessonsLoadError();

        showErrorMessage(
            LESSONS_MESSAGE_ID,
            error.message || "Failed to load lessons."
        );
    }
}


document
    .getElementById(LESSONS_TABLE_BODY_ID)
    .addEventListener("click", handleLessonRowClick);

document
    .getElementById("backToAdminButton")
    .addEventListener("click", navigateToAdminDashboard);

document
    .getElementById("addLessonButton")
    .addEventListener("click", navigateToCreateLesson);

document
    .getElementById(LESSONS_SEARCH_INPUT_ID)
    .addEventListener("input", handleSearchInput);

document
    .getElementById(LESSONS_PREVIOUS_PAGE_BUTTON_ID)
    .addEventListener("click", handlePreviousPageClick);

document
    .getElementById(LESSONS_NEXT_PAGE_BUTTON_ID)
    .addEventListener("click", handleNextPageClick);

loadLessons();
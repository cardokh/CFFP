const MY_LESSONS_TABLE_BODY_ID =
    "myLessonsTableBody";

const MY_LESSONS_SEARCH_INPUT_ID =
    "myLessonsSearchInput";

const MY_LESSONS_PREVIOUS_PAGE_BUTTON_ID =
    "myLessonsPreviousPageButton";

const MY_LESSONS_PAGINATION_STATUS_ID =
    "myLessonsPaginationStatus";

const MY_LESSONS_NEXT_PAGE_BUTTON_ID =
    "myLessonsNextPageButton";

const MY_LESSONS_ROWS_PER_PAGE =
    10;

let allLessons =
    [];

let currentMyLessonsPage =
    1;


function getAuthenticatedUserId() {
    const authenticatedUser =
        requireAuthentication();

    if (!authenticatedUser || !authenticatedUser.userId) {
        throw new Error("Authenticated user ID is missing.");
    }

    return authenticatedUser.userId;
}


function navigateToStudentLessonDetails(lessonId) {
    window.location.href =
        `/desktop/protected/student-lesson-details.html?lessonId=${lessonId}`;
}


function getLessonTitle(lesson) {
    return lesson.lessonTitle || "";
}


function getLessonCategoryName(lesson) {
    return lesson.categoryName || "-";
}


function getLessonTypeName(lesson) {
    return lesson.lessonTypeName || "-";
}


function getLessonEmbodimentTypeName(lesson) {
    return lesson.embodimentTypeName || "-";
}


function getLessonInteractionStyleName(lesson) {
    return lesson.interactionStyleName || "-";
}


function getLessonStatusName(lesson) {
    return lesson.lessonStatusName || "-";
}


function getSearchableLessonText(lesson) {
    return [
        getLessonTitle(lesson),
        getLessonCategoryName(lesson),
        getLessonTypeName(lesson),
        getLessonEmbodimentTypeName(lesson),
        getLessonInteractionStyleName(lesson),
        getLessonStatusName(lesson)
    ]
        .join(" ")
        .toLowerCase();
}


function getSearchInputValue() {
    return document
        .getElementById(MY_LESSONS_SEARCH_INPUT_ID)
        .value;
}


function getFilteredLessons() {
    return filterTableItems(
        allLessons,
        getSearchInputValue(),
        getSearchableLessonText
    );
}


function getTotalMyLessonsPages(lessons) {
    return Math.max(
        1,
        Math.ceil(lessons.length / MY_LESSONS_ROWS_PER_PAGE)
    );
}


function getPagedLessons(lessons) {
    const startIndex =
        (currentMyLessonsPage - 1) * MY_LESSONS_ROWS_PER_PAGE;

    const endIndex =
        startIndex + MY_LESSONS_ROWS_PER_PAGE;

    return lessons.slice(
        startIndex,
        endIndex
    );
}


function updateMyLessonsPaginationControls(filteredLessons) {
    const totalPages =
        getTotalMyLessonsPages(filteredLessons);

    if (currentMyLessonsPage > totalPages) {
        currentMyLessonsPage =
            totalPages;
    }

    document
        .getElementById(MY_LESSONS_PAGINATION_STATUS_ID)
        .textContent =
        `Page ${currentMyLessonsPage} of ${totalPages}`;

    setElementDisabled(
        MY_LESSONS_PREVIOUS_PAGE_BUTTON_ID,
        currentMyLessonsPage <= 1
    );

    setElementDisabled(
        MY_LESSONS_NEXT_PAGE_BUTTON_ID,
        currentMyLessonsPage >= totalPages
    );
}


function renderTableMessage(message) {
    const tableBody =
        document.getElementById(
            MY_LESSONS_TABLE_BODY_ID
        );

    tableBody.innerHTML = `
        <tr>
            <td colspan="6">
                ${escapeHtml(message)}
            </td>
        </tr>
    `;
}


function renderEmptyLessons() {
    renderTableMessage(
        "No lessons available."
    );
}


function renderEmptySearchState() {
    renderTableMessage(
        "No matching lessons found."
    );
}


function renderLessonRow(lesson) {
    return `
        <tr data-lesson-id="${escapeHtml(lesson.lessonId)}">

            <td>
                ${escapeHtml(
        getLessonTitle(lesson)
    )}
            </td>

            <td>
                ${escapeHtml(
        getLessonCategoryName(lesson)
    )}
            </td>

            <td>
                ${escapeHtml(
        getLessonTypeName(lesson)
    )}
            </td>

            <td>
                ${escapeHtml(
        getLessonEmbodimentTypeName(lesson)
    )}
            </td>

            <td>
                ${escapeHtml(
        getLessonInteractionStyleName(lesson)
    )}
            </td>

            <td>
                ${escapeHtml(
        getLessonStatusName(lesson)
    )}
            </td>

        </tr>
    `;
}


function renderLessons(lessons) {
    const tableBody =
        document.getElementById(
            MY_LESSONS_TABLE_BODY_ID
        );

    tableBody.innerHTML =
        lessons
            .map((lesson) =>
                renderLessonRow(lesson)
            )
            .join("");

    initializeTableSorting();
}


function renderLessonsForCurrentState() {
    const filteredLessons =
        getFilteredLessons();

    if (allLessons.length === 0) {
        renderEmptyLessons();
        updateMyLessonsPaginationControls(filteredLessons);
        return;
    }

    if (filteredLessons.length === 0) {
        renderEmptySearchState();
        updateMyLessonsPaginationControls(filteredLessons);
        return;
    }

    updateMyLessonsPaginationControls(filteredLessons);

    renderLessons(
        getPagedLessons(filteredLessons)
    );
}


function handleSearchInput() {
    currentMyLessonsPage =
        1;

    renderLessonsForCurrentState();
}


function handlePreviousPageClick() {
    if (currentMyLessonsPage <= 1) {
        return;
    }

    currentMyLessonsPage -=
        1;

    renderLessonsForCurrentState();
}


function handleNextPageClick() {
    const filteredLessons =
        getFilteredLessons();

    const totalPages =
        getTotalMyLessonsPages(filteredLessons);

    if (currentMyLessonsPage >= totalPages) {
        return;
    }

    currentMyLessonsPage +=
        1;

    renderLessonsForCurrentState();
}


function enableLessonsSearch() {
    enableTableSearchInput(
        MY_LESSONS_SEARCH_INPUT_ID
    );
}


async function loadLessonLibrary() {
    const userId =
        getAuthenticatedUserId();


    const data =
        await getJson(
            LLA_API_ENDPOINTS.student.lessons.byUserId(
                userId
            )
        );

    if (!data.success) {
        throw new Error(
            data.error || "Failed to load lessons."
        );
    }

    allLessons =
        data.userLessons || [];

    currentMyLessonsPage =
        1;

    renderLessonsForCurrentState();

    enableLessonsSearch();
}


function handleLessonsTableClick(event) {
    const row =
        event.target.closest("[data-lesson-id]");

    if (!row) {
        return;
    }

    const lessonId =
        Number(row.dataset.lessonId);

    navigateToStudentLessonDetails(lessonId);
}


async function initializeLessonLibraryPage() {
    try {
        await loadLessonLibrary();
    } catch (error) {
        console.error(error);

        renderTableMessage(
            error.message || "Failed to load lessons."
        );
    }
}


document
    .getElementById(MY_LESSONS_TABLE_BODY_ID)
    .addEventListener(
        "click",
        handleLessonsTableClick
    );


document
    .getElementById(MY_LESSONS_SEARCH_INPUT_ID)
    .addEventListener(
        "input",
        handleSearchInput
    );


document
    .getElementById(MY_LESSONS_PREVIOUS_PAGE_BUTTON_ID)
    .addEventListener(
        "click",
        handlePreviousPageClick
    );


document
    .getElementById(MY_LESSONS_NEXT_PAGE_BUTTON_ID)
    .addEventListener(
        "click",
        handleNextPageClick
    );


initializeLessonLibraryPage();
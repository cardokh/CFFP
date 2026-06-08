/*
 * Progress page controller.
 *
 * Responsibilities:
 * - Load student progress.
 * - Render summary.
 * - Render unified My Lessons table.
 */

const PROGRESS_TOTAL_LESSONS_ID =
    "progressTotalLessons";

const PROGRESS_COMPLETED_LESSONS_ID =
    "progressCompletedLessons";

const PROGRESS_IN_PROGRESS_LESSONS_ID =
    "progressInProgressLessons";

const PROGRESS_COMPLETION_PERCENTAGE_ID =
    "progressCompletionPercentage";

const PROGRESS_TABLE_BODY_ID =
    "progressLessonsTableBody";

const PROGRESS_SEARCH_INPUT_ID =
    "progressSearchInput";

const PROGRESS_PREVIOUS_PAGE_BUTTON_ID =
    "progressPreviousPageButton";

const PROGRESS_PAGINATION_STATUS_ID =
    "progressPaginationStatus";

const PROGRESS_NEXT_PAGE_BUTTON_ID =
    "progressNextPageButton";

const PROGRESS_ROWS_PER_PAGE =
    10;

let allLessons =
    [];

let currentPage =
    1;


function getAuthenticatedUserId() {
    const authenticatedUser =
        requireAuthentication();

    if (!authenticatedUser || !authenticatedUser.userId) {
        throw new Error(
            "Authenticated user ID is missing."
        );
    }

    return authenticatedUser.userId;
}


function setTextContent(elementId, value) {
    document
        .getElementById(elementId)
        .textContent =
        value;
}


function renderSummary(summary) {
    setTextContent(
        PROGRESS_TOTAL_LESSONS_ID,
        summary.totalLessons
    );

    setTextContent(
        PROGRESS_COMPLETED_LESSONS_ID,
        summary.completedLessons
    );

    setTextContent(
        PROGRESS_IN_PROGRESS_LESSONS_ID,
        summary.inProgressLessons
    );

    setTextContent(
        PROGRESS_COMPLETION_PERCENTAGE_ID,
        `${summary.completionPercentage}%`
    );
}


function getLessonTitle(lesson) {
    return lesson.lessonTitle || "-";
}


function getLessonStatus(lesson) {
    if (lesson.completedAt) {
        return "Completed";
    }

    return lesson.lessonStatusName || "Not Started";
}


function getLessonScore(lesson) {
    if (!lesson.completedAt) {
        return "-";
    }

    if (
        lesson.score === null ||
        lesson.score === undefined
    ) {
        return "-";
    }

    if (
        lesson.totalQuestions === null ||
        lesson.totalQuestions === undefined
    ) {
        return String(lesson.score);
    }

    return `${lesson.score} / ${lesson.totalQuestions}`;
}


function getCompletedDate(lesson) {
    return lesson.completedAt || "-";
}


function getSearchableLessonText(lesson) {
    return [
        getLessonTitle(lesson),
        getLessonStatus(lesson),
        getLessonScore(lesson),
        getCompletedDate(lesson)
    ]
        .join(" ")
        .toLowerCase();
}


function getSearchInputValue() {
    return document
        .getElementById(
            PROGRESS_SEARCH_INPUT_ID
        )
        .value;
}


function getFilteredLessons() {
    return filterTableItems(
        allLessons,
        getSearchInputValue(),
        getSearchableLessonText
    );
}


function getTotalPages(lessons) {
    return Math.max(
        1,
        Math.ceil(
            lessons.length /
            PROGRESS_ROWS_PER_PAGE
        )
    );
}


function getPagedLessons(lessons) {
    const startIndex =
        (currentPage - 1) *
        PROGRESS_ROWS_PER_PAGE;

    const endIndex =
        startIndex +
        PROGRESS_ROWS_PER_PAGE;

    return lessons.slice(
        startIndex,
        endIndex
    );
}


function updatePaginationControls(
    filteredLessons
) {
    const totalPages =
        getTotalPages(
            filteredLessons
        );

    if (currentPage > totalPages) {
        currentPage =
            totalPages;
    }

    document
        .getElementById(
            PROGRESS_PAGINATION_STATUS_ID
        )
        .textContent =
        `Page ${currentPage} of ${totalPages}`;

    setElementDisabled(
        PROGRESS_PREVIOUS_PAGE_BUTTON_ID,
        currentPage <= 1
    );

    setElementDisabled(
        PROGRESS_NEXT_PAGE_BUTTON_ID,
        currentPage >= totalPages
    );
}


function renderTableMessage(message) {
    const tableBody =
        document.getElementById(
            PROGRESS_TABLE_BODY_ID
        );

    tableBody.innerHTML =
        `
        <tr>
            <td colspan="4">
                ${escapeHtml(message)}
            </td>
        </tr>
    `;
}


function renderLessonRow(lesson) {
    return `
        <tr data-lesson-id="${escapeHtml(
        lesson.lessonId
    )}">

            <td>
                ${escapeHtml(
        getLessonTitle(lesson)
    )}
            </td>

            <td>
                ${escapeHtml(
        getLessonStatus(lesson)
    )}
            </td>

            <td>
                ${escapeHtml(
        getLessonScore(lesson)
    )}
            </td>

            <td>
                ${escapeHtml(
        getCompletedDate(lesson)
    )}
            </td>

        </tr>
    `;
}


function renderLessons(lessons) {
    const tableBody =
        document.getElementById(
            PROGRESS_TABLE_BODY_ID
        );

    tableBody.innerHTML =
        lessons
            .map(renderLessonRow)
            .join("");

    initializeTableSorting();
}


function renderCurrentState() {
    const filteredLessons =
        getFilteredLessons();

    if (allLessons.length === 0) {
        renderTableMessage(
            "No lessons available."
        );

        updatePaginationControls(
            filteredLessons
        );

        return;
    }

    if (filteredLessons.length === 0) {
        renderTableMessage(
            "No matching lessons found."
        );

        updatePaginationControls(
            filteredLessons
        );

        return;
    }

    updatePaginationControls(
        filteredLessons
    );

    renderLessons(
        getPagedLessons(
            filteredLessons
        )
    );
}


function handleSearchInput() {
    currentPage =
        1;

    renderCurrentState();
}


function handlePreviousPageClick() {
    if (currentPage <= 1) {
        return;
    }

    currentPage--;

    renderCurrentState();
}


function handleNextPageClick() {
    const filteredLessons =
        getFilteredLessons();

    const totalPages =
        getTotalPages(
            filteredLessons
        );

    if (currentPage >= totalPages) {
        return;
    }

    currentPage++;

    renderCurrentState();
}


function enableSearch() {
    enableTableSearchInput(
        PROGRESS_SEARCH_INPUT_ID
    );
}


function navigateToStudentLessonDetails(
    lessonId
) {
    window.location.href =
        `/desktop/protected/student-lesson-details.html?lessonId=${lessonId}`;
}


function handleTableClick(event) {
    const row =
        event.target.closest(
            "[data-lesson-id]"
        );

    if (!row) {
        return;
    }

    const lessonId =
        Number(
            row.dataset.lessonId
        );

    navigateToStudentLessonDetails(
        lessonId
    );
}


async function loadStudentProgress() {
    const userId =
        getAuthenticatedUserId();

    const data =
        await getJson(
            LLA_API_ENDPOINTS.student.progress.byUserId(
                userId
            )
        );

    if (!data.success) {
        throw new Error(
            data.error ||
            "Failed to load progress."
        );
    }

    const progress =
        data.progress;

    renderSummary(
        progress.summary
    );

    allLessons = [
        ...(progress.continueLessons || []),
        ...(progress.completedLessons || [])
    ];

    currentPage =
        1;

    renderCurrentState();

    enableSearch();
}


async function initializeProgressPage() {
    try {
        await loadStudentProgress();
    }
    catch (error) {
        console.error(error);

        renderTableMessage(
            error.message ||
            "Failed to load progress."
        );
    }
}


document
    .getElementById(
        PROGRESS_TABLE_BODY_ID
    )
    .addEventListener(
        "click",
        handleTableClick
    );

document
    .getElementById(
        PROGRESS_SEARCH_INPUT_ID
    )
    .addEventListener(
        "input",
        handleSearchInput
    );

document
    .getElementById(
        PROGRESS_PREVIOUS_PAGE_BUTTON_ID
    )
    .addEventListener(
        "click",
        handlePreviousPageClick
    );

document
    .getElementById(
        PROGRESS_NEXT_PAGE_BUTTON_ID
    )
    .addEventListener(
        "click",
        handleNextPageClick
    );

initializeProgressPage();
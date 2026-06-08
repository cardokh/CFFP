const QUIZ_QUESTIONS_MESSAGE_ID = "quizQuestionsMessage";
const QUIZ_QUESTIONS_TABLE_BODY_ID = "quizQuestionsTableBody";
const QUIZ_QUESTIONS_SEARCH_INPUT_ID = "quizQuestionsSearchInput";

const QUIZ_QUESTIONS_PREVIOUS_PAGE_BUTTON_ID =
    "quizQuestionsPreviousPageButton";

const QUIZ_QUESTIONS_PAGINATION_STATUS_ID =
    "quizQuestionsPaginationStatus";

const QUIZ_QUESTIONS_NEXT_PAGE_BUTTON_ID =
    "quizQuestionsNextPageButton";

const ADMIN_TABLE_ROWS_PER_PAGE_STORAGE_KEY =
    "adminTableRowsPerPage";

const DEFAULT_ADMIN_TABLE_ROWS_PER_PAGE =
    10;

const ALLOWED_ADMIN_TABLE_ROWS_PER_PAGE_VALUES =
    [10, 25, 50];

let allQuizQuestions =
    [];

let currentQuizQuestionsPage =
    1;

function navigateToQuizQuestionEdit(questionId) {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.quizQuestions.edit(questionId);
}

function navigateToCreateQuizQuestion() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.quizQuestions.create;
}

function navigateToAdminDashboard() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.dashboard;
}

function handleQuizQuestionRowClick(event) {
    const row =
        event.target.closest("tr[data-quiz-question-id]");

    if (!row) {
        return;
    }

    const questionId =
        row.dataset.quizQuestionId;

    if (!questionId) {
        showErrorMessage(
            QUIZ_QUESTIONS_MESSAGE_ID,
            "Quiz question ID is missing."
        );

        return;
    }

    navigateToQuizQuestionEdit(questionId);
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

function getQuizQuestionId(quizQuestion) {
    return quizQuestion.questionId;
}

function getQuizQuestionText(quizQuestion) {
    return quizQuestion.questionText || "";
}

function getQuizQuestionCategoryName(quizQuestion) {
    return quizQuestion.categoryName || quizQuestion.categoryId || "";
}

function getQuizQuestionIsActive(quizQuestion) {
    return Boolean(quizQuestion.isActive);
}

function getSearchInputValue() {
    return document
        .getElementById(QUIZ_QUESTIONS_SEARCH_INPUT_ID)
        .value;
}

function getSearchableQuizQuestionText(quizQuestion) {
    return [
        getQuizQuestionId(quizQuestion),
        getQuizQuestionText(quizQuestion),
        getQuizQuestionCategoryName(quizQuestion),
        formatBoolean(getQuizQuestionIsActive(quizQuestion))
    ]
        .join(" ")
        .toLowerCase();
}

function filterQuizQuestions(searchTerm) {
    const normalizedSearchTerm =
        searchTerm.trim().toLowerCase();

    if (!normalizedSearchTerm) {
        return allQuizQuestions;
    }

    return allQuizQuestions.filter((quizQuestion) =>
        getSearchableQuizQuestionText(quizQuestion).includes(
            normalizedSearchTerm
        )
    );
}

function getTotalQuizQuestionPages(quizQuestions) {
    const rowsPerPage =
        getAdminTableRowsPerPage();

    return Math.max(
        1,
        Math.ceil(quizQuestions.length / rowsPerPage)
    );
}

function getPagedQuizQuestions(quizQuestions) {
    const rowsPerPage =
        getAdminTableRowsPerPage();

    const startIndex =
        (currentQuizQuestionsPage - 1) * rowsPerPage;

    const endIndex =
        startIndex + rowsPerPage;

    return quizQuestions.slice(startIndex, endIndex);
}

function updateQuizQuestionsPaginationControls(filteredQuizQuestions) {
    const totalPages =
        getTotalQuizQuestionPages(filteredQuizQuestions);

    if (currentQuizQuestionsPage > totalPages) {
        currentQuizQuestionsPage =
            totalPages;
    }

    document
        .getElementById(QUIZ_QUESTIONS_PAGINATION_STATUS_ID)
        .textContent =
        `Page ${currentQuizQuestionsPage} of ${totalPages}`;

    setElementDisabled(
        QUIZ_QUESTIONS_PREVIOUS_PAGE_BUTTON_ID,
        currentQuizQuestionsPage <= 1
    );

    setElementDisabled(
        QUIZ_QUESTIONS_NEXT_PAGE_BUTTON_ID,
        currentQuizQuestionsPage >= totalPages
    );
}

function renderQuizQuestionsTable(quizQuestions) {
    const tableBody =
        document.getElementById(QUIZ_QUESTIONS_TABLE_BODY_ID);

    tableBody.innerHTML = quizQuestions.map((quizQuestion) => `
        <tr data-quiz-question-id="${escapeHtml(getQuizQuestionId(quizQuestion))}">
            <td>${escapeHtml(getQuizQuestionId(quizQuestion))}</td>

            <td>
                ${escapeHtml(getQuizQuestionText(quizQuestion))}
            </td>

            <td>
                ${escapeHtml(getQuizQuestionCategoryName(quizQuestion))}
            </td>

            <td>
                ${escapeHtml(formatBoolean(getQuizQuestionIsActive(quizQuestion)))}
            </td>
        </tr>
    `).join("");
}

initializeTableSorting();

function renderTableMessage(message) {
    const tableBody =
        document.getElementById(QUIZ_QUESTIONS_TABLE_BODY_ID);

    tableBody.innerHTML = `
        <tr>
            <td colspan="4">
                ${escapeHtml(message)}
            </td>
        </tr>
    `;
}

function renderEmptyQuizQuestionsState() {
    renderTableMessage("No quiz questions found.");
}

function renderEmptySearchState() {
    renderTableMessage("No matching quiz questions found.");
}

function renderQuizQuestionsLoadError() {
    renderTableMessage("Failed to load quiz questions.");
}

function renderQuizQuestionsForCurrentState() {
    const filteredQuizQuestions =
        filterQuizQuestions(getSearchInputValue());

    if (filteredQuizQuestions.length === 0) {
        renderEmptySearchState();
        updateQuizQuestionsPaginationControls(filteredQuizQuestions);
        return;
    }

    updateQuizQuestionsPaginationControls(filteredQuizQuestions);

    renderQuizQuestionsTable(
        getPagedQuizQuestions(filteredQuizQuestions)
    );

    initializeTableSorting();
}


function handleSearchInput() {
    hideMessage(QUIZ_QUESTIONS_MESSAGE_ID);

    currentQuizQuestionsPage =
        1;

    renderQuizQuestionsForCurrentState();
}

function handlePreviousPageClick() {
    if (currentQuizQuestionsPage <= 1) {
        return;
    }

    currentQuizQuestionsPage -=
        1;

    renderQuizQuestionsForCurrentState();
}

function handleNextPageClick() {
    const filteredQuizQuestions =
        filterQuizQuestions(getSearchInputValue());

    const totalPages =
        getTotalQuizQuestionPages(filteredQuizQuestions);

    if (currentQuizQuestionsPage >= totalPages) {
        return;
    }

    currentQuizQuestionsPage +=
        1;

    renderQuizQuestionsForCurrentState();
}

function enableQuizQuestionsSearch() {
    setElementDisabled(
        QUIZ_QUESTIONS_SEARCH_INPUT_ID,
        false
    );
}

async function loadQuizQuestions() {
    hideMessage(QUIZ_QUESTIONS_MESSAGE_ID);

    try {
        const data =
            await getJson(
                LLA_API_ENDPOINTS.admin.quizQuestions.list
            );

        const quizQuestions =
            data.quizQuestions;

        if (!quizQuestions || quizQuestions.length === 0) {
            allQuizQuestions =
                [];

            renderEmptyQuizQuestionsState();
            updateQuizQuestionsPaginationControls(allQuizQuestions);
            enableQuizQuestionsSearch();

            return;
        }

        allQuizQuestions =
            quizQuestions;

        currentQuizQuestionsPage =
            1;

        renderQuizQuestionsForCurrentState();
        enableQuizQuestionsSearch();

    } catch (error) {
        console.error(error);

        renderQuizQuestionsLoadError();

        showErrorMessage(
            QUIZ_QUESTIONS_MESSAGE_ID,
            error.message || "Failed to load quiz questions."
        );
    }
}

document
    .getElementById(QUIZ_QUESTIONS_TABLE_BODY_ID)
    .addEventListener("click", handleQuizQuestionRowClick);

document
    .getElementById("backToAdminButton")
    .addEventListener("click", navigateToAdminDashboard);

document
    .getElementById("addQuizQuestionButton")
    .addEventListener("click", navigateToCreateQuizQuestion);

document
    .getElementById(QUIZ_QUESTIONS_SEARCH_INPUT_ID)
    .addEventListener("input", handleSearchInput);

document
    .getElementById(QUIZ_QUESTIONS_PREVIOUS_PAGE_BUTTON_ID)
    .addEventListener("click", handlePreviousPageClick);

document
    .getElementById(QUIZ_QUESTIONS_NEXT_PAGE_BUTTON_ID)
    .addEventListener("click", handleNextPageClick);

loadQuizQuestions();
const QUIZ_QUESTION_CREATE_MESSAGE_ID =
    "quizQuestionCreateMessage";

const CREATE_QUIZ_QUESTION_BUTTON_ID =
    "createQuizQuestionButton";

const QUIZ_QUESTION_OPTIONS_TABLE_BODY_ID =
    "quizQuestionOptionsTableBody";

const ADD_QUIZ_QUESTION_OPTION_BUTTON_ID =
    "addQuizQuestionOptionButton";

const ANSWER_OPTION_TEXT_INPUT_ID =
    "answerOptionText";

const ANSWER_OPTION_IS_CORRECT_INPUT_ID =
    "answerOptionIsCorrect";

const EMPTY_OPTION_TEXT =
    "";

const DEFAULT_UPDATED_BY =
    "admin";

let answerOptions =
    [];

function navigateBackToQuizQuestions() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.quizQuestions.list;
}

function renderCategoryOptions(categories) {
    const categorySelect =
        document.getElementById("categoryId");

    categorySelect.innerHTML = `
        <option value="">Select category</option>
    `;

    categories.forEach((category) => {
        const option =
            document.createElement("option");

        option.value =
            category.categoryId;

        option.textContent =
            category.name;

        categorySelect.appendChild(option);
    });
}

async function loadCategories() {
    const data =
        await getJson(LLA_API_ENDPOINTS.admin.lessonCategories.list);

    if (!data.success || !data.lessonCategories) {
        throw new Error(data.error || "Failed to load categories.");
    }

    renderCategoryOptions(data.lessonCategories);
}

function normalizeAnswerOptions(options) {
    return options.map((answerOption, index) => ({
        optionText: answerOption.optionText || "",
        isCorrect: Boolean(answerOption.isCorrect),
        displayOrder: index + 1
    }));
}

function getAnswerOptionRowClass(index) {
    return index % 2 === 0
        ? "quiz-question-option-row even"
        : "quiz-question-option-row odd";
}

function readAnswerOptionDetails() {
    return {
        optionText:
            document
                .getElementById(ANSWER_OPTION_TEXT_INPUT_ID)
                .value
                .trim(),

        isCorrect:
            document
                .getElementById(ANSWER_OPTION_IS_CORRECT_INPUT_ID)
                .checked
    };
}

function clearAnswerOptionDetails() {
    document.getElementById(ANSWER_OPTION_TEXT_INPUT_ID).value =
        EMPTY_OPTION_TEXT;

    document.getElementById(ANSWER_OPTION_IS_CORRECT_INPUT_ID).checked =
        false;

    document
        .getElementById(ANSWER_OPTION_TEXT_INPUT_ID)
        .focus();
}

function renderQuizQuestionOptions(options) {
    const tableBody =
        document.getElementById(QUIZ_QUESTION_OPTIONS_TABLE_BODY_ID);

    if (!options || options.length === 0) {
        tableBody.innerHTML = `
            <tr class="quiz-question-option-empty-row">
                <td colspan="4">No answer options added yet.</td>
            </tr>
        `;

        return;
    }

    tableBody.innerHTML =
        options.map((option, index) => `
            <tr
                class="${getAnswerOptionRowClass(index)}"
                data-answer-option-index="${index}"
            >
                <td>
                    ${escapeHtml(option.displayOrder)}
                </td>

                <td>
                    ${escapeHtml(option.optionText)}
                </td>

                <td>
                    <input
                        class="quiz-question-option-correct-input"
                        type="radio"
                        name="correctQuizQuestionOption"
                        value="${index}"
                        data-answer-option-action="set-correct"
                        data-answer-option-index="${index}"
                        ${option.isCorrect ? "checked" : ""}
                    >
                </td>

                <td>
                    <div class="quiz-question-option-action-group">
                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Move up"
                            aria-label="Move answer option up"
                            ${index === 0 ? "disabled" : ""}
                            data-answer-option-action="move-up"
                            data-answer-option-index="${index}">
                            ↑
                        </button>

                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Move down"
                            aria-label="Move answer option down"
                            ${index === options.length - 1 ? "disabled" : ""}
                            data-answer-option-action="move-down"
                            data-answer-option-index="${index}">
                            ↓
                        </button>

                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Remove"
                            aria-label="Remove answer option"
                            data-answer-option-action="remove"
                            data-answer-option-index="${index}">
                            🗑
                        </button>
                    </div>                
                </td>
            </tr>
        `).join("");
}

function renderAnswerOptionsTable() {
    renderQuizQuestionOptions(answerOptions);
}

function addAnswerOption() {
    hideMessage(QUIZ_QUESTION_CREATE_MESSAGE_ID);

    const optionDetails =
        readAnswerOptionDetails();

    if (!optionDetails.optionText) {
        showErrorMessage(
            QUIZ_QUESTION_CREATE_MESSAGE_ID,
            "Option text is required."
        );

        return;
    }

    if (optionDetails.isCorrect) {
        answerOptions =
            answerOptions.map((answerOption) => ({
                ...answerOption,
                isCorrect: false
            }));
    }

    answerOptions.push({
        optionText: optionDetails.optionText,
        isCorrect:
            optionDetails.isCorrect || answerOptions.length === 0,
        displayOrder: answerOptions.length + 1
    });

    answerOptions =
        normalizeAnswerOptions(answerOptions);

    renderAnswerOptionsTable();
    clearAnswerOptionDetails();
}

function moveAnswerOptionUp(index) {
    if (index <= 0) {
        return;
    }

    const movedOption =
        answerOptions[index];

    answerOptions[index] =
        answerOptions[index - 1];

    answerOptions[index - 1] =
        movedOption;

    answerOptions =
        normalizeAnswerOptions(answerOptions);

    renderAnswerOptionsTable();
}

function moveAnswerOptionDown(index) {
    if (index >= answerOptions.length - 1) {
        return;
    }

    const movedOption =
        answerOptions[index];

    answerOptions[index] =
        answerOptions[index + 1];

    answerOptions[index + 1] =
        movedOption;

    answerOptions =
        normalizeAnswerOptions(answerOptions);

    renderAnswerOptionsTable();
}

function removeAnswerOption(index) {
    answerOptions.splice(index, 1);

    if (
        answerOptions.length > 0 &&
        !answerOptions.some((answerOption) => answerOption.isCorrect)
    ) {
        answerOptions[0].isCorrect =
            true;
    }

    answerOptions =
        normalizeAnswerOptions(answerOptions);

    renderAnswerOptionsTable();
}

function setCorrectAnswerOption(index) {
    answerOptions =
        answerOptions.map((answerOption, answerOptionIndex) => ({
            ...answerOption,
            isCorrect: answerOptionIndex === index
        }));

    renderAnswerOptionsTable();
}

function handleAnswerOptionsTableClick(event) {
    const actionButton =
        event.target.closest("button[data-answer-option-action]");

    if (!actionButton) {
        return;
    }

    const index =
        Number(actionButton.dataset.answerOptionIndex);

    const action =
        actionButton.dataset.answerOptionAction;

    if (action === "move-up") {
        moveAnswerOptionUp(index);
        return;
    }

    if (action === "move-down") {
        moveAnswerOptionDown(index);
        return;
    }

    if (action === "remove") {
        removeAnswerOption(index);
    }
}

function handleAnswerOptionCorrectChange(event) {
    const correctInput =
        event.target.closest("input[data-answer-option-action='set-correct']");

    if (!correctInput) {
        return;
    }

    const index =
        Number(correctInput.dataset.answerOptionIndex);

    setCorrectAnswerOption(index);
}

function readAnswerOptionsFormData() {
    return normalizeAnswerOptions(answerOptions);
}

function validateAnswerOptions(options) {
    if (options.length < 2) {
        throw new Error("At least two answer options are required.");
    }

    if (options.some((answerOption) => !answerOption.optionText)) {
        throw new Error("All answer options must have option text.");
    }

    const correctAnswerOptions =
        options.filter((answerOption) => answerOption.isCorrect);

    if (correctAnswerOptions.length !== 1) {
        throw new Error("Exactly one answer option must be marked as correct.");
    }
}

function buildQuizQuestionOptionsPayload(options) {
    return {
        answerOptions: options.map((option, index) => ({
            optionText: option.optionText,
            isCorrect: Boolean(option.isCorrect),
            displayOrder: index + 1
        })),
        updatedBy: DEFAULT_UPDATED_BY
    };
}

function readQuizQuestionFormData() {
    const answerOptionsData =
        readAnswerOptionsFormData();

    validateAnswerOptions(answerOptionsData);

    return {
        questionText: document.getElementById("questionText").value.trim(),
        categoryId: Number(document.getElementById("categoryId").value),
        isActive: document.getElementById("isActive").checked,
        updatedBy: DEFAULT_UPDATED_BY
    };
}

function clearQuizQuestionForm() {
    document.getElementById("quizQuestionCreateForm").reset();

    document.getElementById("isActive").checked =
        true;

    answerOptions =
        [];

    clearAnswerOptionDetails();
    renderAnswerOptionsTable();
}

async function createQuizQuestion(event) {
    event.preventDefault();

    hideMessage(QUIZ_QUESTION_CREATE_MESSAGE_ID);

    let quizQuestionPayload;
    let answerOptionsPayload;

    try {
        answerOptionsPayload =
            readAnswerOptionsFormData();

        validateAnswerOptions(answerOptionsPayload);

        quizQuestionPayload =
            readQuizQuestionFormData();

    } catch (error) {
        showErrorMessage(
            QUIZ_QUESTION_CREATE_MESSAGE_ID,
            error.message
        );

        return;
    }

    setElementDisabled(CREATE_QUIZ_QUESTION_BUTTON_ID, true);
    setElementDisabled(ADD_QUIZ_QUESTION_OPTION_BUTTON_ID, true);

    setButtonText(
        CREATE_QUIZ_QUESTION_BUTTON_ID,
        "Creating..."
    );

    try {
        const quizQuestionData =
            await postJson(
                LLA_API_ENDPOINTS.admin.quizQuestions.create,
                quizQuestionPayload
            );

        if (!quizQuestionData.success) {
            throw new Error(
                quizQuestionData.error ||
                "Failed to create quiz question."
            );
        }

        const createdQuestionId =
            quizQuestionData.quizQuestion?.questionId;

        if (!createdQuestionId) {
            throw new Error(
                "Created quiz question ID is missing."
            );
        }

        const quizQuestionOptionsData =
            await putJson(
                LLA_API_ENDPOINTS.admin.quizQuestionOptions.byQuestionId(
                    createdQuestionId
                ),
                buildQuizQuestionOptionsPayload(
                    answerOptionsPayload
                )
            );

        if (!quizQuestionOptionsData.success) {
            throw new Error(
                quizQuestionOptionsData.error ||
                "Failed to create answer options."
            );
        }

        clearQuizQuestionForm();

        showSuccessMessage(
            QUIZ_QUESTION_CREATE_MESSAGE_ID,
            "Quiz question created successfully."
        );

    } catch (error) {
        console.error(error);

        showErrorMessage(
            QUIZ_QUESTION_CREATE_MESSAGE_ID,
            error.message ||
            "Failed to create quiz question."
        );

    } finally {
        setElementDisabled(CREATE_QUIZ_QUESTION_BUTTON_ID, false);
        setElementDisabled(ADD_QUIZ_QUESTION_OPTION_BUTTON_ID, false);

        setButtonText(
            CREATE_QUIZ_QUESTION_BUTTON_ID,
            "Create quiz question"
        );
    }
}

async function initializeQuizQuestionCreatePage() {
    try {
        await loadCategories();
        renderAnswerOptionsTable();

    } catch (error) {
        console.error(error);

        showErrorMessage(
            QUIZ_QUESTION_CREATE_MESSAGE_ID,
            error.message ||
            "Failed to initialize quiz question create page."
        );
    }
}

document
    .getElementById("backToQuizQuestionsButton")
    .addEventListener("click", navigateBackToQuizQuestions);

document
    .getElementById("quizQuestionCreateForm")
    .addEventListener("submit", createQuizQuestion);

document
    .getElementById(ADD_QUIZ_QUESTION_OPTION_BUTTON_ID)
    .addEventListener("click", addAnswerOption);

document
    .getElementById(QUIZ_QUESTION_OPTIONS_TABLE_BODY_ID)
    .addEventListener("click", handleAnswerOptionsTableClick);

document
    .getElementById(QUIZ_QUESTION_OPTIONS_TABLE_BODY_ID)
    .addEventListener("change", handleAnswerOptionCorrectChange);

initializeQuizQuestionCreatePage();
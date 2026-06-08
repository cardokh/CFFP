const QUIZ_QUESTION_EDIT_MESSAGE_ID =
    "quizQuestionEditMessage";

const SAVE_QUIZ_QUESTION_BUTTON_ID =
    "saveQuizQuestionButton";

const DELETE_QUIZ_QUESTION_BUTTON_ID =
    "deleteQuizQuestionButton";

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

let leaveWithoutSavingConfirmed =
    false;

let originalQuizQuestionFormData =
    null;

let originalQuizQuestionOptionsData =
    [];

let currentQuizQuestionOptions =
    [];

function getQuizQuestionIdFromUrl() {
    const params =
        new URLSearchParams(window.location.search);

    return params.get("questionId");
}

function navigateBackToQuizQuestions() {
    const hasChanges =
        hasQuizQuestionFormChanged(readQuizQuestionFormData()) ||
        hasQuizQuestionOptionsChanged(
            normalizeQuizQuestionOptions(currentQuizQuestionOptions)
        );

    if (!hasChanges) {
        window.location.href =
            LLA_PATHS.desktop.protected.admin.quizQuestions.list;

        return;
    }

    if (!leaveWithoutSavingConfirmed) {
        leaveWithoutSavingConfirmed =
            true;

        showInfoMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            "Unsaved changes detected. Click Save to apply your changes or click Back again to leave without saving."
        );

        return;
    }

    window.location.href =
        LLA_PATHS.desktop.protected.admin.quizQuestions.list;
}

function formatBoolean(value) {
    return value ? "Yes" : "No";
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

function renderCategoryOptions(categories, selectedCategoryId) {
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

        if (Number(category.categoryId) === Number(selectedCategoryId)) {
            option.selected =
                true;
        }

        categorySelect.appendChild(option);
    });
}

async function loadCategories(selectedCategoryId) {
    const data =
        await getJson(LLA_API_ENDPOINTS.admin.lessonCategories.list);

    if (!data.success || !data.lessonCategories) {
        throw new Error(data.error || "Failed to load categories.");
    }

    renderCategoryOptions(data.lessonCategories, selectedCategoryId);
}

async function loadQuizQuestionOptions(questionId) {
    const data =
        await getJson(
            LLA_API_ENDPOINTS.admin.quizQuestionOptions.byQuestionId(questionId)
        );

    if (!data.success || !data.quizQuestionOptions) {
        throw new Error(data.error || "Failed to load answer options.");
    }

    return data.quizQuestionOptions;
}

function normalizeQuizQuestionOptions(options) {
    return options.map((option, index) => ({
        optionId: option.optionId || null,
        optionText: option.optionText || "",
        isCorrect: Boolean(option.isCorrect),
        displayOrder: index + 1
    }));
}

function normalizeQuizQuestionOptionsForComparison(options) {
    return options.map((option, index) => ({
        optionText: option.optionText || "",
        isCorrect: Boolean(option.isCorrect),
        displayOrder: index + 1
    }));
}

function renderQuizQuestionOptions(options) {
    const tableBody =
        document.getElementById(QUIZ_QUESTION_OPTIONS_TABLE_BODY_ID);

    if (!options || options.length === 0) {
        tableBody.innerHTML = `
            <tr class="quiz-question-option-empty-row">
                <td colspan="4">No answer options found.</td>
            </tr>
        `;

        return;
    }

    tableBody.innerHTML =
        options.map((option, index) => `
            <tr
                class="${getAnswerOptionRowClass(index)}"
                data-option-index="${index}"
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
                        data-option-action="set-correct"
                        data-option-index="${index}"
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
                            data-option-action="move-up"
                            data-option-index="${index}">
                            ↑
                        </button>

                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Move down"
                            aria-label="Move answer option down"                            
                            ${index === options.length - 1 ? "disabled" : ""}
                            data-option-action="move-down"
                            data-option-index="${index}">
                            ↓
                        </button>

                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Remove"
                            aria-label="Remove answer option"
                            data-option-action="remove"
                            data-option-index="${index}">
                            🗑
                        </button>
                    </div>
                </td>
            </tr>
        `).join("");
}

function addQuizQuestionOption() {
    hideMessage(QUIZ_QUESTION_EDIT_MESSAGE_ID);

    const optionDetails =
        readAnswerOptionDetails();

    if (!optionDetails.optionText) {
        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            "Option text is required."
        );

        return;
    }

    if (optionDetails.isCorrect) {
        currentQuizQuestionOptions =
            currentQuizQuestionOptions.map((option) => ({
                ...option,
                isCorrect: false
            }));
    }

    currentQuizQuestionOptions.push({
        optionId: null,
        optionText: optionDetails.optionText,
        isCorrect:
            optionDetails.isCorrect || currentQuizQuestionOptions.length === 0,
        displayOrder: currentQuizQuestionOptions.length + 1
    });

    currentQuizQuestionOptions =
        normalizeQuizQuestionOptions(currentQuizQuestionOptions);

    renderQuizQuestionOptions(currentQuizQuestionOptions);
    clearAnswerOptionDetails();
}

function moveQuizQuestionOptionUp(optionIndex) {
    if (optionIndex <= 0) {
        return;
    }

    const movedOption =
        currentQuizQuestionOptions[optionIndex];

    currentQuizQuestionOptions[optionIndex] =
        currentQuizQuestionOptions[optionIndex - 1];

    currentQuizQuestionOptions[optionIndex - 1] =
        movedOption;

    currentQuizQuestionOptions =
        normalizeQuizQuestionOptions(currentQuizQuestionOptions);

    renderQuizQuestionOptions(currentQuizQuestionOptions);
}

function moveQuizQuestionOptionDown(optionIndex) {
    if (optionIndex >= currentQuizQuestionOptions.length - 1) {
        return;
    }

    const movedOption =
        currentQuizQuestionOptions[optionIndex];

    currentQuizQuestionOptions[optionIndex] =
        currentQuizQuestionOptions[optionIndex + 1];

    currentQuizQuestionOptions[optionIndex + 1] =
        movedOption;

    currentQuizQuestionOptions =
        normalizeQuizQuestionOptions(currentQuizQuestionOptions);

    renderQuizQuestionOptions(currentQuizQuestionOptions);
}

function removeQuizQuestionOption(optionIndex) {
    currentQuizQuestionOptions.splice(optionIndex, 1);

    if (
        currentQuizQuestionOptions.length > 0 &&
        !currentQuizQuestionOptions.some((option) => option.isCorrect)
    ) {
        currentQuizQuestionOptions[0].isCorrect =
            true;
    }

    currentQuizQuestionOptions =
        normalizeQuizQuestionOptions(currentQuizQuestionOptions);

    renderQuizQuestionOptions(currentQuizQuestionOptions);
}

function setCorrectQuizQuestionOption(optionIndex) {
    currentQuizQuestionOptions =
        currentQuizQuestionOptions.map((option, index) => ({
            ...option,
            isCorrect: index === optionIndex
        }));

    renderQuizQuestionOptions(currentQuizQuestionOptions);
}

function handleQuizQuestionOptionActionClick(event) {
    const actionButton =
        event.target.closest("button[data-option-action]");

    if (!actionButton) {
        return;
    }

    const optionIndex =
        Number(actionButton.dataset.optionIndex);

    const optionAction =
        actionButton.dataset.optionAction;

    if (Number.isNaN(optionIndex)) {
        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            "Answer option index is missing."
        );

        return;
    }

    if (optionAction === "move-up") {
        moveQuizQuestionOptionUp(optionIndex);
        return;
    }

    if (optionAction === "move-down") {
        moveQuizQuestionOptionDown(optionIndex);
        return;
    }

    if (optionAction === "remove") {
        removeQuizQuestionOption(optionIndex);
    }
}

function handleQuizQuestionOptionCorrectChange(event) {
    const correctInput =
        event.target.closest("input[data-option-action='set-correct']");

    if (!correctInput) {
        return;
    }

    const optionIndex =
        Number(correctInput.dataset.optionIndex);

    if (Number.isNaN(optionIndex)) {
        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            "Answer option index is missing."
        );

        return;
    }

    setCorrectQuizQuestionOption(optionIndex);
}

async function populateQuizQuestionForm(quizQuestion, answerOptions) {
    document.getElementById("questionId").value =
        quizQuestion.questionId;

    document.getElementById("questionText").value =
        quizQuestion.questionText || "";

    await loadCategories(quizQuestion.categoryId);

    document.getElementById("isActive").checked =
        Boolean(quizQuestion.isActive);

    currentQuizQuestionOptions =
        normalizeQuizQuestionOptions(answerOptions || []);

    originalQuizQuestionOptionsData =
        normalizeQuizQuestionOptions(currentQuizQuestionOptions);

    renderQuizQuestionOptions(currentQuizQuestionOptions);
}

function readQuizQuestionFormData() {
    return {
        questionText: document.getElementById("questionText").value.trim(),
        categoryId: Number(document.getElementById("categoryId").value),
        isActive: document.getElementById("isActive").checked,
        updatedBy: DEFAULT_UPDATED_BY
    };
}

function normalizeQuizQuestionFormDataForComparison(formData) {
    return {
        questionText: formData.questionText || "",
        categoryId: Number(formData.categoryId),
        isActive: Boolean(formData.isActive)
    };
}

function hasQuizQuestionFormChanged(currentFormData) {
    if (!originalQuizQuestionFormData) {
        return true;
    }

    return JSON.stringify(
        normalizeQuizQuestionFormDataForComparison(currentFormData)
    ) !== JSON.stringify(
        normalizeQuizQuestionFormDataForComparison(
            originalQuizQuestionFormData
        )
    );
}

function hasQuizQuestionOptionsChanged(currentOptionsData) {
    return JSON.stringify(
        normalizeQuizQuestionOptionsForComparison(currentOptionsData)
    ) !== JSON.stringify(
        normalizeQuizQuestionOptionsForComparison(
            originalQuizQuestionOptionsData
        )
    );
}

function storeOriginalQuizQuestionFormData() {
    originalQuizQuestionFormData =
        readQuizQuestionFormData();
}

function storeOriginalQuizQuestionOptionsData() {
    originalQuizQuestionOptionsData =
        normalizeQuizQuestionOptions(currentQuizQuestionOptions);
}

function validateQuizQuestionOptions(options) {
    if (options.length < 2) {
        throw new Error("At least two answer options are required.");
    }

    if (options.some((option) => !option.optionText)) {
        throw new Error("All answer options must have option text.");
    }

    const correctOptions =
        options.filter((option) => option.isCorrect);

    if (correctOptions.length !== 1) {
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

async function loadQuizQuestionForEdit() {
    const quizQuestionId =
        getQuizQuestionIdFromUrl();

    if (!quizQuestionId) {
        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            "Quiz question ID is missing."
        );

        return;
    }

    try {
        const quizQuestionData =
            await getJson(
                LLA_API_ENDPOINTS.admin.quizQuestions.byId(quizQuestionId)
            );

        if (!quizQuestionData.success || !quizQuestionData.quizQuestion) {
            showErrorMessage(
                QUIZ_QUESTION_EDIT_MESSAGE_ID,
                quizQuestionData.error || "Quiz question not found."
            );

            return;
        }

        const answerOptions =
            await loadQuizQuestionOptions(quizQuestionId);

        await populateQuizQuestionForm(
            quizQuestionData.quizQuestion,
            answerOptions
        );

        storeOriginalQuizQuestionFormData();
        storeOriginalQuizQuestionOptionsData();

    } catch (error) {
        console.error(error);

        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            error.message || "Failed to load quiz question."
        );
    }
}

async function deleteQuizQuestion() {
    const quizQuestionId =
        getQuizQuestionIdFromUrl();

    if (!quizQuestionId) {
        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            "Quiz question ID is missing."
        );

        return;
    }

    const confirmed =
        confirm("Are you sure you want to delete this quiz question?");

    if (!confirmed) {
        return;
    }

    hideMessage(QUIZ_QUESTION_EDIT_MESSAGE_ID);

    setElementDisabled(DELETE_QUIZ_QUESTION_BUTTON_ID, true);
    setButtonText(DELETE_QUIZ_QUESTION_BUTTON_ID, "Deleting...");

    try {
        const data =
            await deleteJson(
                LLA_API_ENDPOINTS.admin.quizQuestions.byId(quizQuestionId)
            );

        if (!data.success) {
            throw new Error(
                data.error || "Failed to delete quiz question."
            );
        }

        navigateBackToQuizQuestions();

    } catch (error) {
        console.error(error);

        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            error.message || "Failed to delete quiz question."
        );

        setElementDisabled(DELETE_QUIZ_QUESTION_BUTTON_ID, false);
        setButtonText(DELETE_QUIZ_QUESTION_BUTTON_ID, "Delete");
    }
}

async function saveQuizQuestion(event) {
    event.preventDefault();

    const quizQuestionId =
        getQuizQuestionIdFromUrl();

    if (!quizQuestionId) {
        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            "Quiz question ID is missing."
        );

        return;
    }

    hideMessage(QUIZ_QUESTION_EDIT_MESSAGE_ID);

    const quizQuestionPayload =
        readQuizQuestionFormData();

    const quizQuestionOptionsPayload =
        normalizeQuizQuestionOptions(currentQuizQuestionOptions);

    try {
        validateQuizQuestionOptions(quizQuestionOptionsPayload);

    } catch (error) {
        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            error.message
        );

        return;
    }

    const quizQuestionChanged =
        hasQuizQuestionFormChanged(quizQuestionPayload);

    const quizQuestionOptionsChanged =
        hasQuizQuestionOptionsChanged(quizQuestionOptionsPayload);

    if (!quizQuestionChanged && !quizQuestionOptionsChanged) {
        showInfoMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            "No changes detected."
        );

        return;
    }

    setElementDisabled(SAVE_QUIZ_QUESTION_BUTTON_ID, true);
    setElementDisabled(DELETE_QUIZ_QUESTION_BUTTON_ID, true);
    setElementDisabled(ADD_QUIZ_QUESTION_OPTION_BUTTON_ID, true);
    setButtonText(SAVE_QUIZ_QUESTION_BUTTON_ID, "Saving...");

    try {
        if (quizQuestionChanged) {
            const quizQuestionData =
                await putJson(
                    LLA_API_ENDPOINTS.admin.quizQuestions.byId(quizQuestionId),
                    quizQuestionPayload
                );

            if (!quizQuestionData.success) {
                throw new Error(
                    quizQuestionData.error || "Failed to update quiz question."
                );
            }
        }

        if (quizQuestionOptionsChanged) {
            const quizQuestionOptionsData =
                await putJson(
                    LLA_API_ENDPOINTS.admin.quizQuestionOptions.byQuestionId(
                        quizQuestionId
                    ),
                    buildQuizQuestionOptionsPayload(
                        quizQuestionOptionsPayload
                    )
                );

            if (!quizQuestionOptionsData.success) {
                throw new Error(
                    quizQuestionOptionsData.error ||
                    "Failed to update answer options."
                );
            }

            currentQuizQuestionOptions =
                normalizeQuizQuestionOptions(
                    quizQuestionOptionsData.quizQuestionOptions ||
                    quizQuestionOptionsPayload
                );

            renderQuizQuestionOptions(currentQuizQuestionOptions);
        }

        originalQuizQuestionFormData =
            quizQuestionPayload;

        storeOriginalQuizQuestionOptionsData();

        leaveWithoutSavingConfirmed =
            false;

        showSuccessMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            "Quiz question updated successfully."
        );

    } catch (error) {
        console.error(error);

        showErrorMessage(
            QUIZ_QUESTION_EDIT_MESSAGE_ID,
            error.message || "Failed to update quiz question."
        );

    } finally {
        setElementDisabled(SAVE_QUIZ_QUESTION_BUTTON_ID, false);
        setElementDisabled(DELETE_QUIZ_QUESTION_BUTTON_ID, false);
        setElementDisabled(ADD_QUIZ_QUESTION_OPTION_BUTTON_ID, false);
        setButtonText(SAVE_QUIZ_QUESTION_BUTTON_ID, "Save");
    }
}

function resetLeaveWithoutSavingConfirmation() {
    leaveWithoutSavingConfirmed =
        false;
}

document
    .getElementById("backToQuizQuestionsButton")
    .addEventListener("click", navigateBackToQuizQuestions);

document
    .getElementById(ADD_QUIZ_QUESTION_OPTION_BUTTON_ID)
    .addEventListener("click", addQuizQuestionOption);

document
    .getElementById(ADD_QUIZ_QUESTION_OPTION_BUTTON_ID)
    .addEventListener("click", resetLeaveWithoutSavingConfirmation);

document
    .getElementById(QUIZ_QUESTION_OPTIONS_TABLE_BODY_ID)
    .addEventListener("click", handleQuizQuestionOptionActionClick);

document
    .getElementById(QUIZ_QUESTION_OPTIONS_TABLE_BODY_ID)
    .addEventListener("change", handleQuizQuestionOptionCorrectChange);

document
    .getElementById(QUIZ_QUESTION_OPTIONS_TABLE_BODY_ID)
    .addEventListener("click", resetLeaveWithoutSavingConfirmation);

document
    .getElementById(QUIZ_QUESTION_OPTIONS_TABLE_BODY_ID)
    .addEventListener("change", resetLeaveWithoutSavingConfirmation);

document
    .getElementById(DELETE_QUIZ_QUESTION_BUTTON_ID)
    .addEventListener("click", deleteQuizQuestion);

document
    .getElementById("quizQuestionEditForm")
    .addEventListener("input", resetLeaveWithoutSavingConfirmation);

document
    .getElementById("quizQuestionEditForm")
    .addEventListener("submit", saveQuizQuestion);

loadQuizQuestionForEdit();
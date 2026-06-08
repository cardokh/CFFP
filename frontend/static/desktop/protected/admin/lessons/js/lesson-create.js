const LESSON_CREATE_MESSAGE_ID =
    "lessonCreateMessage";

const CREATE_LESSON_BUTTON_ID =
    "createLessonButton";

const ASSIGNED_LEARNING_ITEMS_TABLE_BODY_ID =
    "assignedLearningItemsTableBody";

const ASSIGNED_QUIZ_QUESTIONS_TABLE_BODY_ID =
    "assignedQuizQuestionsTableBody";

let assignedLearningItems = [];
let assignedQuizQuestions = [];
let availableLearningItems = [];
let availableQuizQuestions = [];
let leaveWithoutSavingConfirmed = false;

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function navigateBackToLessons() {
    if (!hasUnsavedChanges()) {
        window.location.href =
            LLA_PATHS.desktop.protected.admin.lessons.list;

        return;
    }

    if (!leaveWithoutSavingConfirmed) {
        leaveWithoutSavingConfirmed =
            true;

        showInfoMessage(
            LESSON_CREATE_MESSAGE_ID,
            "Unsaved changes detected. Click Create lesson to save the lesson or click Back again to leave without saving."
        );

        return;
    }

    window.location.href =
        LLA_PATHS.desktop.protected.admin.lessons.list;
}



function showLearningItemsTab() {
    document.getElementById("learningItemsTabButton").classList.add("active");
    document.getElementById("quizQuestionsTabButton").classList.remove("active");
    document.getElementById("learningItemsTabPanel").classList.remove("hidden");
    document.getElementById("quizQuestionsTabPanel").classList.add("hidden");
}


function showQuizQuestionsTab() {
    document.getElementById("quizQuestionsTabButton").classList.add("active");
    document.getElementById("learningItemsTabButton").classList.remove("active");
    document.getElementById("quizQuestionsTabPanel").classList.remove("hidden");
    document.getElementById("learningItemsTabPanel").classList.add("hidden");
}


function populateSelect(selectId, items, defaultLabel) {
    const select = document.getElementById(selectId);

    select.innerHTML =
        `<option value="">${escapeHtml(defaultLabel)}</option>`;

    items.forEach((item) => {
        const option = document.createElement("option");

        option.value = item.id;
        option.textContent = item.name;

        select.appendChild(option);
    });

    setElementDisabled(selectId, false);
}


function populateLessonFormOptions(formOptions) {
    populateSelect("categoryId", formOptions.lesson_categories, "Select category");
    populateSelect("lessonTypeId", formOptions.lesson_types, "Select lesson type");
    populateSelect("embodimentTypeId", formOptions.embodiment_types, "Select embodiment");
    populateSelect("interactionStyleId", formOptions.interaction_styles, "Select interaction style");
}


function readLessonFormData() {
    return {
        title: document.getElementById("title").value.trim(),
        description: document.getElementById("description").value.trim(),
        categoryId: Number(document.getElementById("categoryId").value),
        lessonTypeId: Number(document.getElementById("lessonTypeId").value),
        embodimentTypeId: Number(document.getElementById("embodimentTypeId").value),
        interactionStyleId: Number(document.getElementById("interactionStyleId").value),
        isActive: document.getElementById("isActive").checked
    };
}


function buildCreateLessonPayload(formData) {
    return {
        title: formData.title,
        description: formData.description,
        category_id: formData.categoryId,
        lesson_type_id: formData.lessonTypeId,
        embodiment_type_id: formData.embodimentTypeId,
        interaction_style_id: formData.interactionStyleId,
        is_active: formData.isActive,
        updated_by: "admin"
    };
}


function clearLessonForm() {
    document.getElementById("lessonCreateForm").reset();

    document.getElementById("isActive").checked = true;

    assignedLearningItems = [];
    assignedQuizQuestions = [];

    renderAssignedLearningItems();
    renderAssignedQuizQuestions();

    populateAvailableLearningItemsSelect();
    populateAvailableQuizQuestionsSelect();

    showLearningItemsTab();

    leaveWithoutSavingConfirmed = false;
}


function getAssignedLearningItemIds() {
    return assignedLearningItems.map((item) =>
        Number(item.itemId)
    );
}


function getAssignedQuizQuestionIds() {
    return assignedQuizQuestions.map((question) =>
        Number(question.questionId)
    );
}


function getLearningItemDisplayText(item) {
    return item.sourceText || "";
}


function populateAvailableLearningItemsSelect() {
    const select =
        document.getElementById("availableLearningItemSelect");

    const assignedIds =
        new Set(getAssignedLearningItemIds());

    select.innerHTML =
        `<option value="">Select learning item</option>`;

    availableLearningItems
        .filter((item) => !assignedIds.has(Number(item.itemId)))
        .forEach((item) => {
            const option = document.createElement("option");

            option.value = item.itemId;
            option.textContent = getLearningItemDisplayText(item);

            select.appendChild(option);
        });

    setElementDisabled("availableLearningItemSelect", false);
    setElementDisabled("addLearningItemButton", false);
}


function populateAvailableQuizQuestionsSelect() {
    const select =
        document.getElementById("availableQuizQuestionSelect");

    const assignedIds =
        new Set(getAssignedQuizQuestionIds());

    select.innerHTML =
        `<option value="">Select quiz question</option>`;

    availableQuizQuestions
        .filter((question) => !assignedIds.has(Number(question.questionId)))
        .forEach((question) => {
            const option = document.createElement("option");

            option.value = question.questionId;
            option.textContent = question.questionText;

            select.appendChild(option);
        });

    setElementDisabled("availableQuizQuestionSelect", false);
    setElementDisabled("addQuizQuestionButton", false);
}


function addSelectedLearningItem() {
    const select =
        document.getElementById("availableLearningItemSelect");

    const selectedItemId =
        Number(select.value);

    if (!selectedItemId) {
        return;
    }

    const selectedItem =
        availableLearningItems.find((item) =>
            Number(item.itemId) === selectedItemId
        );

    if (!selectedItem) {
        return;
    }

    assignedLearningItems.push({
        itemId: selectedItem.itemId,
        sourceText: selectedItem.sourceText,
        englishTranslation: selectedItem.englishTranslation,
        itemType: selectedItem.itemType
    });

    select.value = "";

    renderAssignedLearningItems();
    populateAvailableLearningItemsSelect();
    leaveWithoutSavingConfirmed = false;
}


function addSelectedQuizQuestion() {
    const select =
        document.getElementById("availableQuizQuestionSelect");

    const selectedQuestionId =
        Number(select.value);

    if (!selectedQuestionId) {
        return;
    }

    const selectedQuestion =
        availableQuizQuestions.find((question) =>
            Number(question.questionId) === selectedQuestionId
        );

    if (!selectedQuestion) {
        return;
    }

    assignedQuizQuestions.push({
        questionId: selectedQuestion.questionId,
        questionText: selectedQuestion.questionText,
        categoryName: selectedQuestion.categoryName,
        isActive: selectedQuestion.isActive
    });

    select.value = "";

    renderAssignedQuizQuestions();
    populateAvailableQuizQuestionsSelect();
    leaveWithoutSavingConfirmed = false;
}


function moveLearningItemUp(index) {
    if (index <= 0) {
        return;
    }

    const temporaryItem =
        assignedLearningItems[index - 1];

    assignedLearningItems[index - 1] =
        assignedLearningItems[index];

    assignedLearningItems[index] =
        temporaryItem;

    renderAssignedLearningItems();
    leaveWithoutSavingConfirmed = false;
}


function moveLearningItemDown(index) {
    if (index >= assignedLearningItems.length - 1) {
        return;
    }

    const temporaryItem =
        assignedLearningItems[index + 1];

    assignedLearningItems[index + 1] =
        assignedLearningItems[index];

    assignedLearningItems[index] =
        temporaryItem;

    renderAssignedLearningItems();
    leaveWithoutSavingConfirmed = false;
}


function removeLearningItem(index) {
    assignedLearningItems.splice(index, 1);

    renderAssignedLearningItems();
    populateAvailableLearningItemsSelect();
    leaveWithoutSavingConfirmed = false;
}


function moveQuizQuestionUp(index) {
    if (index <= 0) {
        return;
    }

    const temporaryQuestion =
        assignedQuizQuestions[index - 1];

    assignedQuizQuestions[index - 1] =
        assignedQuizQuestions[index];

    assignedQuizQuestions[index] =
        temporaryQuestion;

    renderAssignedQuizQuestions();
    leaveWithoutSavingConfirmed = false;
}


function moveQuizQuestionDown(index) {
    if (index >= assignedQuizQuestions.length - 1) {
        return;
    }

    const temporaryQuestion =
        assignedQuizQuestions[index + 1];

    assignedQuizQuestions[index + 1] =
        assignedQuizQuestions[index];

    assignedQuizQuestions[index] =
        temporaryQuestion;

    renderAssignedQuizQuestions();
    leaveWithoutSavingConfirmed = false;
}


function removeQuizQuestion(index) {
    assignedQuizQuestions.splice(index, 1);

    renderAssignedQuizQuestions();
    populateAvailableQuizQuestionsSelect();
    leaveWithoutSavingConfirmed = false;
}


function renderAssignedLearningItems() {
    const tableBody =
        document.getElementById(ASSIGNED_LEARNING_ITEMS_TABLE_BODY_ID);

    if (assignedLearningItems.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    No learning items assigned.
                </td>
            </tr>
        `;

        return;
    }

    tableBody.innerHTML =
        assignedLearningItems.map((item, index) => `
            <tr>
                <td>${escapeHtml(index + 1)}</td>

                <td>${escapeHtml(item.itemType || "")}</td>

                <td>${escapeHtml(item.sourceText || "")}</td>

                <td>${escapeHtml(item.englishTranslation || "")}</td>

                <td>
                    <div class="lesson-composition-action-group">
                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Move up"
                            aria-label="Move learning item up"
                            ${index === 0 ? "disabled" : ""}
                            data-learning-item-action="up"
                            data-index="${index}">
                            ↑
                        </button>

                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Move down"
                            aria-label="Move learning item down"
                            ${index === assignedLearningItems.length - 1 ? "disabled" : ""}
                            data-learning-item-action="down"
                            data-index="${index}">
                            ↓
                        </button>

                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Remove"
                            aria-label="Remove learning item"
                            data-learning-item-action="remove"
                            data-index="${index}">
                            🗑
                        </button>
                    </div>
                </td>
            </tr>
        `).join("");
}


function renderAssignedQuizQuestions() {
    const tableBody =
        document.getElementById(ASSIGNED_QUIZ_QUESTIONS_TABLE_BODY_ID);

    if (assignedQuizQuestions.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    No quiz questions assigned.
                </td>
            </tr>
        `;

        return;
    }

    tableBody.innerHTML =
        assignedQuizQuestions.map((question, index) => `
            <tr>
                <td>${escapeHtml(index + 1)}</td>

                <td>
                    ${question.isActive ? "Yes" : "No"}
                </td>

                <td>
                    ${escapeHtml(question.categoryName || "")}
                </td>

                <td>
                    ${escapeHtml(question.questionText || "")}
                </td>

                <td>
                    <div class="lesson-composition-action-group">
                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Move up"
                            aria-label="Move quiz question up"
                            ${index === 0 ? "disabled" : ""}
                            data-quiz-question-action="up"
                            data-index="${index}">
                            ↑
                        </button>

                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Move down"
                            aria-label="Move quiz question down"
                            ${index === assignedQuizQuestions.length - 1 ? "disabled" : ""}
                            data-quiz-question-action="down"
                            data-index="${index}">
                            ↓
                        </button>

                        <button
                            class="shared-icon-button"
                            type="button"
                            title="Remove"
                            aria-label="Remove quiz question"
                            data-quiz-question-action="remove"
                            data-index="${index}">
                            🗑
                        </button>
                    </div>
                </td>
            </tr>
        `).join("");
}


function handleLearningItemTableClick(event) {
    const button =
        event.target.closest("[data-learning-item-action]");

    if (!button) {
        return;
    }

    const index =
        Number(button.dataset.index);

    const action =
        button.dataset.learningItemAction;

    if (action === "up") {
        moveLearningItemUp(index);
        return;
    }

    if (action === "down") {
        moveLearningItemDown(index);
        return;
    }

    if (action === "remove") {
        removeLearningItem(index);
    }
}


function handleQuizQuestionTableClick(event) {
    const button =
        event.target.closest("[data-quiz-question-action]");

    if (!button) {
        return;
    }

    const index =
        Number(button.dataset.index);

    const action =
        button.dataset.quizQuestionAction;

    if (action === "up") {
        moveQuizQuestionUp(index);
        return;
    }

    if (action === "down") {
        moveQuizQuestionDown(index);
        return;
    }

    if (action === "remove") {
        removeQuizQuestion(index);
    }
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
            "Failed to load lesson form options."
        );
    }

    populateLessonFormOptions(
        formOptionsData.form_options
    );
}


async function loadAvailableCompositionData() {
    const learningItemsData =
        await getJson(
            LLA_API_ENDPOINTS.admin.learningItems.list
        );

    const quizQuestionsData =
        await getJson(
            LLA_API_ENDPOINTS.admin.quizQuestions.list
        );

    availableLearningItems =
        learningItemsData.learningItems || [];

    availableQuizQuestions =
        quizQuestionsData.quizQuestions || [];

    populateAvailableLearningItemsSelect();
    populateAvailableQuizQuestionsSelect();
}


async function saveLessonLearningItemAssignments(lessonId) {
    const payload = {
        learning_items:
            assignedLearningItems.map((item) => ({
                item_id: item.itemId
            }))
    };

    const data =
        await putJson(
            LLA_API_ENDPOINTS.admin.lessons.learningItems(lessonId),
            payload
        );

    if (!data.success) {
        throw new Error(
            data.error || "Failed to save lesson learning items."
        );
    }
}


async function saveLessonQuizQuestionAssignments(lessonId) {
    const payload = {
        quiz_questions:
            assignedQuizQuestions.map((question) => ({
                question_id: question.questionId
            }))
    };

    const data =
        await putJson(
            LLA_API_ENDPOINTS.admin.lessons.quizQuestions(lessonId),
            payload
        );

    if (!data.success) {
        throw new Error(
            data.error || "Failed to save lesson quiz questions."
        );
    }
}

function resetLeaveWithoutSavingConfirmation() {
    leaveWithoutSavingConfirmed =
        false;
}

function hasUnsavedChanges() {
    const formData =
        readLessonFormData();

    return Boolean(
        formData.title ||
        formData.description ||
        formData.categoryId ||
        formData.lessonTypeId ||
        formData.embodimentTypeId ||
        formData.interactionStyleId ||
        !formData.isActive ||
        assignedLearningItems.length > 0 ||
        assignedQuizQuestions.length > 0
    );
}

async function createLesson(event) {
    event.preventDefault();

    hideMessage(LESSON_CREATE_MESSAGE_ID);

    setElementDisabled(CREATE_LESSON_BUTTON_ID, true);
    setButtonText(CREATE_LESSON_BUTTON_ID, "Creating...");

    try {
        const formData =
            readLessonFormData();

        const data =
            await postJson(
                LLA_API_ENDPOINTS.admin.lessons.create,
                buildCreateLessonPayload(formData)
            );

        if (!data.success) {
            throw new Error(
                data.error || "Failed to create lesson."
            );
        }

        const lessonId =
            data.lesson?.lessonId;

        if (!lessonId) {
            throw new Error(
                "Created lesson ID is missing."
            );
        }

        await saveLessonLearningItemAssignments(lessonId);
        await saveLessonQuizQuestionAssignments(lessonId);

        clearLessonForm();

        showSuccessMessage(
            LESSON_CREATE_MESSAGE_ID,
            "Lesson created successfully."
        );

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LESSON_CREATE_MESSAGE_ID,
            error.message || "Failed to create lesson."
        );

    } finally {
        setElementDisabled(CREATE_LESSON_BUTTON_ID, false);
        setButtonText(CREATE_LESSON_BUTTON_ID, "Create lesson");
    }
}


async function initializeLessonCreatePage() {
    try {
        await loadLessonFormOptions();
        await loadAvailableCompositionData();

        renderAssignedLearningItems();
        renderAssignedQuizQuestions();

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LESSON_CREATE_MESSAGE_ID,
            error.message || "Failed to load lesson create page."
        );
    }
}

document
    .getElementById("lessonCreateForm")
    .addEventListener("input", resetLeaveWithoutSavingConfirmation);

document
    .getElementById("backToLessonsButton")
    .addEventListener("click", navigateBackToLessons);

document
    .getElementById("learningItemsTabButton")
    .addEventListener("click", showLearningItemsTab);

document
    .getElementById("quizQuestionsTabButton")
    .addEventListener("click", showQuizQuestionsTab);

document
    .getElementById("lessonCreateForm")
    .addEventListener("submit", createLesson);

document
    .getElementById("addLearningItemButton")
    .addEventListener("click", addSelectedLearningItem);

document
    .getElementById("addQuizQuestionButton")
    .addEventListener("click", addSelectedQuizQuestion);

document
    .getElementById(ASSIGNED_LEARNING_ITEMS_TABLE_BODY_ID)
    .addEventListener("click", handleLearningItemTableClick);

document
    .getElementById(ASSIGNED_QUIZ_QUESTIONS_TABLE_BODY_ID)
    .addEventListener("click", handleQuizQuestionTableClick);

initializeLessonCreatePage();
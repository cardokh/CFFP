const LESSON_EDIT_MESSAGE_ID =
    "lessonEditMessage";

const SAVE_LESSON_BUTTON_ID =
    "saveLessonButton";

const DELETE_LESSON_BUTTON_ID =
    "deleteLessonButton";

const ASSIGNED_LEARNING_ITEMS_TABLE_BODY_ID =
    "assignedLearningItemsTableBody";

const ASSIGNED_QUIZ_QUESTIONS_TABLE_BODY_ID =
    "assignedQuizQuestionsTableBody";

let originalLessonFormData =
    null;

let originalLearningItemIds =
    [];

let originalQuizQuestionIds =
    [];

let assignedLearningItems =
    [];

let assignedQuizQuestions =
    [];

let availableLearningItems =
    [];

let availableQuizQuestions =
    [];

let leaveWithoutSavingConfirmed =
    false;


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function getLessonIdFromUrl() {
    const params =
        new URLSearchParams(window.location.search);

    return params.get("lessonId");
}


function navigateBackToLessons() {
    const hasChanges =
        hasAnyLessonEditChanged(
            readLessonFormData()
        );

    if (!hasChanges) {
        window.location.href =
            LLA_PATHS.desktop.protected.admin.lessons.list;

        return;
    }

    if (!leaveWithoutSavingConfirmed) {
        leaveWithoutSavingConfirmed =
            true;

        showInfoMessage(
            LESSON_EDIT_MESSAGE_ID,
            "Unsaved changes detected. Click Save to apply your changes or click Back again to leave without saving."
        );

        return;
    }

    window.location.href =
        LLA_PATHS.desktop.protected.admin.lessons.list;
}


function navigateToCreateLesson() {
    window.location.href =
        LLA_PATHS.desktop.protected.admin.lessons.create;
}


async function deleteLesson() {
    const lessonId =
        getLessonIdFromUrl();

    if (!lessonId) {
        showErrorMessage(
            LESSON_EDIT_MESSAGE_ID,
            "Lesson ID is missing."
        );

        return;
    }

    const confirmed =
        confirm("Are you sure you want to delete this lesson?");

    if (!confirmed) {
        return;
    }

    hideMessage(LESSON_EDIT_MESSAGE_ID);

    setElementDisabled(DELETE_LESSON_BUTTON_ID, true);
    setButtonText(DELETE_LESSON_BUTTON_ID, "Deleting...");

    try {
        const data =
            await deleteJson(
                LLA_API_ENDPOINTS.admin.lessons.byId(lessonId)
            );

        if (!data.success) {
            throw new Error(
                data.error || "Failed to delete lesson."
            );
        }

        window.location.href =
            LLA_PATHS.desktop.protected.admin.lessons.list;

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LESSON_EDIT_MESSAGE_ID,
            error.message || "Failed to delete lesson."
        );

        setElementDisabled(DELETE_LESSON_BUTTON_ID, false);
        setButtonText(DELETE_LESSON_BUTTON_ID, "Delete lesson");
    }
}


function showLearningItemsTab() {
    document
        .getElementById("learningItemsTabButton")
        .classList.add("active");

    document
        .getElementById("quizQuestionsTabButton")
        .classList.remove("active");

    document
        .getElementById("learningItemsTabPanel")
        .classList.remove("hidden");

    document
        .getElementById("quizQuestionsTabPanel")
        .classList.add("hidden");
}


function showQuizQuestionsTab() {
    document
        .getElementById("quizQuestionsTabButton")
        .classList.add("active");

    document
        .getElementById("learningItemsTabButton")
        .classList.remove("active");

    document
        .getElementById("quizQuestionsTabPanel")
        .classList.remove("hidden");

    document
        .getElementById("learningItemsTabPanel")
        .classList.add("hidden");
}


function populateSelect(selectId, items, defaultLabel) {
    const select =
        document.getElementById(selectId);

    select.innerHTML =
        `<option value="">${escapeHtml(defaultLabel)}</option>`;

    items.forEach((item) => {
        const option =
            document.createElement("option");

        option.value =
            item.id;

        option.textContent =
            item.name;

        select.appendChild(option);
    });

    setElementDisabled(selectId, false);
}


function populateLessonFormOptions(formOptions) {
    populateSelect(
        "categoryId",
        formOptions.lesson_categories,
        "Select category"
    );

    populateSelect(
        "lessonTypeId",
        formOptions.lesson_types,
        "Select lesson type"
    );

    populateSelect(
        "embodimentTypeId",
        formOptions.embodiment_types,
        "Select embodiment"
    );

    populateSelect(
        "interactionStyleId",
        formOptions.interaction_styles,
        "Select interaction style"
    );
}


function populateLessonForm(lesson) {
    document.getElementById("lessonId").value =
        lesson.lessonId;

    document.getElementById("title").value =
        lesson.title || "";

    document.getElementById("description").value =
        lesson.description || "";

    document.getElementById("categoryId").value =
        lesson.categoryId || "";

    document.getElementById("lessonTypeId").value =
        lesson.lessonTypeId || "";

    document.getElementById("embodimentTypeId").value =
        lesson.embodimentTypeId || "";

    document.getElementById("interactionStyleId").value =
        lesson.interactionStyleId || "";

    document.getElementById("isActive").checked =
        Boolean(lesson.isActive);
}


function readLessonFormData() {
    return {
        title:
            document.getElementById("title").value.trim(),

        description:
            document.getElementById("description").value.trim(),

        categoryId:
            Number(document.getElementById("categoryId").value),

        lessonTypeId:
            Number(document.getElementById("lessonTypeId").value),

        embodimentTypeId:
            Number(document.getElementById("embodimentTypeId").value),

        interactionStyleId:
            Number(document.getElementById("interactionStyleId").value),

        isActive:
            document.getElementById("isActive").checked
    };
}


function buildLessonMetadataPayload(formData) {
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


function normalizeLessonFormDataForComparison(formData) {
    return {
        title: formData.title || "",
        description: formData.description || "",
        categoryId: Number(formData.categoryId),
        lessonTypeId: Number(formData.lessonTypeId),
        embodimentTypeId: Number(formData.embodimentTypeId),
        interactionStyleId: Number(formData.interactionStyleId),
        isActive: Boolean(formData.isActive)
    };
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


function areNumberArraysEqual(left, right) {
    return JSON.stringify(left) === JSON.stringify(right);
}


function hasLessonFormChanged(currentFormData) {
    if (!originalLessonFormData) {
        return true;
    }

    return JSON.stringify(
        normalizeLessonFormDataForComparison(currentFormData)
    ) !== JSON.stringify(
        normalizeLessonFormDataForComparison(originalLessonFormData)
    );
}


function hasLearningItemAssignmentsChanged() {
    return !areNumberArraysEqual(
        getAssignedLearningItemIds(),
        originalLearningItemIds
    );
}


function hasQuizQuestionAssignmentsChanged() {
    return !areNumberArraysEqual(
        getAssignedQuizQuestionIds(),
        originalQuizQuestionIds
    );
}


function hasAnyLessonEditChanged(currentFormData) {
    return (
        hasLessonFormChanged(currentFormData) ||
        hasLearningItemAssignmentsChanged() ||
        hasQuizQuestionAssignmentsChanged()
    );
}


function storeOriginalState() {
    originalLessonFormData =
        readLessonFormData();

    originalLearningItemIds =
        getAssignedLearningItemIds();

    originalQuizQuestionIds =
        getAssignedQuizQuestionIds();
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
            const option =
                document.createElement("option");

            option.value =
                item.itemId;

            option.textContent =
                getLearningItemDisplayText(item);

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
            const option =
                document.createElement("option");

            option.value =
                question.questionId;

            option.textContent =
                question.questionText;

            select.appendChild(option);
        });

    setElementDisabled("availableQuizQuestionSelect", false);
    setElementDisabled("addQuizQuestionButton", false);
}


function resetLeaveWithoutSavingConfirmation() {
    leaveWithoutSavingConfirmed =
        false;
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
    resetLeaveWithoutSavingConfirmation();
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
    resetLeaveWithoutSavingConfirmation();
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
    resetLeaveWithoutSavingConfirmation();
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
    resetLeaveWithoutSavingConfirmation();
}


function removeLearningItem(index) {
    assignedLearningItems.splice(index, 1);

    renderAssignedLearningItems();
    populateAvailableLearningItemsSelect();
    resetLeaveWithoutSavingConfirmation();
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
    resetLeaveWithoutSavingConfirmation();
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
    resetLeaveWithoutSavingConfirmation();
}


function removeQuizQuestion(index) {
    assignedQuizQuestions.splice(index, 1);

    renderAssignedQuizQuestions();
    populateAvailableQuizQuestionsSelect();
    resetLeaveWithoutSavingConfirmation();
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


async function loadLessonForEdit() {
    const lessonId =
        getLessonIdFromUrl();

    if (!lessonId) {
        showErrorMessage(
            LESSON_EDIT_MESSAGE_ID,
            "Lesson ID is missing."
        );

        return;
    }

    try {
        const lessonData =
            await getJson(
                LLA_API_ENDPOINTS.admin.lessons.byId(lessonId)
            );

        const formOptionsData =
            await getJson(
                LLA_API_ENDPOINTS.admin.referenceData.lessonFormOptions
            );

        const learningItemsData =
            await getJson(
                LLA_API_ENDPOINTS.admin.lessons.learningItems(lessonId)
            );

        const quizQuestionsData =
            await getJson(
                LLA_API_ENDPOINTS.admin.lessons.quizQuestions(lessonId)
            );

        const allLearningItemsData =
            await getJson(
                LLA_API_ENDPOINTS.admin.learningItems.list
            );

        const allQuizQuestionsData =
            await getJson(
                LLA_API_ENDPOINTS.admin.quizQuestions.list
            );

        if (!lessonData.success || !lessonData.lesson) {
            showErrorMessage(
                LESSON_EDIT_MESSAGE_ID,
                lessonData.error || "Lesson not found."
            );

            return;
        }

        if (!formOptionsData.success || !formOptionsData.form_options) {
            showErrorMessage(
                LESSON_EDIT_MESSAGE_ID,
                "Failed to load lesson form options."
            );

            return;
        }

        populateLessonFormOptions(
            formOptionsData.form_options
        );

        populateLessonForm(
            lessonData.lesson
        );

        assignedLearningItems =
            learningItemsData.lessonLearningItems || [];

        assignedQuizQuestions =
            quizQuestionsData.lessonQuizQuestions || [];

        availableLearningItems =
            allLearningItemsData.learningItems || [];

        availableQuizQuestions =
            allQuizQuestionsData.quizQuestions || [];

        populateAvailableLearningItemsSelect();
        populateAvailableQuizQuestionsSelect();

        renderAssignedLearningItems();
        renderAssignedQuizQuestions();

        storeOriginalState();

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LESSON_EDIT_MESSAGE_ID,
            error.message || "Failed to load lesson."
        );
    }
}


async function saveLessonMetadata(lessonId, formData) {
    const data =
        await putJson(
            LLA_API_ENDPOINTS.admin.lessons.byId(lessonId),
            buildLessonMetadataPayload(formData)
        );

    if (!data.success) {
        throw new Error(
            data.error || "Failed to update lesson."
        );
    }
}


async function saveLessonLearningItems(lessonId) {
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
            data.error || "Failed to update lesson learning items."
        );
    }

    assignedLearningItems =
        data.lessonLearningItems || assignedLearningItems;
}


async function saveLessonQuizQuestions(lessonId) {
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
            data.error || "Failed to update lesson quiz questions."
        );
    }

    assignedQuizQuestions =
        data.lessonQuizQuestions || assignedQuizQuestions;
}


async function saveLesson(event) {
    event.preventDefault();

    const lessonId =
        getLessonIdFromUrl();

    if (!lessonId) {
        showErrorMessage(
            LESSON_EDIT_MESSAGE_ID,
            "Lesson ID is missing."
        );

        return;
    }

    hideMessage(LESSON_EDIT_MESSAGE_ID);

    const formData =
        readLessonFormData();

    const lessonFormChanged =
        hasLessonFormChanged(formData);

    const learningItemsChanged =
        hasLearningItemAssignmentsChanged();

    const quizQuestionsChanged =
        hasQuizQuestionAssignmentsChanged();

    if (
        !lessonFormChanged &&
        !learningItemsChanged &&
        !quizQuestionsChanged
    ) {
        showInfoMessage(
            LESSON_EDIT_MESSAGE_ID,
            "No changes detected."
        );

        return;
    }

    setElementDisabled(SAVE_LESSON_BUTTON_ID, true);
    setElementDisabled(DELETE_LESSON_BUTTON_ID, true);
    setButtonText(SAVE_LESSON_BUTTON_ID, "Saving...");

    try {
        if (lessonFormChanged) {
            await saveLessonMetadata(
                lessonId,
                formData
            );
        }

        if (learningItemsChanged) {
            await saveLessonLearningItems(
                lessonId
            );
        }

        if (quizQuestionsChanged) {
            await saveLessonQuizQuestions(
                lessonId
            );
        }

        renderAssignedLearningItems();
        renderAssignedQuizQuestions();

        populateAvailableLearningItemsSelect();
        populateAvailableQuizQuestionsSelect();

        storeOriginalState();

        leaveWithoutSavingConfirmed =
            false;

        showSuccessMessage(
            LESSON_EDIT_MESSAGE_ID,
            "Lesson updated successfully."
        );

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LESSON_EDIT_MESSAGE_ID,
            error.message || "Failed to update lesson."
        );

    } finally {
        setElementDisabled(SAVE_LESSON_BUTTON_ID, false);
        setElementDisabled(DELETE_LESSON_BUTTON_ID, false);
        setButtonText(SAVE_LESSON_BUTTON_ID, "Save");
    }
}


document
    .getElementById("lessonEditForm")
    .addEventListener("input", resetLeaveWithoutSavingConfirmation);

document
    .getElementById("backToLessonsButton")
    .addEventListener("click", navigateBackToLessons);

document
    .getElementById("addLessonButton")
    .addEventListener("click", navigateToCreateLesson);

document
    .getElementById("deleteLessonButton")
    .addEventListener("click", deleteLesson);

document
    .getElementById("learningItemsTabButton")
    .addEventListener("click", showLearningItemsTab);

document
    .getElementById("quizQuestionsTabButton")
    .addEventListener("click", showQuizQuestionsTab);

document
    .getElementById("lessonEditForm")
    .addEventListener("submit", saveLesson);

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

loadLessonForEdit();
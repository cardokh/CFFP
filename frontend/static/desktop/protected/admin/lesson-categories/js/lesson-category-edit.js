const LESSON_CATEGORY_EDIT_MESSAGE_ID =
    "lessonCategoryEditMessage";

const SAVE_LESSON_CATEGORY_BUTTON_ID =
    "saveLessonCategoryButton";

const DELETE_LESSON_CATEGORY_BUTTON_ID =
    "deleteLessonCategoryButton";

const SAVE_LESSON_CATEGORY_BUTTON_DEFAULT_TEXT =
    "Save";

const SAVE_LESSON_CATEGORY_BUTTON_LOADING_TEXT =
    "Saving...";

const LESSON_CATEGORY_ID_MISSING_MESSAGE =
    "Lesson category ID is missing.";

const LESSON_CATEGORY_NOT_FOUND_MESSAGE =
    "Lesson category not found.";

const FAILED_TO_LOAD_LESSON_CATEGORY_MESSAGE =
    "Failed to load lesson category.";

const FAILED_TO_UPDATE_LESSON_CATEGORY_MESSAGE =
    "Failed to update lesson category.";

const FAILED_TO_DELETE_LESSON_CATEGORY_MESSAGE =
    "Failed to delete lesson category.";

const LESSON_CATEGORY_UPDATED_SUCCESS_MESSAGE =
    "Lesson category updated successfully.";

const NO_CHANGES_DETECTED_MESSAGE =
    "No changes detected.";

const ADMIN_UPDATED_BY =
    "admin";

let originalLessonCategoryFormData =
    null;

let leaveWithoutSavingConfirmed =
    false;

function getLessonCategoryIdFromUrl() {
    const params =
        new URLSearchParams(window.location.search);

    return params.get("categoryId");
}

function navigateBackToLessonCategories() {
    const hasChanges =
        hasLessonCategoryFormChanged(
            readLessonCategoryFormData()
        );

    if (!hasChanges) {
        window.location.href =
            LLA_PATHS.desktop.protected.admin.lessonCategories.list;

        return;
    }

    if (!leaveWithoutSavingConfirmed) {
        leaveWithoutSavingConfirmed =
            true;

        showInfoMessage(
            LESSON_CATEGORY_EDIT_MESSAGE_ID,
            "Unsaved changes detected. Click Save to apply your changes or click Back again to leave without saving."
        );

        return;
    }

    window.location.href =
        LLA_PATHS.desktop.protected.admin.lessonCategories.list;
}

function resetLeaveWithoutSavingConfirmation() {
    leaveWithoutSavingConfirmed =
        false;
}

function populateLessonCategoryForm(lessonCategory) {
    document.getElementById("categoryId").value =
        lessonCategory.categoryId;

    document.getElementById("name").value =
        lessonCategory.name || "";

    document.getElementById("description").value =
        lessonCategory.description || "";

    document.getElementById("isActive").checked =
        Boolean(lessonCategory.isActive);
}

function readLessonCategoryFormData() {
    return {
        name:
            document.getElementById("name").value.trim(),

        description:
            document.getElementById("description").value.trim(),

        isActive:
            document.getElementById("isActive").checked,

        updatedBy:
            ADMIN_UPDATED_BY
    };
}

function normalizeLessonCategoryFormDataForComparison(formData) {
    return {
        name:
            formData.name || "",

        description:
            formData.description || "",

        isActive:
            Boolean(formData.isActive)
    };
}

function hasLessonCategoryFormChanged(currentFormData) {
    if (!originalLessonCategoryFormData) {
        return false;
    }

    return JSON.stringify(
        normalizeLessonCategoryFormDataForComparison(currentFormData)
    ) !== JSON.stringify(
        normalizeLessonCategoryFormDataForComparison(
            originalLessonCategoryFormData
        )
    );
}

function storeOriginalLessonCategoryFormData() {
    originalLessonCategoryFormData =
        readLessonCategoryFormData();
}

async function loadLessonCategoryForEdit() {
    const categoryId =
        getLessonCategoryIdFromUrl();

    if (!categoryId) {
        showErrorMessage(
            LESSON_CATEGORY_EDIT_MESSAGE_ID,
            LESSON_CATEGORY_ID_MISSING_MESSAGE
        );

        return;
    }

    try {
        const data =
            await getJson(
                LLA_API_ENDPOINTS.admin.lessonCategories.byId(categoryId)
            );

        if (!data.success || !data.lessonCategory) {
            showErrorMessage(
                LESSON_CATEGORY_EDIT_MESSAGE_ID,
                data.error || LESSON_CATEGORY_NOT_FOUND_MESSAGE
            );

            return;
        }

        populateLessonCategoryForm(
            data.lessonCategory
        );

        storeOriginalLessonCategoryFormData();

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LESSON_CATEGORY_EDIT_MESSAGE_ID,
            error.message || FAILED_TO_LOAD_LESSON_CATEGORY_MESSAGE
        );
    }
}

async function deleteLessonCategory() {
    const categoryId =
        getLessonCategoryIdFromUrl();

    if (!categoryId) {
        showErrorMessage(
            LESSON_CATEGORY_EDIT_MESSAGE_ID,
            LESSON_CATEGORY_ID_MISSING_MESSAGE
        );

        return;
    }

    const confirmed =
        confirm(
            "Are you sure you want to delete this lesson category?"
        );

    if (!confirmed) {
        return;
    }

    hideMessage(
        LESSON_CATEGORY_EDIT_MESSAGE_ID
    );

    setElementDisabled(
        DELETE_LESSON_CATEGORY_BUTTON_ID,
        true
    );

    setElementDisabled(
        SAVE_LESSON_CATEGORY_BUTTON_ID,
        true
    );

    setButtonText(
        DELETE_LESSON_CATEGORY_BUTTON_ID,
        "Deleting..."
    );

    try {
        const data =
            await deleteJson(
                LLA_API_ENDPOINTS.admin.lessonCategories.byId(categoryId)
            );

        if (!data.success) {
            throw new Error(
                data.error ||
                FAILED_TO_DELETE_LESSON_CATEGORY_MESSAGE
            );
        }

        window.location.href =
            LLA_PATHS.desktop.protected.admin.lessonCategories.list;

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LESSON_CATEGORY_EDIT_MESSAGE_ID,
            error.message ||
            FAILED_TO_DELETE_LESSON_CATEGORY_MESSAGE
        );

        setElementDisabled(
            DELETE_LESSON_CATEGORY_BUTTON_ID,
            false
        );

        setElementDisabled(
            SAVE_LESSON_CATEGORY_BUTTON_ID,
            false
        );

        setButtonText(
            DELETE_LESSON_CATEGORY_BUTTON_ID,
            "Delete"
        );
    }
}

async function saveLessonCategory(event) {
    event.preventDefault();

    const categoryId =
        getLessonCategoryIdFromUrl();

    if (!categoryId) {
        showErrorMessage(
            LESSON_CATEGORY_EDIT_MESSAGE_ID,
            LESSON_CATEGORY_ID_MISSING_MESSAGE
        );

        return;
    }

    hideMessage(
        LESSON_CATEGORY_EDIT_MESSAGE_ID
    );

    const payload =
        readLessonCategoryFormData();

    if (!hasLessonCategoryFormChanged(payload)) {
        showInfoMessage(
            LESSON_CATEGORY_EDIT_MESSAGE_ID,
            NO_CHANGES_DETECTED_MESSAGE
        );

        return;
    }

    setElementDisabled(
        SAVE_LESSON_CATEGORY_BUTTON_ID,
        true
    );

    setElementDisabled(
        DELETE_LESSON_CATEGORY_BUTTON_ID,
        true
    );

    setButtonText(
        SAVE_LESSON_CATEGORY_BUTTON_ID,
        SAVE_LESSON_CATEGORY_BUTTON_LOADING_TEXT
    );

    try {
        const data =
            await putJson(
                LLA_API_ENDPOINTS.admin.lessonCategories.byId(categoryId),
                payload
            );

        if (!data.success) {
            throw new Error(
                data.error ||
                FAILED_TO_UPDATE_LESSON_CATEGORY_MESSAGE
            );
        }

        originalLessonCategoryFormData =
            payload;

        leaveWithoutSavingConfirmed =
            false;

        showSuccessMessage(
            LESSON_CATEGORY_EDIT_MESSAGE_ID,
            LESSON_CATEGORY_UPDATED_SUCCESS_MESSAGE
        );

    } catch (error) {
        console.error(error);

        showErrorMessage(
            LESSON_CATEGORY_EDIT_MESSAGE_ID,
            error.message ||
            FAILED_TO_UPDATE_LESSON_CATEGORY_MESSAGE
        );

    } finally {
        setElementDisabled(
            SAVE_LESSON_CATEGORY_BUTTON_ID,
            false
        );

        setElementDisabled(
            DELETE_LESSON_CATEGORY_BUTTON_ID,
            false
        );

        setButtonText(
            SAVE_LESSON_CATEGORY_BUTTON_ID,
            SAVE_LESSON_CATEGORY_BUTTON_DEFAULT_TEXT
        );
    }
}

document
    .getElementById("backToLessonCategoriesButton")
    .addEventListener(
        "click",
        navigateBackToLessonCategories
    );

document
    .getElementById(DELETE_LESSON_CATEGORY_BUTTON_ID)
    .addEventListener(
        "click",
        deleteLessonCategory
    );

document
    .getElementById("lessonCategoryEditForm")
    .addEventListener(
        "input",
        resetLeaveWithoutSavingConfirmation
    );

document
    .getElementById("lessonCategoryEditForm")
    .addEventListener(
        "submit",
        saveLessonCategory
    );

loadLessonCategoryForEdit();